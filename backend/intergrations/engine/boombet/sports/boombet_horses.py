import requests
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class boombet_horses(scraper):
    def getVenues(self):
        url = "https://sb-saturn.azurefd.net/api/v2.0/race/GetRaceMeetingsAll"
        headers = {
            "sp-authtoken": "",
            "sp-deviceid": "f4a49a8f-4adf-4de3-9429-8178d84cbe59",
            "sp-platformid": "1",
            "sp-clientversion": "2060000303",
            "sp-deviceinfo": "Physical/Google/Pixel 3/Pixel 3",
            "sp-osinfo": "Android/12",
            "accept": "application/json",

            
            "accept-encoding": "identity",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 3 Build/SP1A.210812.016.B1)",
            "host": "sb-saturn.azurefd.net"
        }
        response = requests.get(url, headers=headers)
        response = response.text
        response = json.loads(response)
        return response

    def getRaces(self,day,location):
        url = f"https://sb-saturn.azurefd.net/api/v2.0/race/GetRaceMeetingCard/{day}/T/{location}"
        headers = {
            "sp-authtoken": "",
            "sp-deviceid": "f4a49a8f-4adf-4de3-9429-8178d84cbe59",
            "sp-platformid": "1",
            "sp-clientversion": "2060000303",
            "sp-deviceinfo": "Physical/Google/Pixel 3/Pixel 3",
            "sp-osinfo": "Android/12",
            "accept": "application/json",
            "accept-encoding": "identity",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 3 Build/SP1A.210812.016.B1)",
            "host": "sb-saturn.azurefd.net"
        }
        response = requests.get(url, headers=headers)
        response = response.text
        response = json.loads(response)
        return response

    def getRaceCard(self,id):
        url = f"https://sb-saturn.azurefd.net/api/v2.0/race/event/{id}/1"

        headers = {
            "sp-authtoken": "",
            "sp-deviceid": "f4a49a8f-4adf-4de3-9429-8178d84cbe59",
            "sp-platformid": "1",
            "sp-clientversion": "2060000303",
            "sp-deviceinfo": "Physical/Google/Pixel 3/Pixel 3",
            "sp-osinfo": "Android/12",
            "accept": "application/json",
            "accept-encoding": "identity",
            "user-agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel 3 Build/SP1A.210812.016.B1)",
            "host": "sb-saturn.azurefd.net"
        }

        response = requests.get(url, headers=headers)
        response = response.text
        response = json.loads(response)
        return response
    
    def convertTime(self,timeTxt):
        startTime = datetime.fromisoformat(timeTxt)
        startTime = startTime.replace(tzinfo=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def aquireOdds(self):
        AustralianStates = ['ACT','NSW','NT','QLD','SA','TAS','VIC','WA']
        days = self.getVenues()
        currentDate = datetime.now()
        todaysData = None
        for day in days:
            date_string_no_tz = day['date'][:-6]
            dayDatetime = datetime.fromisoformat(date_string_no_tz)
            if currentDate.date() == dayDatetime.date():
                todaysData = day
                break
        
        if todaysData == None:
            raise Exception('Current day not found')
        dayCode = todaysData['day']
        
        raceData = []
        for location in todaysData['raceMeetings']:
            if location['raceType'] == 4 and location['state'] in AustralianStates:
                LOC = location['meetingName']
                races = self.getRaces(dayCode,LOC)
                for race in races['races']:
                    raceNumber = race['raceNumber']
                    raceID = race['eventId']
                    horces = self.getEntrants(raceID)
                    startTime = self.convertTime(race['jumpTime'][:-6])
                    raceData.append({'name': f'R{raceNumber} {LOC}', 'participants': len(horces),'startTime':startTime.isoformat(),'teams':horces})
                    self.addStartTime(startTime)

        return raceData

    def getEntrants(self,id):
        horces = []
        raceCard = self.getRaceCard(id)
        for horce in raceCard['runners']:
            if horce['isEliminated'] == False:
                NAME = horce['name']
                ODDS = None
                for odd in horce['odds']:
                    if odd['product']['betType'] == 'Win':
                        ODDS = odd['value']
                        break
                horces.append({'name':NAME,'odds':ODDS})
        return horces