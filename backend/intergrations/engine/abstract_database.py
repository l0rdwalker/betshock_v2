from abc import ABC, abstractmethod
import os
from datetime import datetime,timedelta
import dataManagement
from abstract_task import task

class database(task):
    def __init__(self,attributes) -> None:
        super().__init__(attributes)
        self.operation = 'database'
    
    @abstractmethod
    def init(self,data=None):
        pass
    
    def whenNextRun(self):
        return datetime.now()+timedelta(hours=1)
        