import sys
import concurrent.futures
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from abstract_platform import platformManager
from alive_progress import alive_bar
from datetime import datetime,timedelta,timezone
import json
from multiTask_common import multitask_common
from engine.arbie.sports.arbie_updateFocus import arbie_updateFocus
from arb_manager import arb_manager

class better(multitask_common):
    def __init__(self,attributes,database,router,betting_pool,identifyer) -> None:
        super().__init__(attributes,database,router)
        self.identidyer = identifyer
        self.betting_pool = betting_pool
        
        self.name = identifyer[0]
        self.race_id = identifyer[1]
        self.local_id = identifyer[2]
        
        self.all_functions = []
        self.api_links = {}
        
    def derive_identity(self):
        pass
    
    def collect_api_links(self):
        race_api_details = self.database.get_platform_api_links(self.race_id)
        for entry in race_api_details:
            self.api_links[entry[1]] = json.loads(entry[0])
    
    def activate_platform_watch(self):
        temp_functions = []
        for function in self.functions:
            if function[0]['platform'] in self.api_links:
                temp_functions.append((function[0],self.api_links[function[0]['platform']]))
        self.functions = temp_functions
    
    def init(self,data):
        self.configure_next_run(None)
        if self.race_id == None:
            identity = self.database.get_my_better_config(self.local_id)
            if identity == None:
                raise Exception("No matching better id")
            self.name = identity[0]
            self.race_id = identity[1]

        if not self.race_id == None:
            self.collect_api_links()
            self.activate_platform_watch()
            
            race_data = self.run_core_functions()
            self.update_datebase(race_data)
            race_data = self.run_post_tasks(race_data)
            self.configure_next_run(None)
        else:
            self.configure_next_run(None)
            raise Exception("No race associated with better.")
        
    def update_datebase(self,update_data):
        if not self.race_id == None:
            for platform in update_data:
                platform_name = platform['platform']
                for entrant in platform['data']:
                    horse_name = entrant['name'].replace("'","").strip().lower()
                    entrant_id = self.database.get_specific_entrant_id_by_name_and_race(self.race_id,horse_name) 
                    if not entrant_id == None:
                        self.database.impose_odds(entrant_id,platform_name,entrant['odds'],entrant['record_time'])
            
    def set_race_watch(self):
        races = self.database.get_future_races()
        possible_races = []
        for race in races:
            best_race_selections = self.calculate_best_arb(race[0])
            if not best_race_selections == None:
                possible_races.append(best_race_selections)
        possible_races = sorted(possible_races, key=lambda x: x['i_p'])
        return possible_races[0]
        
    def triggerDriver(self,driver,params):
        data = driver.get_race_by_id(params)
        return data
    
    def configure_next_run(self, data):
        self.next_run = datetime.now().astimezone(timezone.utc) + timedelta(seconds=5)

