import sys
import concurrent.futures
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abstract_platform import platformManager
from alive_progress import alive_bar
from datetime import datetime,timedelta,timezone
import json
import threading
from arbie.sports.database.databaseOperations import databaseOperations
from multiTask_common import multitask_common

from arb_manager import arb_manager

class better(multitask_common):
    def __init__(self,attributes,database,identifyer) -> None:
        super().__init__(attributes,database)
        self.identidyer = identifyer
        #if race_id == None:
        #    self.best_selections = self.set_race_watch()
        #    self.race_id = self.best_selections['race_id']
        #else:
        #    self.race_id = race_id
        #self.api_links = {}
        
    def derive_identity(self):
        pass
    
    def collect_api_links(self):
        race_api_details = self.database.get_platform_api_links(self.race_id)
        for entry in race_api_details:
            self.api_links[entry[1]] = json.loads(entry[0])
    
    def activate_platform_watch(self):
        temp_functions = []
        for function in self.all_functions:
            if function[0]['platform'] in self.api_links:
                temp_functions.append((function[0],self.api_links[function[0]['platform']]))
        self.functions = temp_functions
    
    def init(self,data):
        self.collect_api_links()
        self.activate_platform_watch()
        
        data = super().init(data)
            
    def set_race_watch(self):
        races = self.database.get_future_races()
        possible_races = []
        for race in races:
            best_race_selections = self.calculate_best_arb(race[0])
            if not best_race_selections == None:
                possible_races.append(best_race_selections)
        possible_races = sorted(possible_races, key=lambda x: x['i_p'])
        return possible_races[0]
        
    def trigger_post_scrape(self,postTask,data):
        postTask['driver'].init(data,self.race_id)
        
    def triggerDriver(self,driver,params):
        data = driver.get_race_by_id(params)
        return data
    
    def configure_next_run(self, data):
        self.next_run = datetime.now().astimezone(timezone.utc) + timedelta(seconds=5)

