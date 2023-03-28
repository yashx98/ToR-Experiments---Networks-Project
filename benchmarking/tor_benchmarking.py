from stem import Signal, CircStatus
from stem.control import Controller, EventType
import time
from io import StringIO
import requests
import random

SOCKS_PORT = 9150
CONTROL_PORT = 9151
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit
# EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'
EXIT_FINGERPRINT = 'EF25C1F9BEF8C4A3F2859493C7C8C5148725B4E7'

def renewConnection():
    with Controller.from_port(port = 9051) as controller:
        controller.authenticate(password="")
        controller.signal(Signal.NEWNYM)

def circuitBuildTime():
  with Controller.from_port(port = 9051) as controller:
      controller.authenticate()

      # Build a new circuit and note the start time
      start_time = time.time()
      circuit_id = controller.new_circuit()

      # Wait for the circuit to become fully established
      while True:
          circuit = controller.get_circuit(circuit_id)
          if circuit.status == CircStatus.BUILT:
              end_time = time.time()
              break
          time.sleep(0.0001)

      # Calculate the circuit build time
      circuit_build_time = end_time - start_time
      print("Circuit build time: %.3f seconds" % circuit_build_time)

def get(url):
  """
  Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
  """
  session = requests.session()
  session.proxies = {
    'http': 'socks5://127.0.0.1:%s' % SOCKS_PORT,
    'https': 'socks5://127.0.0.1:%s' % SOCKS_PORT,
  }
  try: 
    response = session.get(url)
    return response
  except:
    print("Could not connect")

def connect(controller, path, url):
  """ Build a custom 2 hop circuit using the path fingerprint
  and the hard coded exit node """

  circuit_id = controller.new_circuit(path, await_build = True)

  def attach_stream(stream):
    if stream.status == 'NEW':
      controller.attach_stream(stream.id, circuit_id)

  controller.add_event_listener(attach_stream, EventType.STREAM)

  try:
    controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
    check_page = get(url)
    return check_page
  finally:
    # Stop listening for attach stream events and stop controlling streams
    controller.remove_event_listener(attach_stream)
    controller.reset_conf('__LeaveStreamsUnattached')

def twoHopTry():
  with Controller.from_port(port=CONTROL_PORT) as controller:
    controller.authenticate()

    relay_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses()]

    fingerprint = random.choice(relay_fingerprints)
    try:
      url = "http://www.torproject.org"
      response = connect(controller, [fingerprint, EXIT_FINGERPRINT], url)
      if response.status_code == 200:
          print("Connection to %s successful using node %s" % (url, fingerprint))
    except Exception as exc:
        print('%s => %s' % (fingerprint, exc))

def listCircuits():
  with Controller.from_port(port = 9051) as controller:
    controller.authenticate()

    for circ in sorted(controller.get_circuits()):
      if circ.status != CircStatus.BUILT:
        continue

      print("")
      print("Circuit %s (%s)" % (circ.id, circ.purpose))

      for i, entry in enumerate(circ.path):
        div = '+' if (i == len(circ.path) - 1) else '|'
        fingerprint, nickname = entry

        desc = controller.get_network_status(fingerprint, None)
        address = desc.address if desc else 'unknown'

        print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))

# listCircuits()

# twoHopTry()
# renewConnection()
