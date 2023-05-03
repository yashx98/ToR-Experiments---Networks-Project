import socket
import socks
import http.client
import string
import random
import time
import statistics
import subprocess
import os
import signal
from stem import Signal, CircStatus
from stem.control import Controller, EventType
import matplotlib.pyplot as plt

# IS_SERVER = True
IS_SERVER = False
PORT_NO = 12345
SEND_SERVER_PORT_NO = 12346
RECV_SERVER_PORT_NO = 12347
FILE_NAME = 'random_text.txt'
RECV_FILE_NAME = 'recv_random_text.txt'
FILE_SIZE = 1024 * 1024 * 100 # 100MB
NUM_TIMES = 10
NUM_TIMES_LATENCY = 100
TOR_PORT = 9200
SOCKS_PORT = 9200
CONTROL_PORT = 9201
MAX_NUM_HOPS = 10
MEAN_STR = "Mean"
MEADIAN_STR = "Median"
STD_DEV_STR = "Standard Deviation"
COF_VAR_STR = "Coefficient of Variation"
IP_ADR = 'linserv1.cims.nyu.edu'
NUM_IGNORE_INITIAL = 0
NUM_IGNORE_INITIAL_THROUGHPUT = 0
NUM_INITIAL_THROUGHPUT = 20

def server():
  # socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
  # socket.socket = socks.socksocket
  createRandomFile(FILE_NAME, FILE_SIZE)
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # TCP_IP = socket.gethostbyaddr('216.165.95.184')[2]
  # print(TCP_IP)
  # sock.bind(('localhost', 12348))
  host = socket.gethostname()
  print(host)
  server_socket.bind(('', SEND_SERVER_PORT_NO))
  # server_socket.bind(('172.58.228.79', 12346))
  server_socket.listen(100)
  while True:
    client_socket, address = server_socket.accept()
    print(address)
    # client.sendfile('popular_websites.txt')
    with open(FILE_NAME, 'rb') as f:
      while True:
        data = f.read(1024)
        if not data:
          break
        client_socket.sendall(data)
    client_socket.close()
  server_socket.close()
  # file = open(FILE_NAME, 'rb')
  # sendData = file.read(1024)
  # client_socket.send(sendData)
  # # client.send('WooHoo')

def serverReceive():
  # createRandomFile(FILE_NAME, FILE_SIZE)
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = socket.gethostname()
  print(host)
  server_socket.bind(('', RECV_SERVER_PORT_NO))
  server_socket.listen(100)
  while True:
    client_socket, address = server_socket.accept()
    print(address)
    # with client_socket, open(RECV_FILE_NAME, 'wb') as f:
    while True:
      data = client_socket.recv(1024)
      if not data:
        break
        # f.write(data)
    # with open(FILE_NAME, 'rb') as f:
    #   while True:
    #     data = f.read(1024)
    #     if not data:
    #       break
    #     client_socket.sendall(data)
    client_socket.close()
  server_socket.close()

def serverLatency():
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = socket.gethostname()
  print(host)
  server_socket.bind(('', PORT_NO))
  server_socket.listen(100)
  while True:
    client_socket, address = server_socket.accept()
    print(address)
    client_socket.send(b'Hey')
    client_socket.close()
  server_socket.close()

def clientThroughput():
  # socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
  # socket.socket = socks.socksocket
  # host = '10-16-188-38.dynapool.wireless.nyu.edu'
  # IP_ADR = '216.165.95.184'
  # IP_ADR = '10-16-252-228.dynapool.wireless.nyu.edu'
  host = '10.16.252.228'
  IP_ADR = 'linserv1.cims.nyu.edu'
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect((IP_ADR, SEND_SERVER_PORT_NO))
  start_time = time.time()
  # print(socket.gethostbyaddr('216.165.95.184'))
  # client_socket.connect((socket.gethostbyaddr('216.165.95.184')[0], 12348))
  # s.send("why")
  # recvData = client_socket.recv(1000)
  # clnt = http.client.Client()
  # request = clnt.request('GET', 'localhost:12345/popular_websites.txt')
  # response = request.read()
  # with client_socket, open(FILE_NAME, 'wb') as f:
  while True:
    data = client_socket.recv(1024)
    if not data:
      break
      # f.write(data)
  end_time = time.time()
  client_socket.close()
  throughput = FILE_SIZE / (end_time - start_time) / 1024 / 1024
  print(throughput)
  return throughput

