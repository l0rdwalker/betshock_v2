import requests
import json
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class playup_horses(scraper):
    def __init__(self, attributes) -> None:
        super().__init__(attributes)
        self.flex_dates = True
    
    def get_meets(self,date:datetime):
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'apptoken': 'cxp-desktop-web',
            'channel': 'cxp',
            'content-type': 'application/json',
            'dnt': '1',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-request-id': '082433eeb73549c88eee139fa1a8599e',
        }

        response = requests.get(
            f'https://www.sportsbet.com.au/apigw/sportsbook-racing/Sportsbook/Racing/AllRacing/{date.strftime("%Y-%m-%d")}',
            headers=headers,
        )
        return json.loads(response.text)

    def get_race_card(self,id):
        headers = {
            'accept': 'application/json',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'apptoken': 'cxp-desktop-web',
            'channel': 'cxp',
            'content-type': 'application/json',
            'dnt': '1',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        params = {
            'classId': '1',
        }

        response = requests.get(
            f'https://www.sportsbet.com.au/apigw/sportsbook-racing/{id}',
            params=params,
            headers=headers,
        )
        response = response.text
        return json.loads(response)
    
    def convertTime(self,data):
        startTime = datetime.fromtimestamp(data, tz=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime    

    def aquireOdds(self,race_date_obj:timedelta):
        raceData = []
        set_date = datetime.now()
        if isinstance(race_date_obj,timedelta):
            set_date += race_date_obj
        
        meets = self.get_meets(set_date)
        
        for date in meets['dates']:
            for sport in date['sections']:
                if sport['displayName'] == "Horses":
                    meets = sport
                    break
            break
        
        for meet in meets['meetings']:
            try:
                if not meet['regionName'] == 'Australia':
                    continue
                LOC = meet['name']
                for event in meet['events']:
                    round = event['raceNumber']
                    start_time = datetime.fromtimestamp(event['startTime'])
                    
                    race_identifyer = {'race_id':event['httpLink']}
                    
                    entrants = self.get_entrants(race_identifyer)
                    raceData.append({'round':round,'name': f'{LOC}', 'start_time':start_time.isoformat(),'entrants':entrants, 'race_id':race_identifyer})
            except Exception as e:
                self.local_print(e)
                continue
        return raceData
    
    def get_entrants(self,race_identifyer):
        entrants = []
        race_card = self.get_race_card(race_identifyer['race_id'])
        record_time = datetime.now()
        for market in race_card['markets']:
            if market['name'] == 'Win or Place' and market['international'] == False:
                for entrant in market['selections']:
                    try:
                        NAME = entrant['name']
                        for price in entrant['prices']:
                            if price['priceCode'] == 'L':
                                ODDS = -1
                                if 'winPrice' in price:
                                    ODDS = price['winPriceNum'] / price['winPriceDen']
                                    ODDS += 1
                                entrants.append({'name':NAME,'odds':ODDS,'scratched':entrant['result']=='V','record_time':record_time.isoformat()})
                    except Exception as e:
                        self.local_print(e)
                        continue
        return entrants
