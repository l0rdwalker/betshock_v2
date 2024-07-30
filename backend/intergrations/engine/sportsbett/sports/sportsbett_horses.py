import requests
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class sportsbett_horses(scraper):
    def __init__(self,attributes,database) -> None:
        super().__init__(attributes,database)
        self.marketTypes = ['Win or Place']
        self.flex_dates = True

    def getter(welf,url):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "gwapi.sportsbet.com.au",
            "accept-encoding": "gzip"
        }
        data = requests.get(url, headers=headers).text
        return json.loads(data)

    def conditionalDrillDown(self,array,key,searchValue):
        def compareItems(subject,searchTerms):
            if isinstance(searchTerms, list):
                return subject in searchTerms
            else:
                return searchTerms == subject
        for item in array:
            testElement = item[key]
            if compareItems(testElement,searchValue):
                return item
            
    def convertTime(self,timeTxt):
        startTime = datetime.fromtimestamp(timeTxt,tz=timezone.utc)
        startTime = startTime.astimezone(ZoneInfo("Australia/Sydney"))
        startTime = startTime.replace(tzinfo=None)    
        return startTime

    def aquireOdds(self,race_date_obj:timedelta):
        set_date = datetime.now()
        if isinstance(race_date_obj,timedelta):
            set_date += race_date_obj
        
        todaysDate = (set_date).strftime("%Y-%m-%d")
        races = []
        try:
            data = self.getter(f"https://gwapi.sportsbet.com.au/sportsbook-racing/Sportsbook/Racing/AllRacing/{todaysDate}")['dates'][0]['sections']
            meetings = self.conditionalDrillDown(data,'raceType','horse')['meetings']
            for meeting in meetings:
                if meeting['regionName'] == 'Australia':
                    for event in meeting['events']:
                        try:
                            race_identidyer = {'race_id':event['httpLink']}
                            
                            teams = self.get_entrants(race_identidyer)
                            if (len(teams) > 0):
                                startTime = self.convertTime(event['startTime'])
                                races.append({'name': meeting['name'], 'round': event['raceNumber'],'start_time': startTime.isoformat(),'entrants':teams, 'race_id':race_identidyer})
                        except Exception as e:
                            self.local_print(e)
        except Exception as e:
            self.local_print(e)
        return races

    def get_entrants(self,race_identidyer):
        horses = []
        markets = self.getter(f'https://gwapi.sportsbet.com.au/sportsbook-racing/{race_identidyer["race_id"]}')['markets']
        record_time = datetime.now()
        for hourse in self.conditionalDrillDown(markets,'name',self.marketTypes)['selections']: 
            HOURSENAME = hourse['name']
            prices = self.conditionalDrillDown(hourse['prices'],'priceCode','L')
            if ('winPrice' in prices):#winPrice placePrice
                WIN_ODDS = self.conditionalDrillDown(hourse['prices'],'priceCode','L')['winPrice']
                horses.append({'name':HOURSENAME,'odds':WIN_ODDS,'scratched':hourse['result'] == 'V', 'record_time':record_time.isoformat()})
        return horses