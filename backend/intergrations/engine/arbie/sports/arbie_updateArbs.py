import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_database import database

class arbie_updateArbs(database):
    def __init__(self, attributes) -> None:
        super().__init__(attributes)
        self.operation = 'arbUpdate'
        
    def init(self, data=None) -> None:
        requests.post('http://127.0.0.1:8081/updateArbs', json={'sport':'horses'}) 
