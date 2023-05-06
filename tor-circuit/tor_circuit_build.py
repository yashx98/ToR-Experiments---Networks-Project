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
import matplotlib.pyplot as plt
from file_transfer import measureLatency

SOCKS_PORT = 9200
CONTROL_PORT = 9201
MAX_NUM_HOPS = 8
NUM_ITER_FOR_COLLECTION = 30
NUM_CIRCUITS_SETUP = 100
COUNTRIES_TORRC_LINE_NUM = 256
NUM_TRIES_COUNTRY_CIRCUIT = 5
NUM_CIRCUITS_PARALLEL = 10
FINGERPRINT_STR = "Fingerprint"
IP_ADDRESS_STR = "IP Address"
LOCALE_STR = "Locale"
NICKNAME_STR = "Nickname"
ENTRY_NODE_STR = "Entry Node"
EXIT_NODE_STR = "Exit Node"
MIDDLE_NODE_STR = "Middle Node"
MEAN_STR = "Mean"
MEADIAN_STR = "Median"
STD_DEV_STR = "Standard Deviation"
SUCCESS_STR = "Success Rate"
COF_VAR_STR = "Coefficient of Variation"
NORTH_AMERICA_STR = "North America"
EUROPE_STR = "Europe"
EAST_ASIA_STR = "East Asia"

def remakeTorWithChangedHops(num_hops):
  cmd_str = "sed -i '902s/.*/#define DEFAULT_ROUTE_LEN "+ str(num_hops) +"/' src/core/or/or.h"
  subprocess.run(cmd_str, cwd="/users/ys5608/code/tor/", shell=True)
  print("Uninstalling tor")
  subprocess.run("sudo make uninstall", cwd="/users/ys5608/code/tor/", shell=True)
  print("Reinstalling tor with " + str(num_hops) + " hops.")
  subprocess.run("sudo make install", cwd="/users/ys5608/code/tor/", shell=True)
  print("Starting tor with hops=" + str(num_hops))
  tor_process = subprocess.Popen("exec tor --controlport 9201", cwd="/users/ys5608/code/tor/", shell=True)
  time.sleep(30)
  return tor_process

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
  median_time = statistics.median(cir_build_times)
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
  stats_dict = {}
  stats_dict[MEAN_STR] = mean_time
  stats_dict[MEADIAN_STR] = median_time
  stats_dict[STD_DEV_STR] = std_dev_time
  stats_dict[COF_VAR_STR] = coef_var
  stats_dict[SUCCESS_STR] = (NUM_CIRCUITS_SETUP / num_tries) * 100
  return stats_dict

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
        locale = controller.get_info("ip-to-country/" + desc.address)
        print(locale)

        print(" %s- %s (%s, %s)" % (div, fingerprint, nickname, address))

def clearAllCircuits():
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  for circ in sorted(controller.get_circuits()):
    if circ.status != CircStatus.BUILT:
      continue
    controller.close_circuit(circ.id)

def collectNodesData(desired_locale):
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  entry_nodes = []
  middle_nodes = []
  exit_nodes = []
  listCircuits()
  for circ in sorted(controller.get_circuits()):
    if circ.status != CircStatus.BUILT:
      continue
    for i, entry in enumerate(circ.path):
      fingerprint, nickname = entry
      desc = controller.get_network_status(fingerprint, None)
      address = desc.address if desc else 'unknown'
      locale = controller.get_info("ip-to-country/" + desc.address)
      if locale != desired_locale:
        continue
      node_details = {}
      node_details[FINGERPRINT_STR] = fingerprint
      node_details[IP_ADDRESS_STR] = address
      node_details[LOCALE_STR] = locale
      node_details[NICKNAME_STR] = nickname
      if i == 0:
        entry_nodes.append(node_details)
      elif i == (len(circ.path) - 1):
        exit_nodes.append(node_details)
      else:
        middle_nodes.append(node_details)
  nodes = {}
  nodes[ENTRY_NODE_STR] = entry_nodes
  nodes[MIDDLE_NODE_STR] = middle_nodes
  nodes[EXIT_NODE_STR] = exit_nodes
  return nodes

