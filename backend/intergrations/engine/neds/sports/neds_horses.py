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

        response = requests.get(f'https://api.betm.com.au/v1/fixtures/races/{id}', params=params, headers=headers)
        response = json.loads(response.text)
        return response

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
        return races
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
                            if (len(horses) > 0):
                                raceCount += 1
                                races.append({'name': raceName, 'participants': len(horses),'startTime':startTime.isoformat(),'teams':horses})
                                self.addStartTime(startTime)
                        except Exception as e:
                            print(e)
                            continue
        return races

    def collectEntrants(self,raceId): 
        data = self.getRaceCard(raceId)['data']
        
                            
        startTime = None
        for key,time in data['races'].items():
            startTime = time['advertised_start']['seconds']
            break

        return horses,self.convertTime(startTime)