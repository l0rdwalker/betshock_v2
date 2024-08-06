import requests
import json
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class betfair_markets(scraper):
    def get_race_markets(self,market_id):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'dnt': '1',
            'origin': 'https://www.betfair.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.betfair.com.au/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }

        response = self.router.perform_get_request(
            platform=self.platformName,
            url=f'https://ero.betfair.com.au/www/sports/exchange/readonly/v1/bymarket?_ak=nzIFcwyWhrlwYMrh&alt=json&currencyCode=AUD&locale=en&marketIds={market_id}&rollupLimit=25&rollupModel=STAKE&types=MARKET_STATE,MARKET_RATES,MARKET_DESCRIPTION,EVENT,RUNNER_DESCRIPTION,RUNNER_STATE,RUNNER_EXCHANGE_PRICES_BEST,RUNNER_METADATA,MARKET_LICENCE,MARKET_LINE_RANGE_INFO',
            headers=headers
        )

        return response

    def get_day_races(self):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            'dnt': '1',
            'origin': 'https://www.betfair.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.betfair.com.au/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'x-application': 'nzIFcwyWhrlwYMrh',
        }

        params = {
            '_ak': 'nzIFcwyWhrlwYMrh',
            'eventTypeId': '7',
            'navigationType': 'todayscard',
            'raceId': '33437480.0534',
        }

        response = self.router.perform_get_request(
            platform=self.platformName,
            url='https://apieds.betfair.com.au/api/eds/racing-navigation/v1',
            params=params,
            headers=headers, 
        )
        
        return response

    def get_all_meets(self,race_date_obj:timedelta):
        curr = datetime.now()
        if isinstance(race_date_obj, timedelta):
            curr += race_date_obj
            
        race_profile = []
        races = self.get_day_races()
        for race in races['races']:
            try:
                date_object = datetime.strptime(race['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                ajusted_date_object = date_object.replace(tzinfo=ZoneInfo('UTC'))
                ajusted_date_object = ajusted_date_object.astimezone(ZoneInfo('Australia/Sydney'))
                if 'AUS' in race['meetingName'] and date_object < (curr+timedelta(days=2)):
                    race_identifyer = {'race_id':race['winMarketId']}
                    ENTRANTS,LOC = self.get_entrants(race_identifyer)
                    race_profile.append(self.create_race_entry(
                        track_name=LOC,
                        round=-1,
                        start_time=ajusted_date_object,
                        entrants=ENTRANTS
                    ))
            except Exception as e:
                print(f'betfair: {e}')
                continue
        return race_profile
    
    def get_entrants(self,race_identifyer):
        race_data = self.get_race_markets(race_identifyer['race_id'])
        record_time = datetime.now()
        ENTRANTS = []
        
        race_data = race_data['eventTypes'][0]['eventNodes'][0]
        venue_info = race_data['event']
        VENUE_NAME = venue_info['venue']
        entrants = race_data['marketNodes'][0]['runners']
        for entrant in entrants:
            NAME = "".join((entrant['description']['runnerName'].split('. ')[1]))
            TOTAL_PRICE = 0
            try:
                if 'availableToBack' in entrant['exchange']:
                    for price in entrant['exchange']['availableToBack']:
                        TOTAL_PRICE += price['price']
                    ENTRANTS.append({'name':NAME,'market_size':TOTAL_PRICE/len(entrant['exchange']['availableToBack']),'record_time':record_time.isoformat()})
            except Exception as e:
                print(f'betfair: {e}')
                continue
        return ENTRANTS,VENUE_NAME