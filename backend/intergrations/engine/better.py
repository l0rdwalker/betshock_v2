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

class better():
    def __init__(self,database,router,name) -> None:
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.credentials_dir = os.path.join(self.current_dir,'creds')
        self.user_creds_dir = os.path.join(self.credentials_dir,f"{name}.json")
        
        if not os.path.isfile(self.user_creds_dir):
            raise Exception('Bad credientials')
        
    def get_balence(self,platform):
        pass
    
    def place_bet(self):
        pass
    
    def get_current_bets(self):
        pass