def measureCircuitBuildTimes():
  build_time_stats = []
  for i in range(2, MAX_NUM_HOPS + 1):
    tor_process = None
    if i != 1:
      tor_process = remakeTorWithChangedHops(i)
      listCircuits()
    if i == 1:
      # Normal without tor proxy
      stats = calCircuitSetupTimes()
      build_time_stats.append(stats)
      continue
    # With tor proxy
    stats = calCircuitSetupTimes()
    build_time_stats.append(stats)
    if i != 1:
      tor_process.send_signal(signal.SIGINT)
  print(build_time_stats)
  stats_arr = [MEAN_STR, MEADIAN_STR]
  fig, ax = plt.subplots()
  x_axis = []
  for i in range(2, MAX_NUM_HOPS + 1):
    x_axis.append(i)
  for stat in stats_arr:
    y_axis = []
    for i in range(MAX_NUM_HOPS - 1):
      y_axis.append(build_time_stats[i][stat])
    ax.plot(x_axis, y_axis, marker='o', markersize=4, label=stat + ' Build Time')
  ax.set_xlabel('Circuit Length')
  ax.set_ylabel('Circuit Build Time (s)')
  ax.set_title('Circuit Build Times')
  ax.legend()
  plt.savefig('CircuitBuildTimes.png')
  fig2, ax2 = plt.subplots()
  y_axis = []
  for i in range(MAX_NUM_HOPS - 1):
    y_axis.append(build_time_stats[i][SUCCESS_STR])
  ax2.plot(x_axis, y_axis, marker='o', markersize=4, label=stat + ' Build Time')
  ax2.set_xlabel('Circuit Length')
  ax2.set_ylabel('Success (%)')
  ax2.set_title('Circuit Build Build Success Rates %')
  ax2.legend()
  plt.savefig('CircuitBuildSuccessRate.png')
  return build_time_stats

def specifyCountryTorrcFile(node_type, countries_list, line_num):
  countries_str = ""
  if len(countries_list) == 0:
    countries_str = "{}"
  for i, country in enumerate(countries_list):
    if i == 0:
      countries_str += "{" + country + "}"
      continue
    countries_str += ",{" + country + "}"
  cmd_str = "sudo sed -i '" + str(line_num) + "s/.*/" + node_type + " " + countries_str +"/' torrc"
  subprocess.run(cmd_str, cwd="/usr/local/etc/tor/", shell=True)

def clearLinesTorrcFile(line_num):
  cmd_str = "sudo sed -i '" + str(line_num) + "s/.*//' torrc"
  subprocess.run(cmd_str, cwd="/usr/local/etc/tor/", shell=True)

def manualNodeCollection():
  nodes_collected = [{}, {}, {}]
  for i in range(NUM_ITER_FOR_COLLECTION):
    nodes_obtained = collectNodesData('us')
    for index, entry_node in enumerate(nodes_obtained[ENTRY_NODE_STR]):
      nodes_collected[0][entry_node[FINGERPRINT_STR]] = entry_node
    for index, middle_node in enumerate(nodes_obtained[MIDDLE_NODE_STR]):
      nodes_collected[1][middle_node[FINGERPRINT_STR]] = middle_node
    for index, exit_node in enumerate(nodes_obtained[EXIT_NODE_STR]):
      nodes_collected[2][exit_node[FINGERPRINT_STR]] = exit_node
    clearAllCircuits()
    time.sleep(10)
  print(nodes_collected)
  print("Num entry nodes: " + str(len(nodes_collected[0])))
  print("Num middle nodes: " + str(len(nodes_collected[1])))
  print("Num exit nodes: " + str(len(nodes_collected[2])))
  return nodes_collected

def workaroundForSpecificCountryNodes(countries_list):
  countries = {}
  for country in countries_list:
    countries[country] = 1
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  loop_again = True
  index = 0
  while loop_again and index < NUM_TRIES_COUNTRY_CIRCUIT:
    index += 1
    listCircuits()
    print("-----------------------------------------------------------------")
    loop_again = False
    for circ in sorted(controller.get_circuits()):
      if circ.status != CircStatus.BUILT:
        continue
      fingerprint, nickname = circ.path[-1]
      desc = controller.get_network_status(fingerprint, None)
      address = desc.address if desc else 'unknown'
      locale = None
      if address != 'unknown':
        locale = controller.get_info("ip-to-country/" + desc.address)
      else:
        locale = ""
      if locale in countries:
        continue
      loop_again = True
      controller.close_circuit(circ.id)
    time.sleep(5)

def runForCountries(countries_list, num_hops):
  specifyCountryTorrcFile("EntryNodes", countries_list, COUNTRIES_TORRC_LINE_NUM)
  specifyCountryTorrcFile("MiddleNodes", countries_list, COUNTRIES_TORRC_LINE_NUM + 2)
  tor_process = remakeTorWithChangedHops(num_hops)
  workaroundForSpecificCountryNodes(countries_list)
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  controller.set_conf('__DisablePredictedCircuits', '1')
  controller.set_conf('MaxOnionsPending', '0')
  controller.set_conf('newcircuitperiod', '999999999')
  controller.set_conf('maxcircuitdirtiness', '999999999')
  stats = measureLatency(True)
  clearLinesTorrcFile(COUNTRIES_TORRC_LINE_NUM)
  clearLinesTorrcFile(COUNTRIES_TORRC_LINE_NUM + 2)
  print("Last circuits list:")
  listCircuits()
  controller.reset_conf('__DisablePredictedCircuits')
  controller.reset_conf('MaxOnionsPending')
  controller.reset_conf('newcircuitperiod')
  controller.reset_conf('maxcircuitdirtiness')
  print("Set configs reset")
  listCircuits()
  clearAllCircuits()
  tor_process.send_signal(signal.SIGINT)
  return stats

