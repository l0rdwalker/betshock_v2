import requests
import json
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class palmerbet_horses(scraper):
    def __init__(self,attributes,database,router) -> None:
        super().__init__(attributes,database,router)
        self.flex_dates = True
    
    def cacheData(self,data):
        file = os.path.dirname(os.path.abspath(__file__))
        file = os.path.join(file,'temp.txt')
        with open(file, 'a') as file:
            for line in data:
                file.write(json.dumps(line) + '\n')
    
    def getVenus(self,date:datetime):
        headers = {
            'authority': 'fixture.palmerbet.online',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'dnt': '1',
            'origin': 'https://www.palmerbet.com',
            'priority': 'u=1, i',
            'referer': 'https://www.palmerbet.com/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        params = {
            'channel': 'website',
        }
        response = self.router.perform_get_request(
            platform=self.platformName,
            url=f'https://fixture.palmerbet.online/fixtures/racing/{date.strftime("%Y-%m-%d")}/HorseRacing',
            params=params,
            headers=headers
        )
        return response

    def get_race_card(self,id):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'dnt': '1',
            'origin': 'https://www.palmerbet.com',
            'priority': 'u=1, i',
            'referer': 'https://www.palmerbet.com/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        params = {
            'channel': 'website',
        }

        response = self.router.perform_get_request(
            platform=self.platformName,
            url=f'https://fixture.palmerbet.online/fixtures/racing/HorseRacing/markets/{id}',
            params=params,
            headers=headers
        )
        
        return response

    def get_prelim_race_card(self,link):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'dnt': '1',
            'origin': 'https://www.palmerbet.com',
            'priority': 'u=1, i',
            'referer': 'https://www.palmerbet.com/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        params = {
            'channel': 'website',
        }

        response = self.router.perform_get_request(
            platform=self.platformName,
            url=f'https://fixture.palmerbet.online/{link}',
            params=params,
            headers=headers
        )
        
        return response

    def conditionalDrillDown(self,array,key,searchValue):
            def compareItems(subject,searchTerms):
                if isinstance(searchTerms, list):
                    return subject in searchTerms
                else:
                    return searchTerms == subject
            for item in array:
                testElement = item[key]
                if compareItems(testElement,searchValue):
                    return item

    def get_all_meets(self,race_date_obj:timedelta):
        set_date = datetime.now()
        if isinstance(race_date_obj,timedelta):
            set_date += race_date_obj
        
        race_profile = []
        data = self.getVenus(set_date)
        for meeting in data['meetings']:
            if 'country' in meeting:
                if (meeting["country"] == 'AU'):
                    TRACK_NAME = meeting['venue']['title']
                    for race in meeting['races']:
                        try:
                            race_identifyer = {'race_id':race['_links'][0]['href']}

                            ENTRANTS = self.get_entrants(race_identifyer)
                            START_TIME = race['startTime']
                            START_TIME:datetime = datetime.fromisoformat(START_TIME.replace('Z', '+00:00'))
                            START_TIME = START_TIME.isoformat()
                            
                            race_profile.append(self.create_race_entry(
                                track_name=TRACK_NAME,
                                round=race['number'],
                                race_identifyer=race_identifyer,
                                entrants=ENTRANTS,
                                start_time=START_TIME
                            ))
                        except Exception as e:
                            self.local_print(e)
                            continue
        return race_profile

    def get_entrants(self,race_identifyer):
        ENTRANTS = []
        prelim_data = self.get_prelim_race_card(race_identifyer['race_id'])
        if prelim_data == None:
            return ENTRANTS
        
        record_time = datetime.now()
        win_price_id = None

        for item in prelim_data['race']['markets']:
            if item['title'] == 'Win':
                win_price_id = item['id']
                break
        if win_price_id != None:
            entrants = self.get_race_card(win_price_id)
            if entrants == None:
                return ENTRANTS
            entrants = entrants['market']['outcomes']
            for entrant in entrants:
                NAME = entrant['title']
                ODDS = -1
                for price in entrant['prices']:
                    if price['name'] == 'Fixed':
                        if 'priceSnapshot' in price:
                            ODDS = price['priceSnapshot']['current']
                        break
                ENTRANTS.append(self.create_entrant_entry(
                    entrant_name=NAME,
                    odds=ODDS,
                    scratched=(not entrant["status"]=='Active'),
                    record_time=record_time
                ))
        return ENTRANTS