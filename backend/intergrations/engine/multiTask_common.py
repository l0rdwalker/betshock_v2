import sys
from abc import ABC, abstractmethod
import concurrent.futures
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abstract_platform import platformManager
from alive_progress import alive_bar
from abstract_task import task
from datetime import datetime,timedelta,timezone

class multitask_common(task):
    def __init__(self,attributes,database,router) -> None:
        super().__init__(attributes,database,router)
        self.functions = []
        self.postTasks = []
        
        self.operation = 'multiTask'
        self.name = 'Arbie'
        self.next_run = datetime.now(timezone.utc)
        
    def add_function(self,function:task,function_parameter=None):
        self.functions.append([function,function_parameter])
        
    def add_post_task(self,post_task):
        self.postTasks.append(post_task)
        
    def run_core_functions(self,task_param=None):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.functions)) as executor:
            tasks = []
            for task_idx in range(0,len(self.functions)):
                tasks.append((self.functions[task_idx][0]['driver'],self.functions[task_idx][1]))
            data = list(executor.map(lambda args: self.triggerDriver(*args),tasks))
        return data
        
    def run_post_tasks(self,task_param):
        for postTask in self.postTasks:
            return_data = postTask['driver'].init(task_param)
            if not return_data == None:
                task_param = return_data
        return task_param
    
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
    def init(self,data=None):
        pass
    
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
    

