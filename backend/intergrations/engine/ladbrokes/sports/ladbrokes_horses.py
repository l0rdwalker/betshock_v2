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
        payload = {
            "operationName": "RacingExtraMarketsList",
            "extensions": { "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "fc75ea1bf3825a06e28028128e8850b9dbcf48d0b40d3ab0bc603114f2b927ec"
                } }
        }
        headers = {
            "content-type": "application/json",
            "host": "api.ladbrokes.com.au",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.2"
        }
        data = requests.post(self.globalUrl, json=payload, headers=headers).text
        data = json.loads(data)
        return data['data']['racingExtraMarkets']['nodes']

    def getRaceListForLocation(self,id):
        payload = {
            "variables": {
                "id": id,
                "promotions": True,
                "promotionEligibility": ["ATL"],
                "walletType": "PERSONAL",
                "isLoggedIn": False
            },
            "operationName": "RacingMeetingRacesList",
            "extensions": { "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "549386b3f261894dd969f87019078822c31a1464c23e975f30c0245a62ed5fff"
                } }
        }
        headers = {
            "content-type": "application/json",
            "host": "api.ladbrokes.com.au",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.2"
        }

        return json.loads(requests.post(self.globalUrl, json=payload, headers=headers).text)['data']['meeting']['races']['nodes']

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

    def findAssociatedOdds(self,prices,searchID):
        winID = '940b8704-e497-4a76-b390-00918ff7d282'
        placeID = '7cf3eea6-5654-42be-9c2e-6de280e7bb34'
        for price in prices:
            if price['id'] == f'{searchID}:{winID}:':
                odds = (float(price['odds']['numerator'])/float(price['odds']['denominator']))+1
                return odds
        raise Exception("couldn't find odds.")

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
        races = []
        for location in markets:
            if (location['category'] == 'HORSE'):
                LOC = location['name']
                rounds = self.getRaceListForLocation(location['id'])
                for x in range(0,len(rounds)):
                    roundDetails = self.getRaceRoundDetails(rounds[x]['id'])
                    horces = self.collectOdds(roundDetails['entrants']['nodes'],roundDetails['prices'])
                    if len(horces) > 0:
                        startTime = self.convertTime(roundDetails['actualStart'])
                        races.append({'name': f'R{x+1} {LOC}', 'participants': len(horces),'startTime':startTime.isoformat(),'teams':horces})
                        self.addStartTime(startTime)
        return races