def clientSendThroughput():
  host = '10.16.252.228'
  IP_ADR = 'linserv1.cims.nyu.edu'
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_socket.connect((IP_ADR, RECV_SERVER_PORT_NO))
  start_time = time.time()
  # print(socket.gethostbyaddr('216.165.95.184'))
  # client_socket.connect((socket.gethostbyaddr('216.165.95.184')[0], 12348))
  # s.send("why")
  # recvData = client_socket.recv(1000)
  # clnt = http.client.Client()
  # request = clnt.request('GET', 'localhost:12345/popular_websites.txt')
  # response = request.read()
  with open(RECV_FILE_NAME, 'rb') as f:
    while True:
      data = f.read(1024)
      if not data:
        break
      client_socket.sendall(data)
  end_time = time.time()
  client_socket.close()
  throughput = FILE_SIZE / (end_time - start_time) / 1024 / 1024
  print(throughput)
  return throughput


def clientLatency():
  # socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
  # socket.socket = socks.socksocket
  # if use_tor:
  #   socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", SOCKS_PORT, True)
  #   socket.socket = socks.socksocket
  # IP_ADR = 'linserv1.cims.nyu.edu'
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  start_time = time.time()
  client_socket.connect((IP_ADR, PORT_NO))
  data = client_socket.recv(1024)
  end_time = time.time()
  client_socket.close()
  latency = (end_time - start_time)
  print(latency)
  return latency

def measureThroughput(send_file = False, use_tor = False, is_initial = False):
  if use_tor:
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", SOCKS_PORT, True)
    socket.socket = socks.socksocket
  throughputs = []
  num = NUM_TIMES
  if is_initial:
    num = NUM_INITIAL_THROUGHPUT
  i = 0
  # for i in range(num):
  while i < num:
    if i < NUM_IGNORE_INITIAL_THROUGHPUT:
      i += 1
      continue
    try:
      if not send_file:
        throughputs.append(clientThroughput())
      else:
        throughputs.append(clientSendThroughput())
    except Exception as e:
      print("Exception occured while calculating throughput: " + str(e))
      i -= 1
    i += 1
  if use_tor:
    socks.set_default_proxy(None)
    socket.socket = socks.socksocket
  print(throughputs)
  mean_throughput = statistics.mean(throughputs)
  median_throughput = statistics.median(throughputs)
  std_dev_throughput = statistics.stdev(throughputs)
  coef_var = std_dev_throughput * 100 / mean_throughput
  print("Num times %s" % num)
  print("Mean %s" % mean_throughput)
  print("Median %s" % median_throughput)
  print("Std Dev %s" % std_dev_throughput)
  print("Coefficient of variation %s" % coef_var)
  stats = {}
  stats[MEAN_STR] = mean_throughput
  stats[MEADIAN_STR] = median_throughput
  stats[STD_DEV_STR] = std_dev_throughput
  stats[COF_VAR_STR] = coef_var
  return stats

def measureLatency(use_tor = False):
  if use_tor:
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", SOCKS_PORT, True)
    socket.socket = socks.socksocket
  latencies = []
  i = 0
  # for i in range(NUM_TIMES_LATENCY):
  while i < NUM_TIMES_LATENCY:
    if i < NUM_IGNORE_INITIAL:
      i += 1
      continue
    try:
      latencies.append(clientLatency())
    except Exception as e:
      print("Exception occured while calculating latency: " + str(e))
      continue
    i += 1
  if use_tor:
    socks.set_default_proxy(None)
    socket.socket = socks.socksocket
  print(latencies)
  mean_latency = statistics.mean(latencies)
  median_latency = statistics.median(latencies)
  std_dev_latency = statistics.stdev(latencies)
  coef_var = std_dev_latency * 100 / mean_latency
  print("Num times %s" % NUM_TIMES_LATENCY)
  print("Mean %s" % mean_latency)
  print("Median %s" % median_latency)
  print("Std Dev %s" % std_dev_latency)
  print("Coefficient of variation %s" % coef_var)
  stats = {}
  stats[MEAN_STR] = mean_latency
  stats[MEADIAN_STR] = median_latency
  stats[STD_DEV_STR] = std_dev_latency
  stats[COF_VAR_STR] = coef_var
  return stats

