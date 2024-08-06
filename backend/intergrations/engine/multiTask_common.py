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
        self.operation = 'multiTask'
        self.name = 'Arbie'

    def run_all_tasks(self,data=None):
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(self.functions)) as executor:
            tasks = []
            for task_idx in range(0,len(self.functions)):
                tasks.append((self.functions[task_idx][0]['driver'],self.functions[task_idx][1]))
            data = list(executor.map(lambda args: args[0].init(args[1]), tasks))
        return data
    
    def add_function(self,function:task,function_parameter=None):
        self.functions.append([function,function_parameter])
    
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
    

