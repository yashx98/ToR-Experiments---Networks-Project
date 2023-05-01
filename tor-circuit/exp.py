from stem import Signal, CircStatus
import stem.descriptor.remote
import stem.process
from stem.control import Controller, EventType
from stem.util import str_tools
from stem.descriptor.remote import DescriptorDownloader
from stem import Flag
import time
from io import StringIO
import requests
import random
import statistics
import subprocess
import os
import signal
import time

SOCKS_PORT = 9200
CONTROL_PORT = 9201
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit
# EXIT_FINGERPRINT = '379FB450010D17078B3766C2273303C358C3A442'
EXIT_FINGERPRINT = 'EF25C1F9BEF8C4A3F2859493C7C8C5148725B4E7'
NUM_CIRCUITS_SETUP = 100
entry_node = "Onyx"
# middle_node = "THELODGE2,marina"
middle_node = "TorRelayPoland,FatTubes,krustykrab"
exit_node = "d2d4"


def listCircuits():
  with Controller.from_port(port = CONTROL_PORT) as controller:
    controller.authenticate()

    for circ in sorted(controller.get_circuits()):
      if circ.status != CircStatus.BUILT:
        continue

      print("")
      print("Circuit %s (%s)" % (circ.id, circ.purpose))
      # for hop in circ.path:
        # get node information
        # node = stem.descriptor.remote.get_server_descriptors(hop[0])
        # for n in node:
        #   print(n.as_info)
        # print(node)
        # node_address = node.address
        # node_country = node.exit_policy.country
        # node_as = node.as_info

        # print node information
        # print(f"\t- {node_address} ({node_country}, AS{node_as})")

      for i, entry in enumerate(circ.path):
        div = '+' if (i == len(circ.path) - 1) else '|'
        fingerprint, nickname = entry

        desc = controller.get_network_status(fingerprint, None)
        address = desc.address if desc else 'unknown'
        locale = controller.get_info("ip-to-country/" + desc.address)
        # print(controller.get_info("entry-guards"))
        print(locale)
        # print(desc)
        # country = str_tools.safe_str(desc.country) if desc else 'unknown'

        print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))

def startNew():
  tor_process = stem.process.launch_tor_with_config(
    config={
        "SocksPort": "9200",
        "ControlPort": "9201",
        "EntryNodes": entry_node,
        "MiddleNodes": middle_node,
        "ExitNodes": exit_node
    }
  )
  with Controller.from_port(port=9201) as controller:
    controller.authenticate()
    controller.signal(Signal.NEWNYM)
  listCircuits()
  tor_process.kill()

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
    response = session.head(url)
    return response
  except:
    print("Could not connect")

def latencyCheck():
  # print(get('http://google.com'))
  session = requests.session()
  session.proxies = {
    'http': 'socks5://127.0.0.1:%s' % SOCKS_PORT,
    'https': 'socks5://127.0.0.1:%s' % SOCKS_PORT,
  }
  response = session.head('http://youtube.com')
  print(response)
  if response.status_code == 200:
     print(response.elapsed)
  else:
     print(response.elapsed)
     print("Did not return 200")

def expNew():
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  # circuit = controller.new_circuit(["Onyx", "TorRelayPoland", "krustykrab", "FatTubes", "d2d4"])
  circuit = controller.new_circuit(["Onyx", "TorRelayPoland", "d2d4"])
  # circuit = controller.new_circuit()
  # circuit = controller.new_circuit(["Onyx","d2d4"])
  # for circ in sorted(controller.get_circuits()):
  #   if circ.status != CircStatus.BUILT:
  #     continue
  #   if (len(circ.path) == 1):
  #     continue
  #   controller.close_circuit(circ.id)
  # circuit.open_stream("www.google.com")
  # response = circuit.read()
  # controller.add_nodes(["Onyx", "TorRelayPoland", "d2d4"])
  # circuit = controller.build_circuit()
  listCircuits()

def listStuff():
  listCircuits()
  print("-------------------")
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  relays = controller.get_network_statuses()
  exits = [relay for relay in relays if relay.exit_policy.is_exiting_allowed()]
  exit_ips = [exit.nickname for exit in exits]
  for exit_ip in exits:
    locale = controller.get_info("ip-to-country/" + exit_ip.address)
    print(locale + " " + exit_ip.nickname + " " + exit_ip.address)
  # print(exit_ips)
  # for desc in controller.get_server_descriptors():
  #   if desc.exit_policy.is_exiting_allowed():
  #     print(desc.address)
  # downloader = DescriptorDownloader()
  # consensus = downloader.get_consensus()
  # print(consensus)
  # relays = [desc for desc in consensus.routers if desc.flags & Flag.RUNNING]
  # for relay in relays:
  #   print(relay.nickname)
  # url = "https://check.torproject.org/exit-addresses"
  # response = requests.get(url)
  # exit_nodes = response.json()["exit_addresses"]
  # controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  # controller.authenticate()
  # exit_nodes = controller.get_info("ns/all-exit-ports")
  # print(exit_nodes)

def closeAllBuiltCircuits(controller):
  for circ in sorted(controller.get_circuits()):
    if circ.status != CircStatus.BUILT:
      continue
    if (len(circ.path) == 1):
      continue
    controller.close_circuit(circ.id)

def getNodesForCountry(control_port, country):
  controller = stem.control.Controller.from_port(port = control_port)
  controller.authenticate()
  
def createNewDefaultCircuit():
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  controller.signal(Signal.NEWNYM)

def remakeTor(num_hops):
  cmd_str = "sed -i '902s/.*/#define DEFAULT_ROUTE_LEN "+ str(num_hops) +"/' src/core/or/or.h"
  subprocess.run(cmd_str, cwd="/users/ys5608/code/tor/", shell=True)
  subprocess.run("sudo make uninstall", cwd="/users/ys5608/code/tor/", shell=True)
  subprocess.run("sudo make install", cwd="/users/ys5608/code/tor/", shell=True)
  tor_process = subprocess.Popen("exec tor --controlport 9201", cwd="/users/ys5608/code/tor/", shell=True)
  time.sleep(10)
  return tor_process

# startNew()
# createNewDefaultCircuit()
# listCircuits()
# get("www.google.com")
# latencyCheck()
# expNew()
# listStuff()
process = remakeTor(2)
print("Here")
print(process.pid)
# process.kill()
listCircuits()
process.send_signal(signal.SIGINT)
print("Hoho")
# os.killpg(os.getpgid(process.pid), signal.SIGINT)