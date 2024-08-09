import requests
import json
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class racenet_horses(scraper):
    def __init__(self, attributes, database, router) -> None:
        super().__init__(attributes, database, router)
        self.flex_dates = True
    
    def get_bookmaker_prices(self,market_id):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'dnt': '1',
            'origin': 'https://www.racenet.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.racenet.com.au/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }

        response = self.router.perform_get_request(
            platform=self.platformName,
            url=f'https://puntapi.com/odds/au/event/{market_id}?betTypes=fixed-win,tote-win,exchange-win,exchange-win-lay&priceFluctuations=50&type=best,bookmaker&bookmaker=ubet,sportsbet,bet365,betm,ladbrokes,betfair,betfair,boombet,tabtouch,pointsbet,neds',
            headers=headers,
            params=None
        )
        
        return response
        
    def get_race_card(self,race_id):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'authorization': 'Bearer none',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://www.racenet.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.racenet.com.au/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }
        params = {
            'operationName': 'eventById',
            'variables': '{"eventId":"'+race_id+'"}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"0029451798d3780a964eef179e79ddad1f1074c93038774ec8626b8b22999e6d"}}',
        }
        
        response = self.router.perform_get_request(
            self.platformName,
            url='https://puntapi.com/graphql-horse-racing', 
            params=params, 
            headers=headers
        )
        
        return response
        
    def get_day_races(self,current_day_obj:datetime):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'authorization': 'Bearer none',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://www.racenet.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.racenet.com.au/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }
        current_day_obj = current_day_obj.replace(hour=0,minute=0,second=0,microsecond=0)
        str_date_start:str = current_day_obj.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        
        shift_24_hours = current_day_obj + timedelta(days=1)
        str_date_end:str = shift_24_hours.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        params = {
            'operationName': 'meetingsIndexByStartEndTime',
            'variables': '{"startTime":"'+str_date_start+'","endTime":"'+str_date_end+'","limit":100,"sportIds":1}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"b8b5bef7544da6d9bc3f601bf6e030a3de79ca24e168186b110692a4302bcbfb"}}',
        }
        response = self.router.perform_get_request(
            platform=self.platformName,
            url='https://puntapi.com/graphql-horse-racing',
            params=params,
            headers=headers
        )

        return response

    def get_all_meets(self,race_date_obj:timedelta):
        curr = datetime.now()
        if isinstance(race_date_obj, timedelta):
            curr += race_date_obj
            
        race_profile = []
        for x in range(0,5):
            try:
                meets = self.get_day_races(curr)
                meets = meets['data']['meetingsGrouped']
                break
            except Exception as e:
                self.local_print(f"Was no able to pull data. Attempt {x+1}")
                if x+1 >= 5:
                    return race_profile
            
        for entry in meets:
            if entry['group'] == 'Australia':
                meets = entry
                break
        for meet in meets['meetings']:
            LOC = meet['name']
            for race in meet['events']:
                ROUND = race['eventNumber']
                START_TIME = datetime.strptime(race['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                
                race_id = {'race_id':race['id'],'start_time':START_TIME.isoformat(),'round':ROUND,'name':LOC}
                
                ENTRANTS = self.get_entrants(race_id)
                race_profile.extend(ENTRANTS)
        
        return race_profile

    def get_entrants(self,race_identifyer):
        dist_to_list = []
        
        try:
            platform_entrants = self.get_race_card(race_identifyer['race_id'])
            platform_prices = self.get_bookmaker_prices(race_identifyer['race_id'])
            record_time = datetime.now()        
            
            name_id_cache = {}
            platform_entrants = platform_entrants['data']['event']['selections']
            for entrant in platform_entrants:
                name_id_cache[entrant['id']] = {'name':entrant['competitor']['name'],'scratched':entrant['status']=='SCRATCHED'}
            
            platform_name_memoization = {}
            platform_offerings = {}
            for price in platform_prices['odds']:
                if price['betType'] == 'fixed-win':
                    entrant = self.create_entrant_entry(
                            entrant_name=name_id_cache[str(price['selectionId'])]['name'],
                            odds=price['price']['value'],
                            scratched=name_id_cache[str(price['selectionId'])]['scratched'],
                            record_time=record_time
                        )
                    if not price['bookmakerId'] in platform_name_memoization:
                        platform_name_memoization[price['bookmakerId']] = set()
                    
                    if not str(price['selectionId']) in platform_name_memoization[price['bookmakerId']]:
                        if not price['bookmakerId'] in platform_offerings:
                            platform_offerings[price['bookmakerId']] = [entrant]
                        else:
                            platform_offerings[price['bookmakerId']].append(entrant)
                        platform_name_memoization[price['bookmakerId']].add(str(price['selectionId']))

                        
            for key, entry in platform_offerings.items():
                race_entry = self.create_race_entry(
                    race_identifyer=race_identifyer,
                    track_name=race_identifyer['name'],
                    round=race_identifyer['round'],
                    start_time=race_identifyer['start_time'],
                    entrants=entry,
                    platform=key
                )
                dist_to_list.append(race_entry)
        except:
            return dist_to_list   
        return dist_to_list