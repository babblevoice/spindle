# spindle

Provisionally named work in progress.

## Goal

Provide a flat API each route of which returns data collated from one or more other URLs in full or part at a set interval, with each route defined in a YAML configuration file pre-startup and/or live.

## Done

- route definition in a YAML configuration file with recursive load of arbitrarily deep nested sequences and mappings of source URLs or other route names or subsets of the same
- retrieval of data from all source URLs, intially once per startup, plus single iteration replacement of other route names with corresponding data where retrieval is pending
- serving of one route per route defined, each returning the corresponding data, plus an `/all` route returning the data from all defined routes keyed by route name

## Todo

- refresh source data at default and per route intervals
- allow for route definition using:
  - other HTTP methods
  - data tree level transformations via the data subset indicator
- provide management routes:
  - `/get`, for configuration file content
  - `/set`, for live route definition
- extend server implementation
- persist source data
- containerise
- ...

## Requirements

The following dependencies are used:

- Python 3
- [PyYAML](https://github.com/yaml/pyyaml)

The spindle root directory requires a configuration file - spindle.yaml.

## Recombination

The configuration file is a set of key-value pairs in YAML format.

### Route names

Each key in the YAML configuration file is a route name. A route name is simply an arbitrary identifier for a GET endpoint to be served by spindle.

### Sources

Each value in the YAML configuration file is one of the following:

- a source string consisting of a URL, a GET endpoint called by spindle to provide the data for the given route
- a source string consisting of another route name defined elsewhere in the file, representing the reuse of the data from that route
- a YAML sequence or mapping of either of the above types of source string

#### Data subset indicators

Each source string, whether URL or route name, may have a data subset indicator appended, allowing a value on its corresponding data tree to be returned directly. A source string with a data subset indicator takes the form `some_url/some_route_name[.item_1.item_2.item_n]`, where the nested items may be referenced by either a sequence index or mapping key.

### Example

For the test endpoints in [Development](#development) below, the following YAML configuration could be created:

```yaml
route1: http://localhost:8000/one
route2: http://localhost:8000/two
route3:
  - http://localhost:8000/one
  - one: http://localhost:8000/one
    two: http://localhost:8000/two
route4:
  one: http://localhost:8000/one
  two:
    - http://localhost:8000/one
    - http://localhost:8000/two
  six: route6
#route5: http://localhost:8000/old
route6: http://localhost:8000/one[.key1]
route7: route2[.1.key2b]
```

Routes `-3` and `-4` demonstrate the use of nested sequences and mappings, `-4` and `-7` a route name as a source and `-6` and `-7` the data subset indicator.

A file with this content can be found at test/test.yaml.

### The /all route

One additional route - `/all` - is available by default. This returns a JSON string with keys corresponding to the route names in the configuration file, with the value for each key the data returned by that route.

### Serving the API

When the main file is run, all source URLs are called and the data for each route is served by default at `localhost:5912` ('SPIN').

## CLI commands

The main file can be run with the command `python3 spindle.py`.

### Development

A development server listening at `localhost:8000` can be set up quickly using [FastAPI and Uvicorn](https://github.com/tiangolo/fastapi#installation).

With the dependencies installed, a file is created to define the development endpoints, which for the example in [Recombination](#recombination) above could contain the following:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get('/one')
def read_one():
  return {'key1': ['value1a', 'value1b']}

@app.get('/two')
def read_two():
  return [{'key2a': 'value2a'}, {'key2b': 'value2b'}]
```

A file with this content can be found at test/test.py and run from that directory with the command `uvicorn test:app`.