def runOverDifferentRegions(countries_list):
  countriesRegions = [NORTH_AMERICA_STR, EUROPE_STR, EAST_ASIA_STR]
  fig, ax = plt.subplots()
  x_axis = []
  for i in range(2, MAX_NUM_HOPS + 1):
    x_axis.append(i)
  for region in countriesRegions:
    y_axis = []
    for i in range(2, MAX_NUM_HOPS + 1):
      stats = runForCountries(countries_list[region], i)
      y_axis.append(stats[MEAN_STR])
    ax.plot(x_axis, y_axis, marker='o', markersize=4, label=region)
  ax.set_xlabel('Circuit Length')
  # 
  ax.set_ylabel('Time (ms)')
  ax.set_title('Circuit Latencies in Different Regions')
  ax.legend()
  plt.savefig('LatenciesRegionTime.png')
  # 
  # ax.set_ylabel('Throughput (MBps)')
  # ax.set_title('Circuit Throughputs in Different Regions')
  # ax.legend()
  # plt.savefig('Throughput.png')

def getListOfNodes(countries_list):
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  nodes = controller.get_network_statuses()
  # entry_nodes = [node for node in nodes if 'Guard' in node.flags and 'Stable' in node.flags]
  entry_nodes = []
  middle_nodes = []
  exit_nodes = []
  for node in nodes:
    try:
      if 'Guard' in node.flags and 'Stable' in node.flags:
        locale = controller.get_info("ip-to-country/" + node.address)
        if locale in countries_list:
          node_details = {}
          node_details[FINGERPRINT_STR] = node.fingerprint
          node_details[IP_ADDRESS_STR] = node.address
          node_details[LOCALE_STR] = locale
          node_details[NICKNAME_STR] = node.nickname
          entry_nodes.append(node_details)
    except Exception as e:
      continue
  for desc in stem.descriptor.remote.get_server_descriptors():
    if desc.exit_policy.is_exiting_allowed() and desc.exit_policy.is_exiting_allowed():
      locale = controller.get_info("ip-to-country/" + desc.address)
      if locale in countries_list:
        node_details = {}
        node_details[FINGERPRINT_STR] = desc.fingerprint
        node_details[IP_ADDRESS_STR] = desc.address
        node_details[LOCALE_STR] = locale
        node_details[NICKNAME_STR] = desc.nickname
        exit_nodes.append(node_details)
    else:
      locale = controller.get_info("ip-to-country/" + desc.address)
      if locale in countries_list:
        node_details = {}
        node_details[FINGERPRINT_STR] = desc.fingerprint
        node_details[IP_ADDRESS_STR] = desc.address
        node_details[LOCALE_STR] = locale
        node_details[NICKNAME_STR] = desc.nickname
        middle_nodes.append(node_details)
  return entry_nodes, middle_nodes, exit_nodes
  # exit_nodes = controller.get_info("ns/all-exit-ports")
  # relays = controller.get_network_statuses()
  # exits = [relay for relay in relays if relay.exit_policy.is_exiting_allowed()]
  # exit_ips = [exit.nickname for exit in exits]
  # for exit_ip in exits:
  #   locale = controller.get_info("ip-to-country/" + exit_ip.address)
  #   print(locale + " " + exit_ip.nickname + " " + exit_ip.address)
  # 
  # 
  # consensus = stem.descriptor.remote.get_consensus()
  # for node in consensus.routers.values():
  #   if node.flags and Flag.GUARD:
  #     entry_nodes.append(node.address)
  # downloader = DescriptorDownloader(controller)
  # relays = downloader.get_server_descriptors()
  # for relay in relays:
  #   if Flag.GUARD in relay.flags and relay.address.endswith('.onion'):
  #     entry_nodes.append(relay.address)
  # print(entry_nodes)

def returnRandomNode(nodes, num):
  if len(nodes) == 0:
    entry, middle, exit = getListOfNodes(["us", "ca", "uk", "fr", "de", "dk"])
    if num == 0:
      return random.choice(entry)[NICKNAME_STR]
    elif num == 1:
      return random.choice(middle)[NICKNAME_STR]
    elif num == 2:
      return random.choice(exit)[NICKNAME_STR]
  return random.choice(nodes)[NICKNAME_STR]

def setupTorForRun(num_hops):
  tor_process = remakeTorWithChangedHops(num_hops)
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  controller.set_conf('__DisablePredictedCircuits', '1')
  controller.set_conf('MaxOnionsPending', '0')
  controller.set_conf('newcircuitperiod', '999999999')
  controller.set_conf('maxcircuitdirtiness', '999999999')
  return tor_process

