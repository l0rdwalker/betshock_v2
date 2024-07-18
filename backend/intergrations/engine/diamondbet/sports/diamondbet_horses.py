import requests
from datetime import datetime
import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_scraper import scraper

class diamondbet_horses(scraper):
    def getVenues(self,date:datetime):
        url = "https://api.diamondbet.com.au/api/v2/combined/meetings/races"

        querystring = {
            "date": date.strftime("%Y-%m-%d"),
            "order": "true"
        }

        headers = {
            "user-agent": "Android google Pixel 3 152fb996a0625f03",
            "accept-encoding": "gzip",
            "website-version": "26.3.0",
            "host": "api.diamondbet.com.au"
        }

        response = requests.get(url, headers=headers, params=querystring)
        response = response.text
        response = json.loads(response)
        return response

    def getRaceCard(self,id):
        url = "https://api.diamondbet.com.au/api/v2/combined/race/selections"

        querystring = { "race_id": f"{id}" }

        headers = {
            "user-agent": "Android google Pixel 3 152fb996a0625f03",
            "accept-encoding": "gzip",
            "website-version": "26.3.0",
            "host": "api.diamondbet.com.au"
        }

        response = requests.get(url, headers=headers, params=querystring)
        response = response.text
        response = json.loads(response)
        return response

    def aquireOdds(self):
        raceData = []
        venues = self.getVenues(datetime.now())['data']
        for venue in venues:
            if venue['country'] == 'AU' and venue['type'] == 'R':
                LOC = ' '.join(word.capitalize() for word in venue['name'].split())
                for race in venue['races']:
                    try:
                        startTime = datetime.strptime(race['start_date'], '%Y-%m-%d %H:%M:%S')
                        raceNumber = race['number']
                        horces = self.getEntrants(race['id'])
                        raceData.append({'name': f'R{raceNumber} {LOC}', 'participants': len(horces),'startTime':startTime.isoformat(),'teams':horces})
                        self.addStartTime(startTime)
                    except:
                        continue
        return raceData
                    
    def getEntrants(self,id):
        horces = []
        entrants = self.getRaceCard(id)['data']['selections']
        for entrant in entrants:
            if 'not' in entrant["selection_status"]:
                NAME = entrant['name']
                winID = entrant['win_fixed']
                index = len(entrant['prices'])-1
                
                keyId = None
                for key,odd in entrant['prices'].items():
                    if keyId == None:
                        keyId = key
                    elif int(key) > int(keyId):
                        keyId = key
                
                ODDS = entrant['prices'][key]['win_odds']
                horces.append({'name':NAME,'odds':ODDS})

        return horces