import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arbie.sports.database.databaseOperations import databaseOperations
from multiTask_common import multitask_common
from better import better

class betters(multitask_common):
    def __init__(self,attributes,scraping_functions,database) -> None:
        super().__init__(attributes,database)
        
        better_configs = self.database.get_better_configs()
        if len(better_configs) > 0:
            for indiv_better in better_configs:
                better_instance = better(attributes,database,indiv_better)
                for function in scraping_functions:
                    better_instance.add_function(function,None)
            self.add_function(better_instance,None)
                    
    def configure_next_run():
        pass
    
    def triggerDriver():
        pass
    
    def trigger_post_scrape():
        pass