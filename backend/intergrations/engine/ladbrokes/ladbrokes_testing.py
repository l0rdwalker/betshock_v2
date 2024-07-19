import requests
import json
from datetime import datetime,timezone
from zoneinfo import ZoneInfo

def get_day_meets():
    cur_date = datetime.now()
    headers = {
        'accept': '*/*',
        'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'dnt': '1',
        'if-modified-since': 'Fri, 19 Jul 2024 10:31:31 GMT',
        'origin': 'https://www.ladbrokes.com.au',
        'priority': 'u=1, i',
        'referer': 'https://www.ladbrokes.com.au/',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
    }

    params = {
        'date': cur_date.strftime("%Y-%m-%d"),
        'region': 'domestic',
        'timezone': 'Australia/Sydney',
    }

    response = requests.get('https://api.ladbrokes.com.au/v2/racing/meeting', params=params, headers=headers)
    return json.loads(response.text)

data = get_day_meets()
meet_ids = []
for event in data['meetings'].items():
    event = event[1]
    if (event['category_id'] == '4a2788f8-e825-4d36-9894-efd4baf1cfae'):

        print("test")