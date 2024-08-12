import requests

responce = requests.get(url='http://127.0.0.1:8080/get_day_races/1723013252641')
responce = responce.text
print("epic")
