import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_database import database

from database.databaseOperations import databaseOperations

class arbie_reviseDates(database):
    def __init__(self, attributes) -> None:
        super().__init__(attributes)
        self.operation = 'revise_dates'
        
    def get_next_run(self):
        return datetime.now()
        
    def init(self, data=None) -> None:
        race_start_time_options = {}
        for platform_offerings in data:
            for race in platform_offerings['data']:
                key = str(hash(f'{race["round"]}{race["name"]}'))
                if not key in race_start_time_options:
                    race_start_time_options[key] = [race['start_time']]
                else:
                    race_start_time_options[key].append(race['start_time'])
        

        for key,time_options in race_start_time_options.items():
            race_time_frequencys = {}
            for time_option in time_options:
                if not time_option in race_time_frequencys:
                    race_time_frequencys[time_option] = 1
                else:
                    race_time_frequencys[time_option] += 1
            consensus = None 
            consensus_frequency = 0
            for time_option,frequency in race_time_frequencys.items():
                if consensus == None:
                    consensus = time_option
                    consensus_frequency = frequency
                elif consensus_frequency < frequency:
                    consensus_frequency = frequency
                    consensus = time_option
            race_start_time_options[key] = consensus
            
        for platform_offerings in data:
            for race in platform_offerings['data']:
                key = str(hash(f'{race["round"]}{race["name"]}'))
                race['start_time'] = race_start_time_options[key]
        
        return data
        
        
