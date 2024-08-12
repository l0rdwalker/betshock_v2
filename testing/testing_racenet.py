import requests


headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'en-AU,en-US;q=0.9,en-GB;q=0.8,en;q=0.7',
    'cache-control': 'no-cache',
    'dnt': '1',
    'origin': 'https://www.racenet.com.au',
    'pragma': 'no-cache',
    'priority': 'u=1, i',
    'referer': 'https://www.racenet.com.au/',
    'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
}

while True:
    response = requests.get(
        'https://puntapi.com/odds/au/event/1691579?betTypes=fixed-win,tote-win,exchange-win,exchange-win-lay&priceFluctuations=50&type=best,bookmaker&bookmaker=ubet,sportsbet,bet365,betm,ladbrokes,betfair,betfair,boombet,tabtouch,pointsbet,neds,racenetstandard',
        headers=headers,
    )
    print(response.text)