# include global dependencies

# - standard library
from urllib.request import Request, urlopen
from json import loads, dumps
from socketserver import BaseRequestHandler, TCPServer

# - external library
from yaml import safe_load

# set default values

file = 'spindle.yaml'
host = 'localhost'
port = 5912

srcs = {}
data = {}

# parse configuration

with open(file, 'r') as f:
  # extract config to srcs dict with route name as key and source URL as value
  conf = f.read()
  srcs = safe_load(conf)

# get source URL data

for name, url in srcs.items():
  # build data dict with route name as key and source URL data as value
  # by making request per srcs dict pair and reading JSON to dict
  req = Request(url)
  with urlopen(req) as res:
    json_str = res.read().decode('utf-8')
  data[name] = loads(json_str)

# merge data for /all

data['all'] = dict([[items[0], items[1]] for items in data.items()])

# serve data by route

class TCPRequestHandler(BaseRequestHandler):

  def handle(self):
    self.data = self.request.recv(1024).strip()
    route = self.data.decode('utf-8').split('\n')[0].split(' ')[1][1:]
    res_data = data.get(route) # data or None
    res_json = dumps(res_data) if res_data is not None else dumps({'Error': 'Route unavailable'})
    self.request.sendall(bytes(res_json, 'utf-8'))

TCPServer.allow_reuse_address = True

with TCPServer((host, port), TCPRequestHandler) as server:
  print(f'Call API at {host}:{port} | Press Ctrl+C here to stop')
  server.serve_forever()
