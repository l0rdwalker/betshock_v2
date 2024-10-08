import requests
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class boombet_horses(scraper):
    def __init__(self, attributes, database, router) -> None:
        super().__init__(attributes, database, router)
        self.flex_dates = True
    
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
        response = self.router.perform_get_request(
            platform=self.platformName,
            url=url,
            headers=headers
        )
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
        response = self.router.perform_get_request(
            platform=self.platformName,
            url=url,
            headers=headers
        )
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

        response = self.router.perform_get_request(
            platform=self.platformName,
            url=url,
            headers=headers
        )
        
        return response
    
    def convertTime(self,timeTxt):
        startTime = datetime.fromisoformat(timeTxt)
        startTime = startTime.replace(tzinfo=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def get_all_meets(self,race_date_obj:timedelta):
        set_date = datetime.now()
        if isinstance(race_date_obj,timedelta):
            set_date += race_date_obj
        
        
        AustralianStates = ['ACT','NSW','NT','QLD','SA','TAS','VIC','WA']
        days = self.getVenues()
        currentDate = set_date
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
        
        race_profile = []
        for location in todaysData['raceMeetings']:
            try:
                if location['raceType'] == 4 and location['state'] in AustralianStates:
                    LOC = location['meetingName']
                    races = self.getRaces(dayCode,LOC)
                    for race in races['races']:
                        try:
                            ROUND = race['raceNumber']

                            race_identidyer = {'race_id':race['eventId']}

                            ENTRANTS = self.get_entrants(race_identidyer)
                            START_TIME = self.convertTime(race['jumpTime'][:-6])
                            race_profile.append(self.create_race_entry(
                                track_name=LOC,
                                round=ROUND,
                                entrants=ENTRANTS,
                                start_time=START_TIME,
                                race_identifyer=race_identidyer
                            ))
                        except Exception as e:
                            self.local_print(e)
            except Exception as e:
                self.local_print(e)
        return race_profile

    def get_entrants(self,race_identidyer):
        ENTRANTS = []
        raceCard = self.getRaceCard(race_identidyer['race_id'])
        if raceCard == None:
            return None
        
        record_time = datetime.now()
        for horce in raceCard['runners']:
            try:
                NAME = horce['name']
                ODDS = -1
                for odd in horce['odds']:
                    if odd['product']['betType'] == 'Win':
                        ODDS = odd['value']
                        break
                ENTRANTS.append(self.create_entrant_entry(
                    entrant_name=NAME,
                    odds=ODDS,
                    scratched=(horce['isEliminated'] == False),
                    record_time=record_time
                ))
            except Exception as e:
                self.local_print(e)
        return ENTRANTS