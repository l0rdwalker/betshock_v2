import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_database import database

from database.databaseOperations import databaseOperations

class arbie_updateArbs(database):
    def __init__(self, attributes) -> None:
        super().__init__(attributes)
        self.operation = 'arbUpdate'
        self.database = databaseOperations()
        
    def init(self, update_data=None) -> None:
        try:
            date_race_store = {}
            scratched_horses = {}
            self.database.initConnection()
            
            for platform in update_data:
                if (platform['platform'] == 'diamondbet'):
                    continue
                platform_id = self.database.impose_platform(platform['platform'])
                for race in platform['data']:
                    track_id = self.database.impose_track(race['name'])
                    race_id = self.database.impose_race(track_id,race['start_time'],race['round'])
                    for entrant in race['entrants']:
                        horse_name = entrant['name'].replace("'","").strip().lower()
                        horse_id = self.database.impose_horse(horse_name)
                        entrant_id = self.database.impose_entrant(horse_id,race_id,entrant['scratched'])
                        
                        self.database.impose_odds(entrant_id,platform_id,entrant['odds'])
                        
                        if (entrant['scratched']):
                            scratched_horses[str(entrant_id)] = 1
                        if not str(race_id) in date_race_store:
                            date_race_store[str(race_id)] = [race['start_time']]
                        else:
                            date_race_store[str(race_id)].append(race['start_time'])
            
            for race_id,date_list in date_race_store.items():
                date_occurence = {}
                for date in date_list:
                    if not date in date_occurence:
                        date_occurence[date] = 1
                    else:
                        date_occurence[date] += 1
                frequent_date = None
                frequency = 0
                for date,date_frequency in date_occurence.items():
                    if frequent_date == None or date_frequency > frequency:
                        frequency = date_frequency
                        frequent_date = date
                self.database.correct_race_start_time(race_id,frequent_date)
            self.database.closeConnection()
        except Exception as e:
            print(e)
            self.database.closeConnection()
