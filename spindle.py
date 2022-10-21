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

source = {}
values = {}

# define utilities

def make_request(url):
  # return parsed JSON response
  req = Request(url)
  with urlopen(req) as res:
    json_str = res.read().decode('utf-8')
  return loads(json_str)

# define primaries

def gather_values_initial(item):
  # return value for each source URL
  # handle base case
  if isinstance(item, str):
    return make_request(item)
  # recurse for nested items
  if isinstance(item, list):
    return [gather_values_initial(nested_item) for nested_item in item]
  if isinstance(item, dict):
    return {key: gather_values_initial(value) for key, value in item.items()}

# parse configuration

with open(file, 'r') as f:
  # extract config to source dict with route name as key and source URL as value
  config = f.read()
  source = safe_load(config)

# get source URL values

for name, src in source.items():
  # build values dict with route name as key and source URL data as value
  values[name] = gather_values_initial(src)

# merge values for /all

values['all'] = dict([[items[0], items[1]] for items in values.items()])

# serve values by route

class TCPRequestHandler(BaseRequestHandler):

  def handle(self):
    self.data = self.request.recv(1024).strip()
    route = self.data.decode('utf-8').split('\n')[0].split(' ')[1][1:]
    res_data = values.get(route) # value or None
    res_json = dumps(res_data) if res_data is not None else dumps({'Error': 'Route unavailable'})
    self.request.sendall(bytes(res_json, 'utf-8'))

TCPServer.allow_reuse_address = True

with TCPServer((host, port), TCPRequestHandler) as server:
  print(f'Call API at {host}:{port} | Press Ctrl+C here to stop')
  server.serve_forever()