def cleanupTorAfterRun(tor_process):
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  print("Last circuits list:")
  listCircuits()
  controller.reset_conf('__DisablePredictedCircuits')
  controller.reset_conf('MaxOnionsPending')
  controller.reset_conf('newcircuitperiod')
  controller.reset_conf('maxcircuitdirtiness')
  print("Set configs reset")
  listCircuits()
  clearAllCircuits()
  tor_process.send_signal(signal.SIGINT)

def torCreateCircuits(countries_list):
  entry, middle, exit = getListOfNodes(countries_list)
  controller = stem.control.Controller.from_port(port = CONTROL_PORT)
  controller.authenticate()
  clearAllCircuits()
  # Create new circuits randomly
  index = 0
  # for i in range(NUM_CIRCUITS_PARALLEL):
  while index < NUM_CIRCUITS_PARALLEL:
    # Entry node
    entry_node = returnRandomNode(entry, 0)
    # Exit node
    exit_node = returnRandomNode(exit, 2)
    seq_nodes = []
    seq_nodes.append(entry_node)
    # Middle nodes
    for i in range(2, MAX_NUM_HOPS):
      middle_node = returnRandomNode(middle, 1)
      seq_nodes.append(middle_node)
    seq_nodes.append(exit_node)
    try:
      controller.new_circuit(seq_nodes)
    except Exception as e:
      print("Error in creating tor circuit: " + str(e))
      continue
    index += 1

def runOverDifferentRegionsManually(countries_list):
  countriesRegions = []
  for region in countries_list:
    countriesRegions.append(region)
  fig, ax = plt.subplots()
  fig2, ax2 = plt.subplots()
  x_axis = []
  for i in range(2, MAX_NUM_HOPS + 1):
    x_axis.append(i)
  y_axis = {}
  y_axis2 = {}
  for region in countriesRegions:
    y_axis[region] = []
    y_axis2[region] = []
  for i in range(2, MAX_NUM_HOPS + 1):
    tor_process = setupTorForRun(i)
    for region in countriesRegions:
      torCreateCircuits(countries_list[region])
      stats = measureLatency(True)
      y_axis[region].append(stats[MEAN_STR])
      y_axis2[region].append(stats[MEADIAN_STR])
    cleanupTorAfterRun(tor_process)
  for region in countriesRegions:
    ax.plot(x_axis, y_axis[region], marker='o', markersize=4, label=region)
    ax2.plot(x_axis, y_axis2[region], marker='o', markersize=4, label=region)
  ax.set_xlabel('Circuit Length')
  ax2.set_xlabel('Circuit Length')
  # 
  ax.set_ylabel('Time (ms)')
  ax.set_title('Circuit Latencies in Different Regions')
  ax.legend()
  fig.savefig('MenaLatenciesRegionTime.png')
  # 
  ax2.set_ylabel('Time (ms)')
  ax2.set_title('Circuit Latencies in Different Regions')
  ax2.legend()
  fig2.savefig('MedianLatenciesRegionTime.png')
  # 
  # ax.set_ylabel('Throughput (MBps)')
  # ax.set_title('Circuit Throughputs in Different Regions')
  # ax.legend()
  # plt.savefig('Throughput.png')

def main():
  countries_list = {}
  countries_list[NORTH_AMERICA_STR] = ["us", "ca"]
  countries_list[EUROPE_STR] = ["uk", "fr", "de", "dk", "se", "no"]
  countries_list[EAST_ASIA_STR] = ["jp", "tw", "kr", "sg"]
  # runOverDifferentRegions(countries_list)
  # e, m, x = getListOfNodes(["us", "ca"])
  # print(e)
  runOverDifferentRegionsManually(countries_list)

  # listCircuits()
  # entry, middle, exit = getListOfNodes(countries_list[EAST_ASIA_STR])
  # createCircuitManually()
  # print(len(entry))


  # 
  # measureCircuitBuildTimes()
  # renewConnection()
  # clearAllCircuits()
  # tor_process = remakeTorWithChangedHops(3)
  # nodes_collected = manualNodeCollection()
  # Measure circuit build times
  # measureCircuitBuildTimes()
  # specifyCountryTorrcFile("EntryNodes", ["us"], COUNTRIES_TORRC_LINE_NUM)
  # specifyCountryTorrcFile("MiddleNodes", ["us"], COUNTRIES_TORRC_LINE_NUM + 2)
  # specifyCountryTorrcFile("ExitNodes", ["prsv"], COUNTRIES_TORRC_LINE_NUM + 2)
  # workaroundForSpecificCountryNodes(["us", "dk"])
  # listCircuits()
  # clearAllCircuits()


if __name__ == "__main__":
  main()
