from abc import ABC, abstractmethod
import os
from datetime import datetime,timedelta
import dataManagement

class task(ABC):
    def __init__(self,attributes) -> None:
        self.platformName = attributes[0]
        self.sport = attributes[1]
        self.operation = None
    
    @abstractmethod
    def init(self,data=None):
        pass
    
    @abstractmethod
    def whenNextRun(self):
        pass
        