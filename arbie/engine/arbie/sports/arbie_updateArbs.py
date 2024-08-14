import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_task import task


class arbie_updateArbs(task):
    def __init__(self, attributes, database, router) -> None:
        super().__init__(attributes, database, router)
        self.operation = 'arbUpdate'
        
    def get_next_run(self):
        return datetime.now()
        
    def init(self, update_data=None) -> None:
        date_race_store = {}
        scratched_horses = {}
        
        for class_data in update_data:
            print('epic')
            pass
            
            
            
            #for platform in update_data:
            #    platform_id = self.database.impose_platform(platform['platform'])
            #    if platform['data'] == None:
            #        continue
            #    for race in platform['data']:
            #        track_id = self.database.impose_track(race['name'])
            #        race_id = self.database.impose_race(track_id,race['start_time'],race['round'])
            #        self.database.impose_platform_race_identifyer(race['race_id'],platform['platform'],race_id)
            #        existing_entrant_ids_set = set()
            #        existing_entrant_ids_list = self.database.get_race_entrant_ids(race_id)
            #        for entrant in existing_entrant_ids_list:
            #            existing_entrant_ids_set.add(entrant[0])
            #        construct_entrant_set = set()
            #        for entrant in race['entrants']:
            #            horse_name = entrant['name'].replace("'","").strip().lower()
            #            horse_id = self.database.impose_horse(horse_name)
            #            entrant_id = self.database.impose_entrant(horse_id,race_id,entrant['scratched'])
            #            construct_entrant_set.add(entrant_id)
            #            self.database.impose_odds(entrant_id,platform_id,entrant['odds'],entrant['record_time'])
            #            if not str(entrant_id) in scratched_horses:
            #                scratched_horses[str(entrant_id)] = {'scratched':0,'not_scratched':0}
            #            if entrant['scratched']:
            #                scratched_horses[str(entrant_id)]['scratched'] += 1
            #            else:
            #                scratched_horses[str(entrant_id)]['not_scratched'] += 1
            #            if not str(race_id) in date_race_store:
            #                date_race_store[str(race_id)] = [race['start_time']]
            #            else:
            #                date_race_store[str(race_id)].append(race['start_time'])
            #        for entrant_id in existing_entrant_ids_set:
            #            if not entrant_id in construct_entrant_set:
            #                self.database.delete_by_entrant_id(entrant_id)
            
            self.correct_race_start_time(date_race_store)
            self.correct_scratched(scratched_horses)
        
    def correct_scratched(self,scratched_horses):
        for entrant_id,value in scratched_horses.items():
            if value['scratched'] > value['not_scratched']:
                self.database.update_scratched(entrant_id,1)
            else:
                self.database.update_scratched(entrant_id,0)
        
    def correct_race_start_time(self,date_race_store):
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