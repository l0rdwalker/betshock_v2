import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))

from abstract_task import task

class arbie_updateFocus(task):
    def __init__(self, attributes,database) -> None:
        super().__init__(attributes,database)
        self.operation = 'arbUpdateFocus'
        
    def get_next_run(self):
        return datetime.now()
        
    def init(self, update_data=None, race_id=0) -> None:
        for platform in update_data:
            platform_name = platform['platform']
            for entrant in platform['data']:
                horse_name = entrant['name'].replace("'","").strip().lower()
                entrant_id = self.database.get_specific_entrant_id_by_name_and_race(race_id,horse_name) 
                if not entrant_id == None:
                    self.database.impose_odds(entrant_id,platform_name,entrant['odds'],entrant['record_time'])
