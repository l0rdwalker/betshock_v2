import requests
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
import json
import os
import sys
import re
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))
from abstract_database import database

class arbie_getResults(database):
    def __init__(self, attributes) -> None:
        super().__init__(attributes)
        self.operation = 'getResults'
    
    def getAllRaces(self,url):
        cookies = {
            '_cb': 'hejgcDS12WsBTaYfv',
            'nc_aam_segs': 'asgmnt%3D16675898',
            'nk': '963329d201b0a984e01acbde152bdb11',
            '_ncid': '766aca3a3dc12c8323e6494b3bfc131e',
            '_fbp': 'fb.2.1704182246448.1473864599',
            'AMCVS_5FE61C8B533204850A490D4D%40AdobeOrg': '1',
            'DM_SitId1581': '1',
            'DM_SitId1581SecId13127': '1',
            'AMCV_5FE61C8B533204850A490D4D%40AdobeOrg': '1585540135%7CMCIDTS%7C19751%7CMCMID%7C54474334304258673054252936408577865429%7CMCAAMLH-1707022542%7C8%7CMCAAMB-1707022542%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1706424942s%7CNONE%7CvVersion%7C4.4.0',
            '_ncg_id_': '18d4e6c480d-b42653bd-86a1-4804-9beb-3d22b130e1c8',
            'nearSessionCookie': '0.01195359861034695',
            '_ncg_sp_ses.b006': '*',
            '_chartbeat2': '.1704182243700.1706423943787.0000000000000011.DR40rzCxb1WPpCUyoCVQdOIB86ACT.1',
            '_cb_svref': 'external',
            'utag_main': 'v_id:018cc92d66eb0096cf8e049755200506f003a06700978$_sn:4$_se:9$_ss:0$_st:1706425744473$vapi_domain:racenet.com.au$ses_id:1706423622192%3Bexp-session$_pn:9%3Bexp-session',
            '_ncg_sp_id.b006': '57438b71-03cb-48d5-a5a4-8ef8ce6f2bea.1704182246.4.1706423945.1706419459.7050e570-4a03-4cfb-a470-e83dbc21973a',
            'nol_fpid': '9zov3ronktwjhzuqiac5vgowbil2o1704182245|1704182245658|1706423944649|1706423944691',
            'FCNEC': '%5B%5B%22AKsRol-9E268VKDss4fb7tsvX1pbb2htokzrLPozQjlcdoDZpOX0y8vzEGM3IjwC2VqQ2kSLuK5Nf_n5EcpNsD6Z_dpzem6AJnzBwFYM4I9JtGkpzNOkGDvSQRFtf_lMbqWhltjCK73tZXu8g-eXO9qCIRTBwxh4AQ%3D%3D%22%5D%5D',
            '__gads': 'ID=6c65ddc87a5050d3:T=1704182245:RT=1706423944:S=ALNI_MZ3HLxdxJSuv7ikDqfz6mggAFNQ4A',
            '__gpi': 'UID=00000ccfeaa50e1b:T=1704182245:RT=1706423944:S=ALNI_MYpyEK3Z8bhumyAbKivQLrd9oAtAg',
            '_rdt_uuid': '1704182246314.af6e57ce-ab5e-42c7-8da6-eb53eaa69ec3',
        }

        headers = {
            'authority': 'www.racenet.com.au',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'cache-control': 'max-age=0',
            'dnt': '1',
            'if-none-match': 'W/"e8976-BdCBAZqStXWroZbfMBbDGa/AQ0U"',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        response = requests.get(
            url,
            cookies=cookies,
            headers=headers,
        )
        return response.text

    def getDateSpecificInfo(self,date:datetime):
        headers = {
            'authority': 'puntapi.com',
            'accept': '*/*',
            'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
            'authorization': 'Bearer none',
            'content-type': 'application/json',
            'dnt': '1',
            'origin': 'https://www.racenet.com.au',
            'priority': 'u=1, i',
            'referer': 'https://www.racenet.com.au/',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-vch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        date = date.strftime('%Y-%m-%d')
        params = {
            'operationName': 'meetingsIndexByStartEndDate',
            'variables': '{"startDate":"'+date+'","endDate":"'+date+'","limit":100}',
            'extensions': '{"persistedQuery":{"version":1,"sha256Hash":"998212fede87c9261e0f18e9d8ced2ed04a915453dcd64ae1b5cf5a72cf25950"}}',
        }

        response = requests.get('https://puntapi.com/graphql-horse-racing', params=params, headers=headers)
        return json.loads(response.text)

    def findRow(self,data,key,value):
        for row in data:
            if row[key] == value:
                return row
        return None

    def parsePageData(self,html_content,venue:str,events):
        venue = venue.replace('-',' ')
        venueSplit = venue.split(' ')
        for x in range(0,len(venueSplit)):
            venueSplit[x] = venueSplit[x].capitalize()
        venue = ' '.join(venueSplit)
        
        startTimes = {}
        for event in events:
            time = datetime.fromisoformat(event['startTime'].rstrip('Z'))
            time = time.replace(tzinfo=ZoneInfo("UTC"))
            time = time.astimezone(ZoneInfo("Australia/Sydney"))
            time = time.replace(tzinfo=None)   
            startTimes[event['eventNumber']] = time
        
        races = []
        round = 0
        soup = BeautifulSoup(html_content, 'html.parser')
        try:
            errorNoneFound = soup.find('h1',class_='results-index__title')
            if (errorNoneFound == None):
                elements = soup.find_all('div', class_='results__all-races-container')
                for element in elements:
                    horces = []
                    htmlHorceElements = element.find_all('div',class_='selection-result')
                    round += 1
                    winner = None
                    for htmlHorceElement in htmlHorceElements:
                        name = htmlHorceElement.find(attrs={"data-analytics": "Results : Horse Profile"}).text.replace(".","")
                        name = re.sub(r'[0-9]', '', name).strip()
                        if winner == None:
                            name = name.replace('"','')
                            name = name.replace("'",'')
                            winner = name
                            break
                    if not winner == None:
                        races.append({'winner':winner,'name': f'R{round} {venue}', 'startTime':f'{startTimes[round].isoformat()}'})
        except:
            print('error')
        return races
    
    def getWinners(self):
        indexDate = datetime.now()
        raceData = []
        try:
            try:
                races = self.findRow(self.getDateSpecificInfo(indexDate)['data']['meetingsGrouped'],'group','Australia')
                if not races == None:
                    for meeting in races['meetings']:
                        venue = meeting['venue']['slug']
                        url = f"https://www.racenet.com.au/results/horse-racing/{meeting['slug']}/all-races"
                        raceData.extend(self.parsePageData(self.getAllRaces(url),meeting['venue']['slug'],meeting['events']))
                indexDate += timedelta(days=1)
            except:
                indexDate += timedelta(days=1)
        except:
            print('error')
        return raceData
    
    def init(self,data=None):
        data = self.getWinners()
        requests.post('http://127.0.0.1:8081/setWinners', json=data)