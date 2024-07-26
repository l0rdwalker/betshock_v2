import sys
import concurrent.futures
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abstract_platform import platformManager
from alive_progress import alive_bar
from datetime import datetime,timedelta
import json
import threading

class multitask(platformManager):
    def __init__(self,functions:list,postTasks=[]) -> None:
        self.functions = functions
        self.postTasks = postTasks
        
        self.threads = []
        self.operation = 'multiTask'
        self.name = 'Arbie'
        self.next_run = datetime.now()
        
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
        
        self.configure_next_run()
        
        return data
    
    def get_next_run(self):
        return self.next_run
    
    def configure_next_run(self):
        try:
            min_date = None
            max_date = None
            for function in self.functions:
                curr_date = function[0]['driver'].get_next_run()
                if curr_date == None:
                    curr_date = max_date
                if min_date == None or max_date == None:
                    min_date = curr_date
                    max_date = curr_date
                    continue
                if curr_date > max_date:
                    max_date = curr_date
                if curr_date < min_date:
                    min_date = curr_date
            curr_date = datetime.now()
            if min_date < curr_date < max_date:
                self.next_run = curr_date + timedelta(minutes=5)
            elif min_date > curr_date:
                self.next_run = min_date - timedelta(minutes=5)
            else:
                tomorrow = curr_date + timedelta(days=1)
                tomorrow_at_6_am = tomorrow.replace(hour=6, minute=0, second=0, microsecond=0)
                self.next_run = tomorrow_at_6_am
        except Exception as e:
            print(f'Multi-task: {e}')
            self.next_run = datetime.now() + timedelta(minutes=5)
    
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
    

