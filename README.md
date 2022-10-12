# spindle

Provisionally named work in progress.

## Todo

- refresh source data at default and per route intervals
- allow for route definition using:
  - mixed data structures
  - other defined routes
  - source data subsets
  - other HTTP methods
- persist source data
- containerise
- ...

## Requirements

The following dependencies are used:

- Python 3
- [PyYAML](https://github.com/yaml/pyyaml)

The spindle root directory requires a configuration file - spindle.yaml.

## Recombination

The configuration file is a set of key-value pairs in YAML format. Each key is a route name and each value a source URL string or a YAML sequence or mapping of source URL strings. The route name is a GET endpoint to be served by spindle, while each corresponding source URL is an endpoint called by spindle to provide the data for that route.

For example, for the test endpoints in [Development](#development) below:

```yaml
route1: http://localhost:8000/one
route2: http://localhost:8000/two
route3:
  - http://localhost:8000/one
  - http://localhost:8000/two
route4:
  one: http://localhost:8000/one
  two: http://localhost:8000/two
```

One additional route - `/all` - is available by default. This returns a JSON string with keys corresponding to the route names in the configuration file, with the value for each key the data returned by that endpoint.

When the main file is run, all source URLs are called and each corresponding route is served by default at `localhost:5912` ('SPIN').

## CLI commands

The main file can be run with the command `python3 spindle.py`.

### Development

A development server listening at `localhost:8000` can be set up quickly using [FastAPI and Uvicorn](https://github.com/tiangolo/fastapi#installation). With the dependencies installed, a file named main.py can be created to define the development endpoints, which for the example in [Recombination](#recombination) above could contain the following:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get('/one')
def read_one():
  return { 'key1': 'value1' }

@app.get('/two')
def read_two():
  return { 'key2': 'value2' }
```

The server can then be run with the command `uvicorn main:app`.
