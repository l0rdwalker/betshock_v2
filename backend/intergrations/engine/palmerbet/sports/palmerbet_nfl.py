import requests
from datetime import datetime
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class palmerbet_nfl(scraper):
    def aquireOdds(self):
        url = "https://fixture.palmerbet.online/fixtures/sports/378b3809-98e6-478d-8a30-a3b20739df78/matches"
        querystring = {
            "sportType": "AmericanFootball",
            "pageSize": "200",
            "channel": "mobile",
            "app-version": "5.77.161504"
        }
        headers = {
            "user-agent": "Dart/3.1 (dart:io)",
            "accept": "application/json",
            "accept-encoding": "gzip",
            "host": "fixture.palmerbet.online"
        }
        response = requests.get(url, headers=headers, params=querystring)
        sportsData = json.loads(response.text)
        
        return self.__cleanData(sportsData)

    def __cleanData(self,sportsData):
        cleanedData = {'data':[],'platform':'palmerbet','sport':'NFL'}

        for match in sportsData['matches']:
            try: 
                teams = []
                teams.append(self._constructTeam(match['homeTeam']))
                teams.append(self._constructTeam(match['awayTeam']))
                cleanedData["data"].append({'startTime':datetime.strptime(match['startTime'], '%Y-%m-%dT%H:%M:%SZ').isoformat(),'teams':teams,'name':'auto','participants':len(teams)})
            except:
                pass

        return cleanedData
    
    def _constructTeam(self,data):
        name = data['title']
        odds = data['win']['price']
        return {'name':name,'odds':odds}