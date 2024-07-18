import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class betm_horses(scraper):
    def getVenues(self,token):
        url = "https://api.betm.com.au/v1/fixtures/races/today/A"

        headers = {
            "user-agent": "Dart/3.2 (dart:io)",
            "x-client-version": "5.6.0",
            "accept-encoding": "gzip",
            "x-client-model": "Pixel 3",
            "x-csrf-token": f"{token}",
            "host": "api.betm.com.au",
            "x-client-platform": "android"
        }

        response = requests.get(url, headers=headers)
        response = response.text
        response = json.loads(response)
        return response

    def getcsrf_token(self):
        url = "https://api.betm.com.au/v1/csrf_token"

        headers = {
            "user-agent": "Dart/3.2 (dart:io)",
            "x-client-version": "5.6.0",
            "accept-encoding": "gzip",
            "x-client-model": "Pixel 3",
            "host": "api.betm.com.au",
            "x-client-platform": "android"
        }

        response = requests.get(url, headers=headers)
        response = response.text
        response = json.loads(response)
        return response

    def getRaceCard(self,token,id):
        url = f"https://api.betm.com.au/v1/fixtures/races/{id}"

        headers = {
            "user-agent": "Dart/3.2 (dart:io)",
            "x-client-version": "5.6.0",
            "accept-encoding": "gzip",
            "x-client-model": "Pixel 3",
            "x-csrf-token": f"{token}",
            "host": "api.betm.com.au",
            "x-client-platform": "android"
        }

        response = requests.get(url, headers=headers)
        response = response.text
        response = json.loads(response)
        return response

    def convertTime(self,timeTxt):
        startTime = datetime.strptime(timeTxt, '%Y-%m-%dT%H:%M:%SZ')
        startTime = startTime.replace(tzinfo=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def aquireOdds(self):
        raceData = []
        AustralianStates = ['ACT','NSW','NT','QLD','SA','TAS','VIC','WA']
        token = self.getcsrf_token()['token']#'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDczNzE3MjMsImlhdCI6MTcwNzM2ODEyMywic3ViIjoiMTIwLjE4LjEwNC4xNjgifQ.0Yi_AL3DWBOPl9kXhco18utUHtEVspP_YuT_TqTQsBo'#
        venues = self.getVenues(token)['race_cards']
        for venue in venues:
            if venue['race_type'] == 'T' and venue['race_state'] in AustralianStates:
                LOC = venue['meeting_name']
                raceNumber = 1
                for race in venue['races']:
                    horces,startTime = self.getEntrants(token,race['event_id'])
                    raceData.append({'name': f'R{raceNumber} {LOC}', 'participants': len(horces),'startTime':startTime.isoformat(),'teams':horces})
                    self.addStartTime(startTime)
                    raceNumber += 1
        return raceData             

    def getEntrants(self,token,id):
        horces = []
        entrants = self.getRaceCard(token,id)
        for entrant in entrants['race']['runners']:
            if entrant['scratched_at'] == None:
                NAME = entrant['name']
                ODDS = entrant['fwin']
                horces.append({'name':NAME,'odds':ODDS})
        return horces,self.convertTime(entrants['race']['starts_at'])
