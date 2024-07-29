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

class better(multitask_common):
    def __init__(self,functions:list,postTasks=[]) -> None:
        super().__init__(functions,postTasks)
        self.all_functions = functions
        
        self.database = databaseOperations()
        self.race_id = None
        self.api_links = {}
        
        self.best_selections = self.set_race_watch()
        self.race_id = self.best_selections['race_id']
    
    def collect_api_links(self):
        self.database.initConnection()
        race_api_details = self.database.get_platform_api_links(self.race_id)
        for entry in race_api_details:
            self.api_links[entry[1]] = json.loads(entry[0])
        self.database.closeConnection()
    
    def calculate_best_arb(self,race_id):
        opened_new_connection = False
        if self.database.connection_open == False:
            self.database.initConnection()
            opened_new_connection = True
        
        i_p = 0
        entrant_selections = []
        entrants = self.database.get_race_entrant_ids(race_id)
        for entrant in entrants:
            if self.database.is_imposed(entrant[0]):
                continue
            best_odds = 0
            best_platform = None
            platform_offerings = self.database.get_entrant_platform_offerings(entrant[0])
            for platform in platform_offerings:
                prices = self.database.get_entrant_odds_by_platform(entrant[0],platform[0])
                if (best_platform == None or prices[0][0] > best_odds) and not prices[0][0] == 0:
                    best_platform = platform[0]
                    best_odds = prices[0][0]
            if not best_platform == None:
                entrant_selections.append({'platform':best_platform,'entrant_id':entrant[0],'horse_name':entrant[1],'odds':best_odds,'i_p':1/best_odds})
                i_p += 1/best_odds
            else:
                i_p += 1
            
        if opened_new_connection:
            self.database.closeConnection()
        return {'race_id':race_id,'entrants':entrant_selections,'i_p':i_p}
    
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
        self.database.initConnection()
        
        races = self.database.get_future_races()
        possible_races = []
        for race in races:
            best_race_selections = self.calculate_best_arb(race[0])
            possible_races.append(best_race_selections)
        possible_races = sorted(possible_races, key=lambda x: x['i_p'])
        
        self.database.closeConnection()
        return possible_races[0]
        
    def trigger_post_scrape(self,postTask,data):
        postTask['driver'].init(data,self.race_id)
        
    def triggerDriver(self,driver,params,updater):
        data = driver.get_race_by_id(params)
        updater()
        return data
    
    def configure_next_run(self, data):
        self.next_run = datetime.now().astimezone(timezone.utc) + timedelta(seconds=5)

