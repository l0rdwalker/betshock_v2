import requests
import json
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class playup_horses(scraper):
    def getVenues(self,date:datetime):
        headers = {
            'authority': 'wagering-api.playup.io',
            'accept': 'application/json',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://www.playup.com.au',
            'platform': 'web',
            'priority': 'u=1, i',
            'product': 'www.playup.com.au',
            'referer': 'https://www.playup.com.au/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }

        params = {
            'include': 'races',
            'filter[start_date][from]': date.strftime("%Y-%m-%d"),
            'filter[start_date][to]': date.strftime("%Y-%m-%d"),
            'filter[is_future]': '0',
            'page[size]': '100',
            'page[number]': '1',
        }

        response = requests.get('https://wagering-api.playup.io/v1/meetings/', params=params, headers=headers)
        response = response.text
        return json.loads(response)

    def getRaceCard(self,id):
        headers = {
            'authority': 'wagering-api.playup.io',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'authorization': 'undefined',
            'dnt': '1',
            'origin': 'https://www.playup.com.au',
            'platform': 'web',
            'priority': 'u=1, i',
            'product': 'www.playup.com.au',
            'referer': 'https://www.playup.com.au/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        response = requests.get(
            f'https://wagering-api.playup.io/v1/races/{id}/?include=meeting,available_bet_types,selections.prices,result',
            headers=headers,
        )
        response = response.text
        return json.loads(response)
    
    def convertTime(self,data):
        startTime = datetime.fromtimestamp(data, tz=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime    

    def getEntrants(self,id):
        race = self.getRaceCard(id)
        startTime = self.convertTime(race['data']['attributes']['start_time_timestamp'])
        entrants = race['included']
        horses = []
        potentialIds = {}
        potentialNames = {}
        for entrant in entrants: 
            if entrant['type'] == 'selections':
                if entrant['attributes']['status']['id']  == 1:
                    NAME = entrant['attributes']['name']
                    for price in entrant['relationships']['prices']['data']:
                        potentialIds[price['id']] = NAME
            elif entrant['type'] == 'prices':
                if entrant['id'] in potentialIds and entrant['attributes']['bet_type']['name'] == 'Win':
                    potentialNames[potentialIds[entrant['id']]] = entrant['attributes']['d_price']

        for horse,odds in potentialNames.items():
            horses.append({'name':horse,'odds':odds})
        
        return horses,startTime

    def aquireOdds(self):
        races = []
        venues = self.getVenues(datetime.now())['data']
        for venue in venues:
            if venue['attributes']['race_type']['name'] == 'Gallop' and venue['attributes']['country']['code'] == 'AU':
                name = venue['attributes']['name']
                startTime = venue['attributes']['start_time']
                countIndex = 1
                for race in venue['relationships']['races']['data']:
                    horces,startTime = self.getEntrants(race['id'])
                    races.append({'name': f'R{countIndex} {name}', 'participants': len(horces),'startTime':startTime.isoformat(),'teams':horces})
                    self.addStartTime(startTime)
                    countIndex += 1
        return races
