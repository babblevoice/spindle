from fastapi import FastAPI

app = FastAPI()

@app.get('/one')
def read_one():
  return {'key1': ['value1a', 'value1b']}

@app.get('/two')
def read_two():
  return [{'key2a': 'value2a'}, {'key2b': 'value2b'}]
