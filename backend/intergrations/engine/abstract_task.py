from abc import ABC, abstractmethod
import os
from datetime import datetime,timedelta,timezone
import dataManagement
from arbie.sports.database.databaseOperations import databaseOperations

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from connection_handler.hydra import hydra

class task(ABC):
    def __init__(self,attributes,database,router) -> None:
        self.platformName = attributes[0]
        self.sport = attributes[1]
        self.operation = None
        self.next_run_time = datetime.now().astimezone(timezone.utc)
        
        self.database:databaseOperations = database
        self.router:hydra = router
    
    def set_operation_name(self,name:str):
        self.operation = name
    
    def get_operaton_name(self):
        return self.operation
        
    @abstractmethod
    def configure_next_run(self,data):
        pass

    def get_next_run(self):
        return self.next_run_time
    
    @abstractmethod
    def init(self,data=None):
        pass
    
    def get_function_config(self):
        return {
            'operation':self.operation,
            'sport':self.sport,
            'driver':self
        }
    
    def local_print(self,msg:str):
        print(f"{self.platformName}: {msg}")
        