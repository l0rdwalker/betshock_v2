import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_task import task

class arbie_updateMarkets(task):
    def __init__(self, attributes, database_obj) -> None:
        super().__init__(attributes, database_obj)
        self.operation = 'arbie_updateMarkets'
        
    def get_next_run(self):
        return datetime.now()
        
    def init(self, update_data=None) -> None:
        if (update_data == None):
            return None
        if len(update_data) == 0:
            return None
        update_data = update_data[0]
        
        for race in update_data['data']:
            entrant_names = []
            for entrant in race['entrants']:
                horse_name = entrant['name'].replace("'","").strip().lower()
                entrant_names.append(horse_name)
            if len(entrant_names) == 0:
                continue
            race_id = self.database.deduce_race_id_by_entrant(entrant_names,race['start_time'])
            if not race_id == None:
                for entrant in race['entrants']:
                    horse_name = entrant['name'].replace("'","").strip().lower()
                    horse_id = self.database.impose_horse(horse_name)
                    entrant_id = self.database.deduce_entrant_id(race_id,horse_id)
                    if not entrant_id == None:
                        self.database.impose_market_condition(entrant_id,entrant['market_size'])
        
        
        
