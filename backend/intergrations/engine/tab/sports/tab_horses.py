import requests
import json
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class tab_horses(scraper):
    def getVenues(self,date:datetime):
        url = f'https://api.beta.tab.com.au/v1/bff-racing/{date.strftime("%Y-%m-%d")}'
        querystring = {
            "jurisdiction": "NSW",
            "platform": "android",
            "version": "12.14.0",
            "loginStatus": "false"
        }
        headers = {
            "user-agent": "au.com.tabcorp.sportsbet@12.14.0.233330013 (Google; Android 12)",
            "accept-encoding": "gzip",
            "host": "api.beta.tab.com.au",
            "retry-count": "2",
            "if-none-match": "W/\"17b86ba2a5f21a9aeaf1b08ad24df49b\""
        }
        response = requests.get(url, headers=headers, params=querystring)
        response = response.text
        return json.loads(response)

    def getRaces(self,date,location):
        url = f"https://api.beta.tab.com.au/v1/bff-racing/{date}/R/{location}"

        querystring = {
            "jurisdiction": "NSW",
            "platform": "android",
            "version": "12.14.0",
            "loginStatus": "false"
        }

        headers = {
            "user-agent": "au.com.tabcorp.sportsbet@12.14.0.233330013 (Google; Android 12)",
            "tracestate": "1261993@nr=0-2-318766-718307996-ac80e5eb239c4659----1707298569176",
            "accept-encoding": "gzip",
            "newrelic": "eyJ2IjpbMCwyXSwiZCI6eyJ0eSI6Ik1vYmlsZSIsImFjIjoiMzE4NzY2IiwiYXAiOiI3MTgzMDc5OTYiLCJ0ciI6ImNiMTMwZjFiMjZiMTQwZTRhMDM0YmFjN2FjZjZlY2Q0IiwiaWQiOiJhYzgwZTVlYjIzOWM0NjU5IiwidGkiOjE3MDcyOTg1NjkxNzYsInRrIjoiMTI2MTk5MyJ9fQ==",
            "traceparent": "00-cb130f1b26b140e4a034bac7acf6ecd4-ac80e5eb239c4659-00",
            "host": "api.beta.tab.com.au",
            "retry-count": "2"
        }

        response = requests.get(url, headers=headers, params=querystring)
        response = response.text
        return json.loads(response)

    def getRaceCard(self,date,location,raceNum):
        url = f"https://api.beta.tab.com.au/v1/bff-racing/{date}/R/{location}/{raceNum}"
        querystring = {
            "jurisdiction": "NSW",
            "platform": "android",
            "version": "12.14.0",
            "loginStatus": "false"
        }
        headers = {
            "user-agent": "au.com.tabcorp.sportsbet@12.14.0.233330013 (Google; Android 12)",
            "tracestate": "1261993@nr=0-2-318766-718307996-fdc6edac59534166----1707302041721",
            "accept-encoding": "gzip",
            "newrelic": "eyJ2IjpbMCwyXSwiZCI6eyJ0eSI6Ik1vYmlsZSIsImFjIjoiMzE4NzY2IiwiYXAiOiI3MTgzMDc5OTYiLCJ0ciI6Ijk4N2RmZDQ4MGYwMDQ4NGY5ODgxNzRhMzk3NjBjYjdmIiwiaWQiOiJmZGM2ZWRhYzU5NTM0MTY2IiwidGkiOjE3MDczMDIwNDE3MjEsInRrIjoiMTI2MTk5MyJ9fQ==",
            "traceparent": "00-987dfd480f00484f988174a39760cb7f-fdc6edac59534166-00",
            "host": "api.beta.tab.com.au",
            "retry-count": "2",
            "if-none-match": "W/\"4fdb3c03186dc0f9b11ee9af738a67f6\""
        }
        response = requests.get(url, headers=headers, params=querystring)
        response = response.text
        return json.loads(response)
    
    def convertTime(self,timeTxt):
        startTime = datetime.fromisoformat(timeTxt.replace('Z', '+00:00'))
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def aquireOdds(self):
        AustralianStates = ['ACT','NSW','NT','QLD','SA','TAS','VIC','WA']
        raceData = []
        venues = self.getVenues(datetime.now())
        for venue in venues['meetings']['R']:
            name:str = venue['meetingName']
            prelimName = name.split('(')
            if prelimName[1].replace(')','') in AustralianStates:
                name = prelimName[0].strip()
                location = venue['venueMnemonic']
                meetingDate = venue['meetingDate']
                races = self.getRaces(meetingDate,location)
                for race in races['races']:
                    raceNumber = race['number']
                    horces,startTime = self.getEntrants(meetingDate,location,raceNumber)
                    raceData.append({'name': f'R{raceNumber} {name}', 'participants': len(horces),'startTime': startTime.isoformat(),'teams':horces})
                    self.addStartTime(startTime)
        return raceData

    def getEntrants(self,meetingDate,location,raceNumber):
        horces = []
        race = self.getRaceCard(meetingDate,location,raceNumber)
        startTime = self.convertTime(race['raceDetail']['summary']['startTime'])
        entrants = race['raceDetail']['runners']
        for entrant in entrants:
            if not 'cratched' in entrant['fixedOdds']['bettingStatus']:
                NAME = entrant['runnerName']
                ODDS = entrant['fixedOdds']['returnWin']
                horces.append({'name':NAME,'odds':ODDS})
        return horces,startTime