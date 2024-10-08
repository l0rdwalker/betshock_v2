import requests
from datetime import datetime,timezone,timedelta
import json
import os
import sys
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class pointsbet_horses(scraper):
    def __init__(self,attributes,database,router) -> None:
        super().__init__(attributes,database,router)
        self.flex_dates = False
    
    def getVenues(self):
        url = "https://api.au.pointsbet.com/api/racing/v3/meetings"
        querystring = {
            "daysToFetch": "1",
            "dateOffset": "0"
        }
        headers = {
            "host": "api.au.pointsbet.com",
            "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Android WebView\";v=\"120\"",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; Pixel 3 Build/SP1A.210812.016.B1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.6099.232 Mobile Safari/537.36 PointsBetApp/android/3.21.0/402212",
            "accept": "application/json, text/plain, */*",
            "x-requested-with": "com.pointsbet.app",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
        }
        response = self.router.perform_get_request(
            platform=self.platformName,
            url=url,
            headers=headers,
            params=querystring
        )
        return response

    def getRaceCard(self,id):
        url = f"https://api.au.pointsbet.com/api/racing/v3/races/{id}"
        headers = {
            "host": "api.au.pointsbet.com",
            "connection": "keep-alive",
            "sec-ch-ua": "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Android WebView\";v=\"120\"",
            "sec-ch-ua-platform": "\"Android\"",
            "sec-ch-ua-mobile": "?1",
            "user-agent": "Mozilla/5.0 (Linux; Android 12; Pixel 3 Build/SP1A.210812.016.B1; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.6099.232 Mobile Safari/537.36 PointsBetApp/android/3.21.0/402212",
            "accept": "application/json, text/plain, */*",
            "x-requested-with": "com.pointsbet.app",
            "sec-fetch-site": "cross-site",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
        }
        
        response = self.router.perform_get_request(
            platform=self.platformName,
            url=url,
            headers=headers
        )
        
        return response
    
    def convertTime(self,timeTxt):
        startTime = datetime.strptime(timeTxt, "%Y-%m-%dT%H:%M:%SZ")
        startTime = startTime.replace(tzinfo=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def get_all_meets(self,race_date_obj:timedelta):
        race_profile = []
        try:
            venues = self.getVenues()[0]['meetings']
        except Exception as e:
            self.local_print(e)
            return race_profile    
        
        for venue in venues:
            try:
                if venue['racingType'] == 1 and venue['countryName'] == 'Australia':
                    LOC = venue['venue']
                    for race in venue['races']:
                        try:
                            ROUND = race['raceNumber']
                            raceId = race['raceId']
                            race_identifyer = {'race_id':raceId}

                            ENTRANTS,START_TIME = self.get_entrants(race_identifyer)
                            race_profile.append(self.create_race_entry(
                                track_name=LOC,
                                round=ROUND,
                                start_time=START_TIME,
                                entrants=ENTRANTS,
                                race_identifyer=race_identifyer
                            ))
                        except Exception as e:
                            self.local_print(e)
            except Exception as e:
                self.local_print(e)
                continue
        return race_profile 
            
    def get_entrants(self,race_id_json):
        horces = []
        raceCard = self.getRaceCard(race_id_json['race_id'])
        if raceCard == None:
            return horces
        
        START_TIME = self.convertTime(raceCard["advertisedStartTimeUtc"])
        read_time = datetime.now()
        for entrant in raceCard['runners']:
            try:
                NAME = entrant["runnerName"]
                ODDS = -1
                if entrant["isScratched"] == False:
                    if 'current' in entrant['fluctuations']:
                        ODDS = entrant['fluctuations']['current']
                horces.append(self.create_entrant_entry(
                    entrant_name=NAME,
                    odds=ODDS,
                    scratched=entrant["isScratched"],
                    record_time=read_time
                ))
            except Exception as e:
                self.local_print(e)
        return horces,START_TIME