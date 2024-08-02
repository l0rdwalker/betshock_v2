import requests
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class betm_horses(scraper):
    def getVenues(self):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'dnt': '1',
            'origin': 'https://betm.com.au',
            'priority': 'u=1, i',
            'referer': 'https://betm.com.au/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-client-platform': 'web',
            'x-client-version': '5.18.0',
        }

        response = self.router.perform_get_request(
            platform=self.platformName,
            url='https://api.betm.com.au/v1/fixtures/races/today/T',
            headers=headers
        )
        
        return response

    def getRaceCard(self,id):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'dnt': '1',
            'origin': 'https://betm.com.au',
            'priority': 'u=1, i',
            'referer': 'https://betm.com.au/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
            'x-client-platform': 'web',
            'x-client-version': '5.18.0',
        }
        params = {
            'is_future': 'false',
        }
        response = self.router.perform_get_request(
            platform=self.platformName,
            url=f'https://api.betm.com.au/v1/fixtures/races/{id}', 
            params=params, 
            headers=headers
        )
        
        return response

    def convertTime(self,timeTxt):
        startTime = datetime.strptime(timeTxt, '%Y-%m-%dT%H:%M:%SZ')
        startTime = startTime.replace(tzinfo=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def aquireOdds(self,race_date_obj:timedelta):
        raceData = []
        AustralianStates = ['ACT','NSW','NT','QLD','SA','TAS','VIC','WA']
        venues = self.getVenues()['race_cards']
        for venue in venues:
            #try:
            if venue['race_type'] == 'T' and venue['race_state'] in AustralianStates:
                LOC = venue['meeting_name']
                for race in venue['races']:
                    race_identifyer = {'race_id':race['event_id']}
                    horces,startTime = self.get_entrants(race_identifyer)
                    raceData.append({'round':race['race_number'], 'name': f'{LOC}', 'start_time':startTime.isoformat(),'entrants':horces, 'race_id':race_identifyer})
            #except Exception as e:
            #    self.local_print(e)
            #    continue
        return raceData             

    def get_entrants(self,race_identifyer):
        horces = []
        entrants = self.getRaceCard(race_identifyer['race_id'])
        record_time = datetime.now()
        for entrant in entrants['race']['runners']:
            #try:
            NAME = entrant['name']
            ODDS = entrant['fwin']
            if (ODDS == None):
                ODDS = -1
            horces.append({'name':NAME,'odds':ODDS,'scratched':not entrant['scratched_at'] == None,'record_time':record_time.isoformat()})
            #except Exception as e:
            #    self.local_print(e)
        return horces,self.convertTime(entrants['race']['starts_at'])
