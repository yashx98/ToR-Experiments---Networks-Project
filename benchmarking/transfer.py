import torpy

def clientFn():
  client = torpy.TorClient()
  client.connect()