import sys
from abc import ABC, abstractmethod
import concurrent.futures
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abstract_platform import platformManager
from alive_progress import alive_bar
from datetime import datetime,timedelta,timezone
import json
import threading

class multitask_common(platformManager):
    def __init__(self,functions:list,postTasks=[]) -> None:
        self.functions = functions
        self.postTasks = postTasks
        
        self.threads = []
        self.operation = 'multiTask'
        self.name = 'Arbie'
        self.next_run = datetime.now(timezone.utc)
    
    @abstractmethod
    def triggerDriver(self,driver,params,updater):
        data = driver.init(params)
        updater()
        return data
    
    @abstractmethod
    def configure_next_run(self,data):
        pass
    
    def get_next_run(self):
        return self.next_run
    
    @abstractmethod
    def trigger_post_scrape(self,postTask,data):
        pass
    
    def init(self,data=None):
        with alive_bar(len(self.functions)) as bar:
            data = self.runTaks(updater=bar)
                
        for postTask in self.postTasks:
            return_data = self.trigger_post_scrape(postTask,data)
            if not return_data == None:
                data = return_data
        
        self.configure_next_run(data)
        
        return data

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
        self.platform_name = 'arbie'
    

