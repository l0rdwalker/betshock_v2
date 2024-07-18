import requests
from datetime import datetime
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class sportsbett_nfl(scraper):
    def aquireOdds(self):
        url = "https://gwapi.sportsbet.com.au/sportsbook-sports/Sportsbook/Sports/Competitions/3073"

        querystring = {
            "displayType": "default",
            "includeTopMarkets": "true",
            "eventFilter": "matches"
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "gwapi.sportsbet.com.au",
            "accept-encoding": "gzip"
        }

        response = requests.get(url, headers=headers, params=querystring)
        sportsData = json.loads(response.text)
        
        return self.__cleanData(sportsData)

    def __cleanData(self,sportsData):
        cleanedData = {'data':[],'platform':'sportsbett','sport':'NFL'}
        for match in sportsData['events']:
            teams = []
            for market in match['marketList']:
                if market['name'] == 'Match Betting':
                    for team in market['selections']:
                        teams.append({'name':team['name'],'odds':team['price']['winPrice']})
                    break
            cleanedData["data"].append({'startTime':datetime.utcfromtimestamp(match['startTime']).isoformat(),'teams':teams,'name':'auto','participants':len(teams)})
        cleanedData['participants'] = len(cleanedData['data'])
        return cleanedData
            
