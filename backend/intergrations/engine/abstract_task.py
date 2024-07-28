from abc import ABC, abstractmethod
import os
from datetime import datetime,timedelta,timezone
import dataManagement

class task(ABC):
    def __init__(self,attributes) -> None:
        self.platformName = attributes[0]
        self.sport = attributes[1]
        self.operation = None
        self.next_run_time = datetime.now().astimezone(timezone.utc)
    
    @abstractmethod
    def init(self,data=None):
        pass
    
    @abstractmethod
    def get_next_run(self):
        pass
    
    @abstractmethod
    def get_function_config():
        pass
    
    def local_print(self,msg:str):
        print(f"{self.platformName}:{msg}")
        