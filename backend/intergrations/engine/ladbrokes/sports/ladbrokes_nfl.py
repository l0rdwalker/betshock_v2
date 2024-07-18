import requests
from datetime import datetime
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class ladbrokes_nfl(scraper):
    def aquireOdds(self):
        url = "https://api.ladbrokes.com.au/graphql"

        payload = {
            "variables": {
                "showIndicators": True,
                "regionSlug": "",
                "competitionSlug": "nfl",
                "category": "AMERICAN_FOOTBALL",
                "anyTeamVsAnyTeamEnabled": True
            },
            "operationName": "SportingCompetitionEvents",
            "extensions": { "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "e940e43da8ccda8b7d712ea1977599b89b84da6aed1f019abb631d9780dc8cd2"
                } }
        }
        headers = {
            "content-type": "application/json",
            "host": "api.ladbrokes.com.au",
            "accept-encoding": "gzip"
        }
        response = requests.post(url, json=payload, headers=headers)
        sportsData = json.loads(response.text)
        
        return self.__cleanData(sportsData)

    def __cleanData(self,sportsData):
        matches = sportsData['data']['competition']['events']['nodes']
        cleanedData = {'data':[]}

        for match in matches:
            for market in range(0,len(match['markets']['nodes'])):
                market = match['markets']['nodes'][market]
                if market['name'] == "Head To Head":
                    teamOne = self.__constructTeam(market,0)
                    teamTwo = self.__constructTeam(market,1)
                    cleanedData['data'].append({'startTime':datetime.strptime(match['advertisedStart'], '%Y-%m-%dT%H:%M:%S.%fZ').isoformat(),'teams':[teamOne,teamTwo],'name':'auto','participants':2})

        cleanedData['platform'] = "ladbrokes"
        cleanedData['sport'] = "NFL"
        return cleanedData

    def __constructTeam(self,market,teamNum):
        team = market['entrants']['nodes'][teamNum]
        name = team['name']
        teamOdds = 1 + (team['price']['odds']['numerator']/team['price']['odds']['denominator'])

        return {'name':name,'odds':teamOdds}
