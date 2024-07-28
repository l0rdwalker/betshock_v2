from abc import ABC, abstractmethod
import os
from datetime import datetime,timedelta
import dataManagement
from abstract_task import task

class scraper(task):
    def __init__(self,attributes) -> None:
        super().__init__(attributes)
        self.operation = 'scrape'
        self.flex_dates = False
        
        self.next_run_procedure = None
        
    def get_function_config(self):
        return {
            'flex_dates':self.flex_dates
        }
                    
    def init(self,data):
        try:
            data = self.aquireOdds(data)
            if self.next_run_procedure == None:
                self.establish_next_run(data)
        except Exception as e:
            self.next_run_time = datetime.now() + timedelta(hours=1) 
            print(f"""{self.platformName}: {e}""")
        finally:
            return {'data':data, 'platform': self.platformName, 'sport': self.sport}
    
    def get_flex_date_status(self):
        return self.flex_dates
    
    def get_next_run(self):
        return self.next_run_time
        
    def establish_next_run(self,data):
        curr_date = datetime.now()
        if data == None:
            return curr_date + timedelta(hours=1) 
        
        next_race = None
        for race in data:
            race_start_time_obj = datetime.strptime(race['start_time'], '%Y-%m-%dT%H:%M:%S')
            if next_race == None:
                next_race = race_start_time_obj
                continue
            if race_start_time_obj > curr_date:
                if race_start_time_obj < next_race:
                    next_race = race_start_time_obj
        if next_race == None:
            self.next_run_time = None
        else:
            self.next_run_time = next_race + timedelta(minutes=5)
        
    @abstractmethod
    def aquireOdds(self):
        pass
    
    