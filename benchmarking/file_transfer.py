import socket
import socks
import http.client

# IS_SERVER = True
IS_SERVER = False

def server():
  # socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
  # socket.socket = socks.socksocket
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # TCP_IP = socket.gethostbyaddr('216.165.95.184')[2]
  # print(TCP_IP)
  # sock.bind(('localhost', 12348))
  host = socket.gethostname()
  print(host)
  server_socket.bind(('216.165.95.153', 12343))
  # server_socket.bind(('172.58.228.79', 12346))
  server_socket.listen(1)
  client_socket, address = server_socket.accept()
  print(address)
  # client.sendfile('popular_websites.txt')
  file = open('popular_websites.txt', 'rb')
  sendData = file.read(1024)
  client_socket.send(sendData)
  # client.send('WooHoo')
  client_socket.close()
  server_socket.close()

def clientS():
  socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 9050, True)
  socket.socket = socks.socksocket
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  # host = '10-16-188-38.dynapool.wireless.nyu.edu'
  host = '10.16.252.228'
  # IP_ADR = '216.165.95.184'
  IP_ADR = '10-16-252-228.dynapool.wireless.nyu.edu'
  client_socket.connect((IP_ADR, 12342))
  # print(socket.gethostbyaddr('216.165.95.184'))
  # client_socket.connect((socket.gethostbyaddr('216.165.95.184')[0], 12348))
  # s.send("why")
  recvData = client_socket.recv(1000)
  # clnt = http.client.Client()
  # request = clnt.request('GET', 'localhost:12345/popular_websites.txt')
  # response = request.read()
  with open('response.txt', 'wb') as f:
    f.write(recvData)

if IS_SERVER:
  server()
else:
  clientS()
