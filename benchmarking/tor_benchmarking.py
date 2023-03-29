from stem import Signal, CircStatus
from stem.control import Controller, EventType
import time
from io import StringIO
import requests
import random
import statistics

SOCKS_PORT = 9150
CONTROL_PORT = 9151
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit
# EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'
EXIT_FINGERPRINT = 'EF25C1F9BEF8C4A3F2859493C7C8C5148725B4E7'
NUM_CIRCUITS_SETUP = 100

def renewConnection():
    with Controller.from_port(port = CONTROL_PORT) as controller:
        controller.authenticate(password="")
        controller.signal(Signal.NEWNYM)

def circuitBuildTime():
  with Controller.from_port(port = CONTROL_PORT) as controller:
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
      return circuit_build_time

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
  with Controller.from_port(port = CONTROL_PORT) as controller:
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

def calCircuitSetupTimes():
  listCircuits()
  cir_build_times = []
  num_tries = 0
  i = 0
  while i < NUM_CIRCUITS_SETUP:
    num_tries += 1
    try:
      cir_build_time = circuitBuildTime()
    except:
       continue
    i += 1
    print(cir_build_time)
    cir_build_times.append(cir_build_time)
  mean_time = statistics.mean(cir_build_times)
  mean_time = statistics.mean(cir_build_times)
  std_dev_time = statistics.stdev(cir_build_times)
  print('Num values %s' % len(cir_build_times))
  print('Num tries %s' % num_tries)
  circuit_build_success_rate = (NUM_CIRCUITS_SETUP * 100.0) / num_tries
  print('Circuit build success rate %s' % circuit_build_success_rate)
  print('Mean Circuit Build Time: %s ms' % mean_time)
  print('Median Circuit Build Time: %s ms' % statistics.median(cir_build_times))
  print('Std dev Circuit Build Time: %s ms' % std_dev_time)
  coef_var = 0
  if mean_time != 0:
    coef_var = std_dev_time * 100 / mean_time
  print('Coefficient of variation Circuit Build Time: %s ms' % coef_var)

calCircuitSetupTimes()
# listCircuits()

# twoHopTry()
# renewConnection()
