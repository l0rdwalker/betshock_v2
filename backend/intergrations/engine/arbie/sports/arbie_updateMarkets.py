import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_database import database

from database.databaseOperations import databaseOperations

class arbie_updateMarkets(database):
    def __init__(self, attributes) -> None:
        super().__init__(attributes)
        self.operation = 'arbie_updateMarkets'
        self.database = databaseOperations()
        
    def init(self, update_data=None) -> None:
        if (update_data == None):
            return None
        if len(update_data) == 0:
            return None
        update_data = update_data[0]
        
        self.database.initConnection()
        for race in update_data['data']:
            race_id = self.database.deduce_race_id(race['track'],race['start_time'])
            for entrant in race['entrants']:
                horse_name = entrant['name'].replace("'","").strip().lower()
                horse_id = self.database.impose_horse(horse_name)
                entrant_id = self.database.deduce_entrant_id(race_id,horse_id)
                if not entrant_id == None:
                    self.database.impose_market_condition(entrant_id,entrant['market_size'])
        self.database.closeConnection()
        
        
        