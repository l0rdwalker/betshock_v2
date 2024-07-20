import requests
import json
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class palmerbet_horses(scraper):
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
        response = requests.get(
            f'https://fixture.palmerbet.online/fixtures/racing/{date.strftime("%Y-%m-%d")}/HorseRacing',
            params=params,
            headers=headers,
        )
        response = response.text
        return json.loads(response)

    def getRaceCard(self,id):
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

        response = requests.get(
            f'https://fixture.palmerbet.online/fixtures/racing/HorseRacing/markets/{id}',
            params=params,
            headers=headers,
        )
        response = response.text
        return json.loads(response)

    def getPrelimRaceCard(self,id):
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

        response = requests.get(
            f'https://fixture.palmerbet.online{id}',
            params=params,
            headers=headers,
        )
        response = response.text
        return json.loads(response)

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
                
    def convertTime(self,timeTxt):
        startTime = datetime.strptime(timeTxt, '%Y-%m-%dT%H:%M:%SZ')
        startTime = startTime.replace(tzinfo=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def aquireOdds(self):
        races = []
        data = self.getVenus(datetime.now())
        for meeting in data['meetings']:
            if 'country' in meeting:
                if (meeting["country"] == 'AU'):
                    venueName = meeting['venue']['title']
                    raceCount = 1
                    for race in meeting['races']:
                        try:
                            id = race['_links'][0]['href'].split('/')
                            id[len(id)-2] = '%20'.join(venueName.split(' '))
                            id = '/'.join(id)
                            horces,winner = self.collectEntrants(id)
                            startTime = self.convertTime(race['startTime'])
                            
                            tempData = {'winner': winner, 'name': f'R{raceCount} {venueName}', 'participants': len(horces),'startTime': startTime.isoformat(),'teams':horces}
                            print(json.dumps(tempData))
                            races.append(tempData)
                            self.addStartTime(startTime)
                            raceCount += 1
                        except:
                            continue
        return races

    def collectEntrants(self,preliminaryID):
        horces = []
        prelimData = self.getPrelimRaceCard(preliminaryID)
        id = None
        winner = prelimData['race']['result']['first'][0]
        for market in prelimData['race']['markets']:
            if market['title'] == 'Win':
                id = market['id']
                break

        racers = set()
        for horce in prelimData['race']['runners']:
            if horce['isScratched'] == False:
                if horce['number'] == winner:
                    winner = horce['name']
                racers.add(horce['name'])
        
        entrants = self.getRaceCard(id)['market']['outcomes']
        for entrant in entrants:
            NAME = entrant['title']
            if NAME in racers:
                ODDS = self.conditionalDrillDown(entrant['prices'],'name','Fixed')['priceSnapshot']['current']
                horces.append({'name':NAME,'odds':ODDS})
        return horces,winner