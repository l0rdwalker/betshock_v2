import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class ladbrokes_horses(scraper):
    def __init__(self,attributes) -> None:
        super().__init__(attributes)
        self.globalUrl = "https://api.ladbrokes.com.au/graphql"

    def getAllMarkets(self):
        cur_date = datetime.now()
        headers = {
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'dnt': '1',
            'if-modified-since': 'Fri, 19 Jul 2024 10:31:31 GMT',
            'origin': 'https://www.ladbrokes.com.au',
            'priority': 'u=1, i',
            'referer': 'https://www.ladbrokes.com.au/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }

        params = {
            'date': cur_date.strftime("%Y-%m-%d"),
            'region': 'domestic',
            'timezone': 'Australia/Sydney',
        }

        response = requests.get('https://api.ladbrokes.com.au/v2/racing/meeting', params=params, headers=headers)
        return json.loads(response.text)

    def get_race_details(self,id):
        headers = {
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://www.ladbrokes.com.au',
            'priority': 'u=1, i',
            'referer': 'https://www.ladbrokes.com.au/',
            'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        }
        params = {
            'method': 'racecard',
            'id': f'{id}',
        }
        response = requests.get('https://api.ladbrokes.com.au/rest/v1/racing/', params=params, headers=headers)
        return json.loads(response.text)
        
    def getRaceRoundDetails(self,id:str):
        id = id.replace('RacingMarket:','')

        url = "https://api.ladbrokes.com.au/graphql"
        querystring = {
            "operationName": "RacingRaceScreen",
            "variables": "{\"raceId\":\""+id+"\"}",
            "extensions": "{\"persistedQuery\":{\"version\":1,\"sha256Hash\":\"84d3c0ba5fc52da6471ce036915962e86dba18bc16bf0697e5198be4f3cb5365\"}}"
        }
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "host": "api.ladbrokes.com.au",
            "connection": "Keep-Alive",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.2"
        }
        response = requests.get(url, headers=headers, params=querystring).text
        data = json.loads(response)['data']['race']['finalFieldMarket']['nodes'][0]
        return data

    def find_associated_odds(self,prices,searchID):
        winID = '940b8704-e497-4a76-b390-00918ff7d282'
        placeID = '7cf3eea6-5654-42be-9c2e-6de280e7bb34'

        if f'{searchID}:{winID}:' in prices:
            odds_json = prices[f'{searchID}:{winID}:']
            if ('numerator' in odds_json['odds'] and 'denominator' in odds_json['odds']):
                odds = (float(odds_json['odds']['numerator'])/float(odds_json['odds']['denominator']))+1
                return odds
        return -1

    def convertTime(self,timeTxt):
        startTime = datetime.strptime(timeTxt, '%Y-%m-%dT%H:%M:%S.%fZ')
        startTime = startTime.replace(tzinfo=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def collectOdds(self,entrys,prices):
        horces = []
        for hourse in entrys:
            try:
                if (hourse['isScratched'] == hourse['isLateScratched'] == False):
                    currId = hourse['id'].replace('RacingEntrant:','')
                    HOURSENAME = hourse['name']
                    WIN_ODDS = self.findAssociatedOdds(prices,currId)
                    horces.append({'name':HOURSENAME,'odds':WIN_ODDS})
            except:
                continue
        return horces

    def aquireOdds(self):
        markets = self.getAllMarkets()
        race_data = []
        
        for event in markets['meetings'].items():
            try:
                event = event[1]
                if (event['category_id'] == '4a2788f8-e825-4d36-9894-efd4baf1cfae'):
                    if (not event['country'] == 'AUS'):
                        continue
                    LOC = event['name']
                    round = 1
                    for race_id in event['race_ids']:
                        race_details = self.get_race_details(race_id)
                        START_TIME = None
                        for key,item in race_details['data']['meetings'].items():
                            START_TIME = datetime.fromtimestamp(item['advertised_date']['seconds'])
                            break
                        
                        entrants = []
                        for key,entrant in race_details['data']['entrants'].items():
                            if "barrier" in entrant:
                                HORSE_NAME = entrant['name']
                                ODDS = self.find_associated_odds(race_details['data']['prices'],entrant['id'])
                                if (ODDS != -1):
                                    entrants.append({'name':HORSE_NAME,'odds':ODDS, 'scratched':'is_scratched' in entrant})
                        if (len(entrants) > 0):
                            race_data.append({'round': round,'name': f'{LOC}','start_time':START_TIME.isoformat(),'entrants':entrants})
                            round += 1
            except Exception as e:
                print(e)
                continue

        return race_data
