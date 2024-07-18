import requests
import json
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class neds_horses(scraper):
    def getRaceCard(self,id):
        headers = {
            'authority': 'api.neds.com.au',
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'dnt': '1',
            'if-modified-since': 'Tue, 06 Feb 2024 01:25:21 GMT',
            'origin': 'https://www.neds.com.au',
            'priority': 'u=1, i',
            'referer': 'https://www.neds.com.au/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        params = {
            'method': 'racecard',
            'id': id,
        }
        response = requests.get('https://api.neds.com.au/rest/v1/racing/', params=params, headers=headers)
        response = response.text
        return json.loads(response)

    def getVenues(self,date:datetime):
        headers = {
            'authority': 'api.neds.com.au',
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'dnt': '1',
            'if-modified-since': 'Tue, 06 Feb 2024 02:45:38 GMT',
            'origin': 'https://www.neds.com.au',
            'priority': 'u=1, i',
            'referer': 'https://www.neds.com.au/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        }
        params = {
            'date': date.strftime("%Y-%m-%d"),
            'timezone': 'Australia/Sydney',
        }
        response = requests.get('https://api.neds.com.au/v2/racing/meeting', params=params, headers=headers)
        response = response.text
        return json.loads(response)
    
    def convertTime(self,timeTxt):
        startTime = datetime.fromtimestamp(timeTxt,tz=ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def aquireOdds(self):
        races = []
        data = self.getVenues(datetime.now())['meetings']
        for key,value in data.items():
            if 'country' in value:
                if value['country'] == 'AUS' and value['category_id'] == '4a2788f8-e825-4d36-9894-efd4baf1cfae':
                    venueName = value['name']
                    raceCount = 1
                    for raceId in value['race_ids']:
                        raceName = f'R{raceCount} {venueName}'
                        try:
                            horses,startTime = self.collectEntrants(raceId)
                            raceCount += 1
                            races.append({'name': raceName, 'participants': len(horses),'startTime':startTime.isoformat(),'teams':horses})
                            self.addStartTime(startTime)
                        except:
                            continue
        return races

    def collectEntrants(self,raceId):
        data = self.getRaceCard(raceId)['data']
        entrants = data['entrants']
        prices = data['prices']
        horses = []
        for entrant in entrants.items():
            entrant = entrant[1]
            if not 'is_scratched' in entrant:
                NAME = entrant['name']
                entrantID = entrant['id']
                ODDS = prices[f'{entrantID}:940b8704-e497-4a76-b390-00918ff7d282:']
                ODDS = 1+ODDS['odds']['numerator']/ODDS['odds']['denominator']
                horses.append({'name':NAME,'odds':ODDS})
        
        startTime = None
        for key,time in data['races'].items():
            startTime = time['advertised_start']['seconds']
            break

        return horses,self.convertTime(startTime)