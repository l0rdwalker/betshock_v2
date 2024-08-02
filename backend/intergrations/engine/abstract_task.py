from abc import ABC, abstractmethod
import os
from datetime import datetime,timedelta,timezone
import dataManagement
from ..connection_handler.hydra import hydra

class task(ABC):
    def __init__(self,attributes,database,router) -> None:
        self.platformName = attributes[0]
        self.sport = attributes[1]
        self.operation = None
        self.next_run_time = datetime.now().astimezone(timezone.utc)
        
        self.database = database
        self.router:hydra = router
    
    @abstractmethod
    def init(self,data=None):
        pass
    
    @abstractmethod
    def get_next_run(self):
        pass
    
    def get_function_config(self):
        return {
            'operation':self.operation,
            'sport':self.sport,
            'driver':self
        }
    
    def local_print(self,msg:str):
        print(f"{self.platformName}:{msg}")
        