def createRandomFile(name, size):
  random_text = ''.join(random.choices(string.ascii_lowercase + string.digits, k=size))
  with open(name, 'w') as f:
    f.write(random_text)

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

def measureLatencyOverHops():
  latencies_stats = []
  for i in range(1, MAX_NUM_HOPS + 1):
    tor_process = None
    if i != 1:
      tor_process = remakeTorWithChangedHops(i)
      listCircuits()
    # for j in NUM_TIMES_LATENCY:
    if i == 1:
      # Normal without tor proxy
      stats = measureLatency()
      latencies_stats.append(stats)
      continue
    # With tor proxy
    stats = measureLatency(True)
    latencies_stats.append(stats)
    if i != 1:
      tor_process.send_signal(signal.SIGINT)
  print(latencies_stats)
  stats_arr = [MEAN_STR, MEADIAN_STR]
  fig, ax = plt.subplots()
  x_axis = [0]
  for i in range(2, MAX_NUM_HOPS + 1):
    x_axis.append(i)
  for stat in stats_arr:
    y_axis = []
    for i in range(MAX_NUM_HOPS):
      y_axis.append(latencies_stats[i][stat])
    ax.plot(x_axis, y_axis, marker='o', markersize=4, label=stat + ' Latency Time')
  ax.set_xlabel('Circuit Length')
  ax.set_ylabel('Time (ms)')
  ax.set_title('Latencies')
  ax.legend()
  plt.savefig('LatenciesTime.png')
  return latencies_stats


def measureThroughputOverHops(send_file = False):
  throughputs_stats = []
  for i in range(1, MAX_NUM_HOPS + 1):
    tor_process = None
    if i != 1:
      tor_process = remakeTorWithChangedHops(i)
      listCircuits()
    if i == 1:
      # Normal without tor proxy
      stats = measureThroughput(send_file, False)
      throughputs_stats.append(stats)
      continue
    # With tor proxy
    stats = measureThroughput(send_file, True)
    throughputs_stats.append(stats)
    if i != 1:
      tor_process.send_signal(signal.SIGINT)
  print(throughputs_stats)
  stats_arr = [MEAN_STR, MEADIAN_STR]
  fig, ax = plt.subplots()
  x_axis = [0]
  for i in range(2, MAX_NUM_HOPS + 1):
    x_axis.append(i)
  for stat in stats_arr:
    y_axis = []
    for i in range(MAX_NUM_HOPS):
      y_axis.append(throughputs_stats[i][stat])
    ax.plot(x_axis, y_axis, marker='o', markersize=4, label=stat + ' Throughput')
  ax.set_xlabel('Circuit Length')
  ax.set_ylabel('Throughput (MBps)')
  ax.set_title('Circuit Throughputs')
  ax.legend()
  plt.savefig('Throughput.png')
  return throughputs_stats


def main():
  print("Choose one of the following options:")
  print("Type 1 to start a server which will send a file")
  print("Type 2 to start a client which will receive the file from the corresponding server")
  print("Type 3 to start a server for measuring latency")
  print("Type 4 to start a client for measuring latency")
  print("Type 5 to start a server which will receive a file")
  print("Type 6 to start a client which will send the file to the corresponding server")
  # choice = input()
  # choice = int(choice)
  # subprocess.run("tor --version", shell=True)
  # tor_process = subprocess.Popen("exec tor --controlport 9201", cwd="/users/ys5608/code/tor/", shell=True)
  # createRandomFile(RECV_FILE_NAME, FILE_SIZE)
  choice = 6
  if choice == 1:
    server()
  elif choice == 2:
    clientThroughput()
  elif choice == 3:
    serverLatency()
  elif choice == 4:
    measureLatencyOverHops()
  elif choice == 5:
    serverReceive()
  elif choice == 6:
    measureThroughputOverHops(True)



if __name__ == "__main__":
  main()

# if IS_SERVER:
#   server()
# else:
#   # clientS()
#   # measureThroughput()
#   measureLatency()