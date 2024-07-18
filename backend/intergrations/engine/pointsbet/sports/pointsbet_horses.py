import requests
from datetime import datetime,timezone
import json
import os
import sys
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class pointsbet_horses(scraper):
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
        response = requests.get(url, headers=headers, params=querystring)
        response = response.text
        response = json.loads(response)
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
        response = requests.get(url, headers=headers)
        response = response.text
        response = json.loads(response)
        return response
    
    def convertTime(self,timeTxt):
        startTime = datetime.strptime(timeTxt, "%Y-%m-%dT%H:%M:%SZ")
        startTime = startTime.replace(tzinfo=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def aquireOdds(self):
        raceData = []
        venues = self.getVenues()[0]['meetings']
        for venue in venues:
            if venue['racingType'] == 1 and venue['countryName'] == 'Australia':
                LOC = venue['venue']
                for race in venue['races']:
                    raceNumber = race['raceNumber']
                    raceId = race['raceId']
                    horces,startTime = self.getEntrants(raceId)
                    raceData.append({'name': f'R{raceNumber} {LOC}', 'participants': len(horces),'startTime':startTime.isoformat(),'teams':horces})
                    self.addStartTime(startTime)
        return raceData 
            
    def getEntrants(self,id):
        horces = []
        raceCard = self.getRaceCard(id)
        startTime = self.convertTime(raceCard["advertisedStartTimeUtc"])
        for entrant in raceCard['runners']:
            if entrant["isScratched"] == False:
                NAME = entrant["runnerName"]
                ODDS = entrant['fluctuations']['current']
                horces.append({'name':NAME,'odds':ODDS})
        return horces,startTime