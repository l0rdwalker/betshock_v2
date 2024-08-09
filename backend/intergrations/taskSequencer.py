import os
import json
import dataManagement as dm
from connection_handler.hydra import hydra
from datetime import datetime, timedelta, timezone
from priorityQueue import queue
from engine.better import better
from threading import Thread, Lock
import threading
from engine.arbie.sports.database.databaseOperations import databaseOperations


class taskSchedular:
    def __init__(self,max_threads=3,utx_offset=10) -> None:
        self.file = os.path.dirname(os.path.abspath(__file__))
        
        self.max_threads = max_threads
        self.lock = Lock()
        self.threads = []
        
        self.tasks = []
        self.functions = []
        
        self.currentDatetime = datetime.now()
        self.utc_hours_offset = utx_offset #set to sydney local time
        
        self.database = databaseOperations()
        self.database.initConnection()
        self.router = hydra()

        self.log('Initalizeing task schedular')
        sportObjectsDir = os.path.join(self.file,'engine')
        for platform in [entry for entry in os.listdir(sportObjectsDir) if os.path.isdir(os.path.join(sportObjectsDir,entry))]:
            try:
                platformDriver = dm.getModuleByPath(os.path.join(sportObjectsDir,platform),platform,self.database,self.router)
                for function in platformDriver.getFunctions():
                    self.functions.append(function)
                self.log(f'Successfully imported {platform} dependencys')
            except Exception as e:
                self.log(e)
                
    def enqueue(self,function,run_time=datetime.now().astimezone(timezone.utc)):
        with self.lock:
            self.tasks.append((run_time,function.returnFunctionConfig()))
        
    def enqueue_embedded_runtime(self,function_with_runtime):
        with self.lock:
            self.tasks.append((function_with_runtime[1],function_with_runtime[0].returnFunctionConfig()))
        
    def get_database_obj(self):
        return self.database
    
    def get_router_obj(self):
        return self.router

    def init(self) -> None:
        self.threads = []
        for _ in range(self.max_threads):
            thread = Thread(target=self.allocate_tasks,args=())
            thread.start()
            self.threads.append(thread)
        for thread in self.threads:
            thread.join()
                
    def allocate_tasks(self):
        while True:
            self.currentDatetime = datetime.now().astimezone(timezone.utc)
            
            task_to_run = None
            with self.lock:
                self.tasks = sorted(self.tasks, key=lambda x: x[0])
                if len(self.tasks) > 0:
                    if self.currentDatetime > self.tasks[0][0]:
                        task_to_run = self.tasks.pop(0)[1]
            
            if not task_to_run == None:
                next_run = self.perform_task(task_to_run)
                with self.lock:
                    self.tasks.append((next_run,task_to_run))
            
    def perform_task(self,current_task):
        #try:
        self.log(f"starting {current_task['type']} on {current_task['platform']}.")
        current_task['driver'].init(current_task['data'])
        self.log(f"{current_task['type']} on {current_task['platform']} succeeded.")
        #except Exception as e:
        #    self.log(e,error=True)
        #    self.log(f"{current_task['type']} on {current_task['platform']} failed.",error=True)
        return current_task['driver'].get_next_run()

    def contains_key(self,key_value,search_data):
        match_status = False
        for key,value in search_data.items():
            if match_status:
                return match_status
            if isinstance(value, dict):
                match_status = self.contains_key(key_value,value)
            elif key_value[0] == key and key_value[1] == value:
                match_status = True
        return match_status
            
    def searchFunctions(self,data,searchData=None):
        if searchData == None:
            searchData = self.functions
        
        if len(data) > 0:
            for key,item in data.items():
                key_data = (key,item)
                data.pop(key)
                break
            
            releventFunctions = []
            for function in searchData:
                if self.contains_key(key_data,function):
                    releventFunctions.append(function)
            return self.searchFunctions(data,releventFunctions)
        else:
            return searchData
        
    def getFunctions(self):
        return self.functions

    def log(self,message,error=False):
        blackCode = '\033[0m'
        colorCode = blackCode
        if error:
            colorCode = '\033[91m'

        message = str(message)
        message = message.replace("\n","")
        self.clock = datetime.now()

        strDate = f'{self.clock.day}_{self.clock.month}_{self.clock.year}'
        strDateTime = f'{strDate}:{self.clock.hour}_{self.clock.minute}_{self.clock.second}'
        message = f'{strDateTime}: {message}'

        self.logDir = os.path.join(self.file,'logs')
        self.dayLog = os.path.join(self.logDir,f'{strDate}.txt')
        dm.writeFile(self.dayLog,message)

        print(f'{colorCode}{message}{blackCode}\n',end=" ")
