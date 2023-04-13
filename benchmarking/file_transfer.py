import socket
import socks
import http.client
import string
import random
import time
import statistics

# IS_SERVER = True
IS_SERVER = False
FILE_NAME = 'random_text.txt'
FILE_SIZE = 1024 * 1024 * 40 # 1MB
NUM_TIMES = 10
NUM_TIMES_LATENCY = 50
TOR_PORT = 9200

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
  server_socket.bind(('', 12345))
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

def serverLatency():
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  host = socket.gethostname()
  print(host)
  server_socket.bind(('', 12345))
  server_socket.listen(100)
  while True:
    client_socket, address = server_socket.accept()
    print(address)
    client_socket.send(b'Hey')
    client_socket.close()
  server_socket.close()

def clientS():
  # socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
  # socket.socket = socks.socksocket
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # host = '10-16-188-38.dynapool.wireless.nyu.edu'
  host = '10.16.252.228'
  # IP_ADR = '216.165.95.184'
  # IP_ADR = '10-16-252-228.dynapool.wireless.nyu.edu'
  IP_ADR = 'linserv1.cims.nyu.edu'
  start_time = time.time()
  client_socket.connect((IP_ADR, 12345))
  # print(socket.gethostbyaddr('216.165.95.184'))
  # client_socket.connect((socket.gethostbyaddr('216.165.95.184')[0], 12348))
  # s.send("why")
  # recvData = client_socket.recv(1000)
  # clnt = http.client.Client()
  # request = clnt.request('GET', 'localhost:12345/popular_websites.txt')
  # response = request.read()
  with client_socket, open(FILE_NAME, 'wb') as f:
    while True:
      data = client_socket.recv(1024)
      if not data:
        break
      f.write(data)
  end_time = time.time()
  client_socket.close()
  throughput = FILE_SIZE / (end_time - start_time) / 1024 / 1024
  print(throughput)
  return throughput
  # with open('response.txt', 'wb') as f:
  #   f.write(recvData)

def clientLatency():
  # socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
  # socket.socket = socks.socksocket
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  IP_ADR = 'linserv1.cims.nyu.edu'
  start_time = time.time()
  client_socket.connect((IP_ADR, 12345))
  data = client_socket.recv(1024)
  end_time = time.time()
  client_socket.close()
  latency = (end_time - start_time)
  print(latency)
  return latency

def measureThroughput():
  throughputs = []
  for i in range(NUM_TIMES):
    throughputs.append(clientS())
  print(throughputs)
  mean_throughput = statistics.mean(throughputs)
  median_throughput = statistics.median(throughputs)
  std_dev_throughput = statistics.stdev(throughputs)
  coef_var = std_dev_throughput * 100 / mean_throughput
  print("Num times %s" % NUM_TIMES)
  print("Mean %s" % mean_throughput)
  print("Median %s" % median_throughput)
  print("Std Dev %s" % std_dev_throughput)
  print("Coefficient of variation %s" % coef_var)

def measureLatency():
  latencies = []
  for i in range(NUM_TIMES_LATENCY):
    latencies.append(clientLatency())
  print(latencies)
  mean_latency = statistics.mean(latencies)
  median_latency = statistics.median(latencies)
  std_dev_latency = statistics.stdev(latencies)
  coef_var = std_dev_latency * 100 / mean_latency
  print("Num times %s" % NUM_TIMES)
  print("Mean %s" % mean_latency)
  print("Median %s" % median_latency)
  print("Std Dev %s" % std_dev_latency)
  print("Coefficient of variation %s" % coef_var)

def createRandomFile(name, size):
  random_text = ''.join(random.choices(string.ascii_lowercase + string.digits, k=size))
  with open(name, 'w') as f:
    f.write(random_text)



if IS_SERVER:
  server()
else:
  # clientS()
  # measureThroughput()
  measureLatency()
