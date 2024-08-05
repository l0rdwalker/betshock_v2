import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arb_manager import arb_manager
from abstract_task import task
from better import better
from datetime import datetime, timedelta, timezone

class race(task):
    def __init__(self,attributes,database,router) -> None:
        super().__init__(attributes,database,router)
        self.race_id = None
        self.start_time = None
        self.begin_watch = None
        
        self.is_active = False
        self.shut_down = False
        
        self.odds_manager = arb_manager()  
        
    def force_race_clear(self):
        self.race_id = None
        self.race_platform_ids = []
        self.start_time = None
        self.begin_watch = None
        
        #Perform an exiting state update to the database
        
        self.odds_manager.clear_arb()
    
    def set_race(self,data=None):
        if not self.race_id == None:
            raise Exception('A race has already been configured')
        if data == None:
            raise Exception('No race config was provided')

        self.race_id = data['race_id']
        self.race_platform_ids = data['platform_ids'] 
        self.start_time = data['start_time']
        self.begin_watch = data['start_watch']
        
        self.odds_manager.clear_arb()
        
    def looper(self):
        while self.shut_down == False:
            if not self.race_id == None:
                continue
    
    def configure_next_run(self):
        self.next_run = datetime.now() + timedelta(seconds=1)