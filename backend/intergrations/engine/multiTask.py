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
        self.nextScheduledRun = datetime.now()
        
    def triggerDriver(self,driver,params,updater):
        data = driver.init(params)
        updater()
        return data
        
    def init(self,data):
        with alive_bar(len(self.functions)) as bar:
            data = self.runTaks(updater=bar)
    
        smallest = datetime.now()+timedelta(days=1)
        smallest = smallest.replace(hour=6,minute=0,second=0,microsecond=0)
        for function in self.functions:
            try:
                if function['driver'].whenNextRun() < smallest:
                    smallest = function['driver'].whenNextRun()
            except:
                continue
        self.nextScheduledRun = smallest
        
        for postTask in self.postTasks:
            postTask['driver'].init(data)
        
        return data
        
    def whenNextRun(self):
        return self.nextScheduledRun
    
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
    

