import sys
import concurrent.futures
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abstract_platform import platformManager
from alive_progress import alive_bar
from datetime import datetime,timedelta,timezone
import json
import threading

class multitask(platformManager):
    def __init__(self,functions:list,postTasks=[]) -> None:
        self.functions = functions
        self.postTasks = postTasks
        
        self.threads = []
        self.operation = 'multiTask'
        self.name = 'Arbie'
        self.next_run = datetime.now(timezone.utc)
        
    def triggerDriver(self,driver,params,updater):
        data = driver.init(params)
        updater()
        return data
        
    def init(self,data=None):
        with alive_bar(len(self.functions)) as bar:
            data = self.runTaks(updater=bar)
                
        for postTask in self.postTasks:
            return_data = postTask['driver'].init(data)
            if not return_data == None:
                data = return_data
        
        self.configure_next_run(data)
        
        return data
    
    def get_next_run(self):
        return self.next_run
    
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
                    self.next_run = current_time + timedelta(minutes=5)
                    set_date = True
                    break
        
        if set_date == False:
            for date in system_dates:
                if date > current_time:
                    self.next_run = date-timedelta(hours=1)
                    break

    def runTaks(self,updater):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.functions)) as executor:
            tasks = []
            for task_idx in range(0,len(self.functions)):
                tasks.append((self.functions[task_idx][0]['driver'],self.functions[task_idx][1],updater))
            results = list(executor.map(lambda args: self.triggerDriver(*args),tasks))
        return results
    
    def getFunctions(self):
        return self.functions
    
    def returnFunctionConfig(self):
        return (
            {                                
                'driver':self,
                'platform':self.name,
                'type':self.operation,
                'data':{}
            }
        )
    
    def setPlatformName(self):
        self.name = 'All Platforms - Horces'
    

