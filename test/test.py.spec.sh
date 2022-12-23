# describe: source server (test.py)

it="serves source endpoint GET /one"

response=$(curl -s localhost:8000/one)
expected="{\"key1\":[\"value1a\",\"value1b\"]}"

sh test "$it" "$response" "$expected"


it="serves source endpoint GET /two"

response=$(curl -s localhost:8000/two)
expected="[{\"key2a\":\"value2a\"},{\"key2b\":\"value2b\"}]"

sh test "$it" "$response" "$expected"
