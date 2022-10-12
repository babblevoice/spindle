# spindle

Provisionally named work in progress.

## Todo

- revise configuration for use of yaml
- refresh source data at default and per route intervals
- allow for route definition using:
  - multiple sources combined
  - other defined routes
  - source data subsets
- persist source data
- containerise
- ...

## Requirements

The following dependencies are used:

- Python 3

The spindle root directory requires a configuration file - spindle.txt.

## Recombination

The configuration file lists pairs of values, each pair being a route name and a source URL, one pair per line, with the route name and source URL separated by a colon and any number of spaces. Each route name is a GET endpoint to be served by spindle, while the corresponding source URL the endpoint called by spindle to provide the data for that route.

For example, for the test endpoints in [Development](#development) below:

```
route1: http://localhost:8000/one
route2: http://localhost:8000/two
```

An additional route named `/all` is available by default. This returns a JSON string with keys corresponding to the route names in the configuration file, with the value for each key the data returned by that endpoint.

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
