import sys
import concurrent.futures
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abstract_platform import platformManager
from alive_progress import alive_bar
from datetime import datetime,timedelta,timezone
import pytz
import json
import threading
import math
from multiTask_common import multitask_common

class get_market_context(multitask_common):
    def __init__(self, attributes, database, router) -> None:
        super().__init__(attributes, database, router)
        
    def init(self,data=None):
        task_data = self.run_all_tasks(None)
        self.configure_next_run(None)
        self.push_to_database(task_data)
        
    def push_to_database(self,data):
        self.local_print("Uploading data to database")
        race_start_times = {}
        scratched_horses = {}
        
        for platform_data in data:
            for race in platform_data:
                platform_id = self.database.impose_platform(race['platform'])
                track_id = self.database.impose_track(race['name'])
                race_id = self.database.impose_race(track_id,race['start_time'],race['round'])
                self.database.impose_platform_race_identifyer(race['race_id'],race['platform'],race_id)
                for entrant in race['entrants']:
                    horse_name = entrant['name'].replace("'","").strip().lower()
                    horse_id = self.database.impose_horse(horse_name)
                    entrant_id = self.database.impose_entrant(horse_id,race_id,entrant['scratched'])
                    self.database.impose_odds(entrant_id,platform_id,entrant['odds'],entrant['record_time'])
                    
                    if not str(entrant_id) in scratched_horses:
                        scratched_horses[str(entrant_id)] = {'scratched':0,'not_scratched':0}
                    if entrant['scratched']:
                        scratched_horses[str(entrant_id)]['scratched'] += 1
                    else:
                        scratched_horses[str(entrant_id)]['not_scratched'] += 1
                    
                if not str(race_id) in race_start_times:
                    race_start_times[str(race_id)] = [race['start_time']]
                else:
                    race_start_times[str(race_id)].append(race['start_time'])

        self.correct_race_start_time(race_start_times)
        self.correct_scratched(scratched_horses)
        self.local_print("Finished uploading to database")

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
        
    def configure_next_run(self,data):
        self.local_print("Configuring when_next_run")
        current_time = datetime.now().replace(tzinfo=timezone.utc)
        
        smallest_timedelta = None
        for function in self.functions:
            desired_next_run:datetime = function[0]['driver'].get_next_run()
            desired_next_run = desired_next_run.replace(tzinfo=timezone.utc)
            if desired_next_run == None:
                continue
            timedelta_difference = desired_next_run - current_time
            if smallest_timedelta == None:
                smallest_timedelta = timedelta_difference
            elif timedelta_difference < smallest_timedelta:
                smallest_timedelta = timedelta_difference
            
        if not smallest_timedelta == None:
            self.next_run_time = current_time+smallest_timedelta
        else:
            sydney_tz = pytz.timezone('Australia/Sydney')
            utc_tz = pytz.utc
            sydney_time = current_time.astimezone(sydney_tz)
            sydney_time = sydney_time.replace(hour=5, minute=0, second=0, microsecond=0)
            sydney_time += timedelta(days=1)
            self.next_run_time = sydney_time.astimezone(utc_tz)
        self.local_print("Completed when_next_run")

        
    

