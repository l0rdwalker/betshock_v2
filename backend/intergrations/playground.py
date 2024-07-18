from datetime import datetime,timedelta
import math
import requests

def init(data={'sport':'horses'}) -> None:
    requests.post('http://127.0.0.1:8081/updateArbs', json=data) 
    
init()
print('test')