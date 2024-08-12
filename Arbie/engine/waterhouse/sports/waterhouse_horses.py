import requests
import json
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import pytz
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class waterhouse_horses(scraper):
    def __init__(self,attributes,database,router) -> None:
        super().__init__(attributes,database,router)
        self.flex_dates = True

    def get_race_meets(self,date_obj:datetime):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'client-brand': 'WAT',
            'dnt': '1',
            'locale': 'en',
            'origin': 'https://robwaterhouse.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://robwaterhouse.com/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'website-version': '31.21.30.1',
        }

        params = {
            'date': date_obj.strftime('%Y-%m-%d')
        }

        
        response = self.router.perform_get_request(
            self.platformName,
            'https://api.robwaterhouse.com/api/v2/combined/meetings/races',
            params,
            headers
        )

        return response

    def get_race_card(self,race_id):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'client-brand': 'WAT',
            'dnt': '1',
            'locale': 'en',
            'origin': 'https://robwaterhouse.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://robwaterhouse.com/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'website-version': '31.21.30.1',
        }

        params = {
            'race_id': f'{race_id}',
        }

        response = self.router.perform_get_request(
            platform=self.platformName,
            url='https://api.robwaterhouse.com/api/v2/combined/race/selections',
            params=params,
            headers=headers
        )
        
        return response


    def get_all_meets(self,datetime_param:datetime):
        curr_time = datetime.now()
        if isinstance(datetime_param,datetime):
            curr_time += datetime_param
            
        sydney_tz = pytz.timezone('Australia/Sydney')
        utc_tz = pytz.utc
        
        race_profile = []
        meets = self.get_race_meets(curr_time)['data']
        for meet in meets:
            if not meet['country'] == 'AU':
                continue
            
            LOC:str = meet['name']
            LOC = LOC.split(" ")
            NEW_LOC = []
            for txt in LOC:
                txt = list(txt.lower())
                txt[0] = txt[0].upper()
                txt = ''.join(txt)
                NEW_LOC.append(txt)
            LOC = ' '.join(NEW_LOC)    
                
            for race in meet['races']:
                if not 'gallops' in race['race_site_link']:
                    break
                race_identifyer = {'race_id':race['id']}
                
                START_TIME = datetime.strptime(race['start_date'], '%Y-%m-%d %H:%M:%S')
                
                entrants = self.get_entrants(race_identifyer)
                race_profile.append(self.create_race_entry(START_TIME,race['number'],LOC,race_identifyer,entrants))
        return race_profile     
                
    def get_entrants(self,race_identifyer):
        race_card = self.get_race_card(race_identifyer['race_id'])
        record_time = datetime.now()
        entrants = []
        for entrant in race_card['data']['selections']:
            try:
                NAME = entrant['name']
                ODDS = -1
                if len(entrant['prices']) > 1:
                    if isinstance(entrant['prices'],list):
                        ODDS = entrant['prices'][0]['win_odds']
                    else:
                        ODDS = entrant['prices']['0']['win_odds']
                entrants.append(self.create_entrant_entry(NAME,ODDS,(not entrant['scratching_time']==None),record_time.isoformat()))
            except Exception as e:
                continue
        return entrants