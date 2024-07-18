import requests
from datetime import datetime
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class betfair_horses(scraper):
    def getRace(self,id):
        url = "https://www.betfair.com.au/api/sports/exchange/readonly/v1/bymarket"

        querystring = {
            "currencyCode": "AUD",
            "locale": "en",
            "marketIds": id,#"1.224198224",
            "rollupLimit": "5",
            "rollupModel": "STAKE",
            "virtualise": "true",
            "types": "MARKET_STATE,MARKET_LICENCE,MARKET_RATES,MARKET_DESCRIPTION,EVENT,RUNNER_DESCRIPTION,RUNNER_STATE,RUNNER_METADATA,RUNNER_SP,RUNNER_EXCHANGE_PRICES_BEST,MARKET_LINE_RANGE_INFO"
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-application": "AYXCX3IlPt4vhUk3",
            "charset": "utf-8",
            "host": "www.betfair.com.au",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.2",
            "if-modified-since": datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
        }

        response = requests.get(url, headers=headers, params=querystring)
        return json.loads(response.text)['eventTypes'][0]['eventNodes'][0]['marketNodes'][0]['runners']

    def getAllMarkets(self):
        now = datetime.now()
        startOfDay = now.replace(day=1,hour=0,minute=0,second=0,microsecond=0)
        startOfDay = startOfDay.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        endOfDay = now.replace(day=1,hour=23,minute=59,second=59,microsecond=59)
        endOfDay = endOfDay.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

        url = "https://production.ausnav.online/nav"

        querystring = {
            "type": "screen",
            "name": "racing",
            "next2jump": "true",
            "today": "true"
        }

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-application": "AYXCX3IlPt4vhUk3",
            "charset": "utf-8",
            "host": "production.ausnav.online",
            "accept-encoding": "gzip",
            "user-agent": "okhttp/4.9.2",
            "if-modified-since": datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')
            }

        response = requests.get(url, headers=headers, params=querystring)
        return json.loads(response.text)

    def getHorces(self,id):
        horces = []
        raceData = self.getRace(id)
        for horse in raceData:
            name = horse['description']['runnerName'].split('.')
            HOURSENAME = name[len(name)-1].strip()
            for key,value in horse['exchange'].items():
                if key == 'availableToBack':
                    WIN_ODDS = self.getBestOdds(value)
                    horces.append({'name':HOURSENAME,'odds':WIN_ODDS})
                    break
        return horces

    def getBestOdds(self,data):
        price = None
        for entry in data:
            potentialPrice = float(entry['price'])
            if price == None:
                price = potentialPrice
            elif potentialPrice < price:
                price = potentialPrice
        return price

    def aquireOdds(self):
        return []
        races = []
        markets = self.getAllMarkets()
        for marketKey,market in markets['nextToJump'].items():
            for raceKey,race in market.items():
                for raceType in race:
                    if raceType['marketType'] == 'WIN' and raceType['racingType'] == 'Thoroughbred Racing':
                        NAME = f"R{raceType['raceNumber']} {raceType['venue']}"
                        HORCES = self.getHorces(raceType['id'])
                        startTime = datetime.fromisoformat(raceType['marketStartTime'].replace('Z', '+00:00'))
                        startTime = startTime.replace(tzinfo=None)
                        races.append({'name': NAME, 'participants': len(HORCES),'startTime':startTime.isoformat(),'teams':HORCES})
                        self.addStartTime(startTime)
        return races