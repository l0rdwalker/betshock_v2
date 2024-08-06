from abc import ABC, abstractmethod
import os
from datetime import datetime,timedelta,timezone
import dataManagement
import math
from abstract_task import task

class scraper(task):
    def __init__(self,attributes,database,router) -> None:
        super().__init__(attributes,database,router)
        self.operation = 'scrape'
        self.flex_dates = False
        
    def init(self,data):
        try:
            data = self.get_all_meets(data)
            self.configure_next_run(data)
        except Exception as e:
            self.next_run_time = datetime.now() + timedelta(hours=1) 
            print(f"""{self.platformName}: {e}""")
        finally:
            return data
        
    def configure_next_run(self, data):
        cur_time = datetime.now().astimezone(timezone.utc)
        closest_utc_date = None
        closest_utc_timedelta = None
        for race in data:
            race_start_time = datetime.strptime(race['start_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
            race_start_time = race_start_time.replace(tzinfo=timezone.utc)
            if race_start_time > cur_time:
                timedelta_difference = race_start_time-cur_time
                if closest_utc_timedelta == None:
                    closest_utc_timedelta = timedelta_difference
                    closest_utc_date = race_start_time
                elif closest_utc_timedelta < timedelta_difference:
                    closest_utc_timedelta = timedelta_difference
                    closest_utc_date = race_start_time
        if closest_utc_timedelta == None:
            self.next_run_time = None
        else:
            self.next_run_time = cur_time + timedelta(hours=2)
        
    @abstractmethod
    def get_all_meets(self,data):
        pass
    
    @abstractmethod
    def get_entrants(self, race_id):
        pass
        
    def get_function_config(self):
        return {
            'flex_dates':self.flex_dates
        }
        
    def get_race_by_id(self,race_id):
        data = self.get_entrants(race_id)
        if not data == None:
            if len(data) == 2:
                data = data[0]
        return {'data':data, 'platform': self.platformName, 'sport': self.sport}
        
    def create_race_entry(self,start_time:datetime,round:int,track_name:str,race_identifyer,entrants,platform=None):
        if platform == None:
            platform = self.platformName
        if isinstance(start_time,datetime):
            start_time = start_time.isoformat()
        return {'round':round, 'platform':platform, 'name': f'{track_name}', 'start_time': start_time,'entrants':entrants, 'race_id':race_identifyer}
    
    def create_entrant_entry(self,entrant_name,odds,scratched,record_time:datetime):
        return {'name':entrant_name,'odds':odds,'record_time':record_time.isoformat(),'scratched':scratched}
    