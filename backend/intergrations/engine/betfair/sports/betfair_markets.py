import requests
import json
from datetime import datetime,timezone,timedelta
from zoneinfo import ZoneInfo
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class betfair_markets(scraper):
    def __init__(self, attributes) -> None:
        super().__init__(attributes)

    def get_race_markets(self,market_id):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            # 'cookie': 'vid=eb8cbf85-0020-4f6b-83ee-d1aa00a8a6ed; bfsd=ts=1721810160652|st=p; betexPtk=betexLocale%3Den%7EbetexRegion%3DIRL; language=en; locale=en; _gcl_au=1.1.1646991771.1721810164; _ga=GA1.3.201790113.1721810164; _gid=GA1.3.622865754.1721810164; storageSSC=lsSSC%3D1%3Bcookie-policy%3D1; _tgpc=be4e6b58-537a-50cd-bdbd-2a5464abd849; _fbp=fb.2.1721810165834.603178854472767451; exp=ex; _gat=1; _tguatd=eyJzYyI6IihkaXJlY3QpIn0=; _tgidts=eyJzaCI6ImQ0MWQ4Y2Q5OGYwMGIyMDRlOTgwMDk5OGVjZjg0MjdlIiwiY2kiOiIyMGMxOWYwNS0xYjc3LTVlMGMtODM0NC00ZmRhNDcxM2FkYjgiLCJzaSI6IjZhYjNkOWQyLWVhNzUtNWMxMC05N2JjLWFlOTYwMTVmMzlhZiJ9; __cf_bm=ydZPkr.1hllgmqNUs9BxcdvTD2FR8z7ZZPvsGoiuVKM-1721884121-1.0.1.1-a1vRAwxeM7AaivXk7PASoj1B4f9fLctzTKmMBger0WPqDBJ1d2Gf6_t0_xYKeJzBIGW5r7jr43ebM69uof7uRQ; _tglksd=eyJzIjoiNmFiM2Q5ZDItZWE3NS01YzEwLTk3YmMtYWU5NjAxNWYzOWFmIiwic3QiOjE3MjE4ODMxOTMyOTgsInNvZCI6IihkaXJlY3QpIiwic29kdCI6MTcyMTgxMDE2NDk3NCwic29kcyI6ImMiLCJzb2RzdCI6MTcyMTg4NDE2OTgwNn0=; _tgsid=eyJscGQiOiJ7XCJscHVcIjpcImh0dHBzOi8vd3d3LmJldGZhaXIuY29tLmF1JTJGZXhjaGFuZ2UlMkZwbHVzJTJGXCIsXCJscHRcIjpcIkJldGZhaXIlRTIlODQlQTIlMjAlQzIlQkIlMjBXb3JsZCVFMiU4MCU5OXMlMjBCaWdnZXN0JTIwQmV0dGluZyUyMEV4Y2hhbmdlXCIsXCJscHJcIjpcIlwifSIsInBzIjoiYjllZTA0YzQtMzNjNC00Y2I1LThjYmItYTkzOTIwNTUyYjUyIiwicHZjIjoiMiIsInNjIjoiNmFiM2Q5ZDItZWE3NS01YzEwLTk3YmMtYWU5NjAxNWYzOWFmOi0xIiwiZWMiOiI2IiwicHYiOiIxIiwidGltIjoiNmFiM2Q5ZDItZWE3NS01YzEwLTk3YmMtYWU5NjAxNWYzOWFmOjE3MjE4ODMxOTY1ODU6LTEifQ==; _uetsid=7c606c904a3611efaed271b67ecb5858; _uetvid=7c607d804a3611efb8fe890dcb1e2bfb; _rdt_uuid=1721810169442.35ceb11b-e7d3-4231-ac50-3892f72a516e',
            'dnt': '1',
            'origin': 'https://www.betfair.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.betfair.com.au/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        }

        response = requests.get(
            f'https://ero.betfair.com.au/www/sports/exchange/readonly/v1/bymarket?_ak=nzIFcwyWhrlwYMrh&alt=json&currencyCode=AUD&locale=en&marketIds={market_id}&rollupLimit=25&rollupModel=STAKE&types=MARKET_STATE,MARKET_RATES,MARKET_DESCRIPTION,EVENT,RUNNER_DESCRIPTION,RUNNER_STATE,RUNNER_EXCHANGE_PRICES_BEST,RUNNER_METADATA,MARKET_LICENCE,MARKET_LINE_RANGE_INFO',
            headers=headers,
        )

        response = json.loads(response.text)
        return response

    def get_day_races(self):
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'cache-control': 'no-cache',
            # 'cookie': '__cf_bm=Ase05L3u0pCyNsndz8_jcHm2eLkSsdd_DoFPyjvYNLg-1721885407-1.0.1.1-jJRFU1F9TAxW5u3nIQaomupAjaiIZZ4PtKqLJCFK0JRej7wcL19JBdXm5MpVxzSO5ew13R5fkRmpBf5JAevGJg; vid=11c9864d-3f1e-467d-b524-06170d750265; vid=eeb05688-b8c4-4789-a924-ca855e7fb6e8; bfsd=ts=1721885414082|st=p; wsid=f75f9fa0-4a46-11ef-ab89-fa163e9defab; betexPtk=betexLocale%3Den%7EbetexRegion%3DIRL; language=en; locale=en; exp=ex; _ga=GA1.3.881478498.1721885416; _gid=GA1.3.515927438.1721885416; _gat=1; _tguatd=eyJzYyI6IihkaXJlY3QpIn0=; _tgpc=3ff920ad-54be-5ad2-bfa1-84e72213c706; _tgidts=eyJzaCI6ImQ0MWQ4Y2Q5OGYwMGIyMDRlOTgwMDk5OGVjZjg0MjdlIiwiY2kiOiIyNjBjMjA3NC05NmRiLTVkZTMtYTI3OC0wNWQ2Mjk3NTAyMjEiLCJzaSI6IjMzN2UyNjE1LWEyN2EtNTM3My1hOTM5LTI5Y2ZiODU1OGEwYyJ9; _tglksd=eyJzIjoiMzM3ZTI2MTUtYTI3YS01MzczLWE5MzktMjljZmI4NTU4YTBjIiwic3QiOjE3MjE4ODU0MTYwNTQsInNvZCI6IihkaXJlY3QpIiwic29kdCI6MTcyMTg4NTQxNjA1NCwic29kcyI6Im8iLCJzb2RzdCI6MTcyMTg4NTQxNjA1NH0=; _fbp=fb.2.1721885416586.16503425779822698; storageSSC=lsSSC%3D1%3Bcookie-policy%3D1; _uetsid=f9efc3f04a4611ef809b91b28ad3eecd; _uetvid=f9eff5c04a4611efb8406f8602a8e8e2; _rdt_uuid=1721885421185.a5c2dfee-3558-430e-816c-3c5600c2e983; _tgsid=eyJscGQiOiJ7XCJscHVcIjpcImh0dHBzOi8vd3d3LmJldGZhaXIuY29tLmF1JTJGZXhjaGFuZ2UlMkZwbHVzJTJGXCIsXCJscHRcIjpcIkJldGZhaXIlRTIlODQlQTIlMjAlQzIlQkIlMjBXb3JsZCVFMiU4MCU5OXMlMjBCaWdnZXN0JTIwQmV0dGluZyUyMEV4Y2hhbmdlXCIsXCJscHJcIjpcIlwifSIsInBzIjoiYTk2ZjlkZTctODY5NS00ZmIwLTk1MjAtYWUwMTYwNjg3NmM5IiwicHZjIjoiMSIsInNjIjoiMzM3ZTI2MTUtYTI3YS01MzczLWE5MzktMjljZmI4NTU4YTBjOi0xIiwiZWMiOiI0IiwicHYiOiIxIiwidGltIjoiMzM3ZTI2MTUtYTI3YS01MzczLWE5MzktMjljZmI4NTU4YTBjOjE3MjE4ODU0MTkzOTk6LTEifQ==',
            'dnt': '1',
            'origin': 'https://www.betfair.com.au',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'referer': 'https://www.betfair.com.au/',
            'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
            'x-application': 'nzIFcwyWhrlwYMrh',
        }

        params = {
            '_ak': 'nzIFcwyWhrlwYMrh',
            'eventTypeId': '7',
            'navigationType': 'todayscard',
            'raceId': '33437480.0534',
        }

        response = requests.get(
            'https://apieds.betfair.com.au/api/eds/racing-navigation/v1',
            params=params,
            headers=headers,
        )
        response = response.text
        return json.loads(response)

    def aquireOdds(self,race_date_obj:timedelta):
        curr = datetime.now()
        if isinstance(race_date_obj, timedelta):
            curr += race_date_obj
            
        race_profile = []
        races = self.get_day_races()
        for race in races['races']:
            try:
                date_object = datetime.strptime(race['startTime'], '%Y-%m-%dT%H:%M:%S.%fZ')
                ajusted_date_object = date_object.replace(tzinfo=ZoneInfo('UTC'))
                ajusted_date_object = ajusted_date_object.astimezone(ZoneInfo('Australia/Sydney'))
                if 'AUS' in race['meetingName'] and date_object < (curr+timedelta(days=2)):
                    race_identifyer = {'race_id':race['winMarketId']}
                    entrants,venue_name = self.get_entrants(race_identifyer)
                    race_profile.append({'track':venue_name,'round':-1,'start_time':ajusted_date_object.isoformat(),'entrants':entrants, 'race_id':race_identifyer})
            except Exception as e:
                print(f'betfair: {e}')
                continue
        return race_profile
    
    def get_entrants(self,race_identifyer):
        race_data = self.get_race_markets(race_identifyer['race_id'])
        record_time = datetime.now()
        curr_race = []
        
        race_data = race_data['eventTypes'][0]['eventNodes'][0]
        venue_info = race_data['event']
        VENUE_NAME = venue_info['venue']
        entrants = race_data['marketNodes'][0]['runners']
        for entrant in entrants:
            NAME = "".join((entrant['description']['runnerName'].split('. ')[1]))
            TOTAL_PRICE = 0
            try:
                if 'availableToBack' in entrant['exchange']:
                    for price in entrant['exchange']['availableToBack']:
                        TOTAL_PRICE += price['price']
                    curr_race.append({'name':NAME,'market_size':TOTAL_PRICE/len(entrant['exchange']['availableToBack']),'record_time':record_time.isoformat()})
            except Exception as e:
                print(f'betfair: {e}')
                continue
        return curr_race,VENUE_NAME