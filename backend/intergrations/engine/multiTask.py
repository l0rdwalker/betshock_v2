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
from multiTask_common import multitask_common

class multitask(multitask_common):
    def __init__(self, attributes, database) -> None:
        super().__init__(attributes, database)
    
    def triggerDriver(self,driver,params):
        data = driver.init(params)
        return data
    
    def trigger_post_scrape(self,postTask,data):
        postTask['driver'].init(data)
    
    def configure_next_run(self,data):
        current_time = datetime.now().astimezone(timezone.utc)
        current_time
        system_dates = []
        
        for platform_entry in data:
            for race in platform_entry['data']:
                time_instance = datetime.fromisoformat(race['start_time'])
                time_instance = time_instance.astimezone(timezone.utc)
                system_dates.append(time_instance)

        system_dates = sorted(system_dates)
        set_date = False
        for date in system_dates:
            time_difference = date - current_time
            time_dif_delt = timedelta(hours=1)
            if time_difference > timedelta(0):
                if time_difference < time_dif_delt:
                    self.next_run = current_time + timedelta(minutes=30)
                    set_date = True
                    break
        
        if set_date == False:
            for date in system_dates:
                if date > current_time:
                    self.next_run = date-timedelta(hours=1)
                    break
    

