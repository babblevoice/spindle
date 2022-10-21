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
routes = []
values = {}

pending = {}
pending_prefix = '_spindle_pending_'

# define utilities

def pluck_subset(item, keys):
  # return value from data tree
  for key in keys:
    try: key = int(key)
    except Exception: pass
    item = item[key]
  return item

def make_request(url):
  # return parsed JSON response
  req = Request(url)
  with urlopen(req) as res:
    json_str = res.read().decode('utf-8')
  return loads(json_str)

# define primaries

def locate_value(url, keys=None):
  # handle any URL subset part
  if '[' in url or ']' in url:
    err = SyntaxError(f'Incomplete subset in URL "{url}"')
    # split URL if subset delimited
    if not ']' in url or not '[' in url: raise err
    parts = url.split('[')
    url = parts[0].strip()
    # extract keys if notation full
    if '.' != parts[1].strip()[0]: raise err
    keys = [key.strip() for key in parts[1][:-1].split('.')[1:]]
  value = make_request(url)
  # restrict data to any subset
  if keys: value = pluck_subset(value, keys)
  return value

def gather_values_initial(item):
  # return value for each source URL or placeholder if route pending
  # handle base case
  if isinstance(item, str):
    # assumed URL: make request and return response
    if item not in routes: return locate_value(item)
    # assumed route name:
    # - value currently available: return data
    if item in values and (not isinstance(values[item], str)\
      or pending_prefix not in values[item]):
      return values[item]
    # - value unavailable: mark route pending
    placeholder = pending_prefix + item
    pending[placeholder] = item
    return placeholder
  # recurse for nested items
  if isinstance(item, list):
    return [gather_values_initial(nested_item) for nested_item in item]
  if isinstance(item, dict):
    return {key: gather_values_initial(value) for key, value in item.items()}

def insert_values_pending(item):
  # return values with each final value substituted for placeholder
  # handle base case
  if isinstance(item, str) and item in pending.keys():
    return values[pending[item]]
  # recurse for nested items
  if isinstance(item, list):
    return [insert_values_pending(nested_item) for nested_item in item]
  if isinstance(item, dict):
    return {key: insert_values_pending(value) for key, value in item.items()}
  return item

# parse configuration

with open(file, 'r') as f:
  # extract config to source dict with route name as key and source URL as value
  config = f.read()
  source = safe_load(config)
  routes = source.keys()

# get source URL values

for name, src in source.items():
  # build values dict with route name as key and source URL data as value
  values[name] = gather_values_initial(src)

for _ in enumerate(pending):
  # update values dict with final values for routes marked pending
  values = insert_values_pending(values)

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
