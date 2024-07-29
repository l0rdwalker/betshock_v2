import requests
from datetime import datetime
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class tab_nfl(scraper):
    def aquireOdds(self):
        url = "https://api.beta.tab.com.au/v1/bff-sports/sports/American%20Football/competitions/NFL/page"

        querystring = {
            "jurisdiction": "NSW",
            "version": "12.13.0",
            "loggedIn": "false"
        }

        headers = {
            "accept-encoding": "gzip",
            "host": "api.beta.tab.com.au"
        }

        response = requests.get(url, headers=headers, params=querystring)
        sportsData = json.loads(response.text)
        
        return self.__cleanData(sportsData)

    def __cleanData(self,sportsData):
        cleanedData = {'data':[],'platform':'tab','sport':'NFL'}
        for markets in sportsData['data']:
            if (markets['type'] == 'sports.competition.betOptions'):
                for match in markets['data'][0]['data']:
                    teams = []
                    for team in match['markets'][0]['propositions']:
                        teams.append({'name':team['name'],'odds':team['returnWin']})
                    cleanedData["data"].append(
                        {
                            'startTime':datetime.strptime(match['startTime'], 
                            "%Y-%m-%dT%H:%M:%S.%fZ").isoformat(),
                            'teams':teams,
                            'name':'auto',
                            'participants':len(teams)
                        }
                    )
        return cleanedData
    
    def get_entrants(self):
        pass