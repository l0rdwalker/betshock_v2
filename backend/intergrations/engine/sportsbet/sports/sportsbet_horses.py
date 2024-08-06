import requests
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class sportsbet_horses(scraper):
    def __init__(self,attributes,database,router) -> None:
        super().__init__(attributes,database,router)
        self.marketTypes = ['Win or Place']
        self.flex_dates = True

    def getter(self,url):
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "gwapi.sportsbet.com.au",
            "accept-encoding": "gzip"
        }
        responce = self.router.perform_get_request(
            platform=self.platformName,
            url=url,
            headers=headers
        )
        return responce

    def conditionalDrillDown(self,array,key,searchValue):
        try:
            def compareItems(subject,searchTerms):
                if isinstance(searchTerms, list):
                    return subject in searchTerms
                else:
                    return searchTerms == subject
            for item in array:
                testElement = item[key]
                if compareItems(testElement,searchValue):
                    return item
        except Exception as e:
            return None

    def get_all_meets(self,race_date_obj:timedelta):
        set_date = datetime.now()
        if isinstance(race_date_obj,timedelta):
            set_date += race_date_obj
        
        todaysDate = (set_date).strftime("%Y-%m-%d")
        races = []
        try:
            data = self.getter(f"https://gwapi.sportsbet.com.au/sportsbook-racing/Sportsbook/Racing/AllRacing/{todaysDate}")
            if data == None:
                return races
            data = data['dates'][0]['sections']
            meetings = self.conditionalDrillDown(data,'raceType','horse')['meetings']
            for meeting in meetings:
                if meeting['regionName'] == 'Australia':
                    for event in meeting['events']:
                        try:
                            race_identidyer = {'race_id':event['httpLink']}
                            ENTRANTS = self.get_entrants(race_identidyer)
                            if ENTRANTS == None:
                                continue
                            if (len(ENTRANTS) > 0):
                                START_TIME = datetime.fromtimestamp(event['startTime'])
                                races.append(self.create_race_entry(
                                    track_name=meeting['name'],
                                    round=event['raceNumber'],
                                    start_time=START_TIME,
                                    entrants=ENTRANTS,
                                    race_identifyer=race_identidyer
                                ))
                        except Exception as e:
                            self.local_print(e)
        except Exception as e:
            self.local_print(e)
        return races

    def get_entrants(self,race_identidyer):
        horses = []
        markets = self.getter(f'https://gwapi.sportsbet.com.au/sportsbook-racing/{race_identidyer["race_id"]}')
        if markets == None:
            return horses
        
        markets = markets['markets']
        record_time = datetime.now()
        
        try:
            entrants = self.conditionalDrillDown(markets,'name',self.marketTypes)['selections']
        except:
            return None
        
        for hourse in entrants: 
            HOURSENAME = hourse['name']
            prices = self.conditionalDrillDown(hourse['prices'],'priceCode','L')
            if prices == None:
                return None
            if ('winPrice' in prices):
                WIN_ODDS = self.conditionalDrillDown(hourse['prices'],'priceCode','L')['winPrice']
                horses.append(self.create_entrant_entry(
                    entrant_name=HOURSENAME,
                    odds=WIN_ODDS,
                    scratched=(hourse['result'] == 'V'),
                    record_time=record_time
                ))
        return horses