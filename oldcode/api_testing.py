import requests
import json

test = requests.get(url="http://127.0.0.1:8080/get_race_details/2533")
test = json.loads(test.text)

print("epic")