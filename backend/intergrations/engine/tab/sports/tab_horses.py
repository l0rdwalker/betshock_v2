import requests
import json
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class tab_horses(scraper):
    def __init__(self,attributes,database,router) -> None:
        super().__init__(attributes,database,router)
        self.flex_dates = True
    
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
        
        response = self.router.perform_get_request(
            platform=self.platformName,
            url=url,
            headers=headers, 
            params=querystring
        )

        return response

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

        response = self.router.perform_get_request(
            self.platformName,
            url=url,
            headers=headers,
            params=querystring
        )
        
        return response

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
        
        response = self.router.perform_get_request(
            platform=self.platformName,
            url=url,
            headers=headers, 
            params=querystring
        )
        
        return response

    def get_all_meets(self,race_date_obj:timedelta):
        set_date = datetime.now()
        if isinstance(race_date_obj,timedelta):
            set_date = set_date+race_date_obj
        
        AustralianStates = ['ACT','NSW','NT','QLD','SA','TAS','VIC','WA']
        raceData = []
        
        venues = self.getVenues(set_date)

        if not 'meetings' in venues:
            return raceData
        elif not 'R' in venues['meetings']:
            return raceData
        
        for venue in venues['meetings']['R']:
            name:str = venue['meetingName']
            prelimName = name.split('(')
            if prelimName[1].replace(')','') in AustralianStates:
                NAME = prelimName[0].strip()
                location = venue['venueMnemonic']
                meetingDate = venue['meetingDate']
                races = self.getRaces(meetingDate,location)
                for race in races['races']:
                    ROUND = race['number']
                    RACE_ID = {'meeting_date':meetingDate,'location':location,'round':ROUND}
                    
                    ENTRANTS,START_TIME = self.get_entrants(RACE_ID)
                    if ENTRANTS == None:
                        continue
                    
                    raceData.append(self.create_race_entry(
                        track_name=NAME,
                        round=ROUND,
                        start_time=START_TIME,
                        entrants=ENTRANTS,
                        race_identifyer=RACE_ID))
        return raceData

    def get_entrants(self,race_identifyer):
        horces = []
        race = self.getRaceCard(race_identifyer['meeting_date'],race_identifyer['location'],race_identifyer['round'])
        if race == None:
            return None,None
        
        record_time = datetime.now()
        entrants = race['raceDetail']['runners']
        for entrant in entrants:
            NAME = entrant['runnerName']
            ODDS = entrant['fixedOdds']['returnWin']
            horces.append(self.create_entrant_entry(entrant_name=NAME,odds=ODDS,scratched=('cratched' in entrant['fixedOdds']['bettingStatus']),record_time=record_time))
        return horces,race['raceDetail']['summary']['startTime']