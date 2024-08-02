import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arbie.sports.database.databaseOperations import databaseOperations
from arbie.sports.arbie_updateFocus import arbie_updateFocus
from multiTask_common import multitask_common
from better import better
from datetime import datetime, timedelta, timezone

class betters(multitask_common):
    def __init__(self,attributes,scraping_functions,database,router) -> None:
        super().__init__(attributes,database,router)
        
        better_configs = self.database.get_better_configs()
        if len(better_configs) > 0:
            for indiv_better in better_configs:
                better_instance = better(attributes,database,router,self,indiv_better)
                for function in scraping_functions:
                    better_instance.add_function(function,None)
            self.add_function(better_instance,datetime.now().astimezone(timezone.utc))
                    
    def configure_next_run(self):
        self.next_run = datetime.now() + timedelta(seconds=1)
    
    def init(self,data=None):
        ######Does some general state managerment######
        pass
    
    def triggerDriver(self,dummy_param):
        pass
    
    def trigger_post_scrape():
        pass