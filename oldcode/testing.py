from backend.intergrations.engine.arbie.sports.database.databaseOperations import databaseOperations
import matplotlib.pyplot as plt 
from datetime import datetime, timedelta

def get_races(database):
    query = """
    SELECT race.race_id, track.track_name
    FROM race
    JOIN track ON race.track_id = track.track_id
    WHERE DATE(race.start_time) > DATE(NOW());
    """
    return database.pushQuery(query)

def get_platform_names(database, race_id):
    query = f"""
    SELECT DISTINCT platform_name
    FROM race
    JOIN track ON race.track_id = track.track_id
    JOIN entrant ON entrant.race_id = race.race_id
    JOIN odds ON odds.entrant_id = entrant.entrant_id
    WHERE race.race_id = {race_id};
    """
    return database.pushQuery(query)

def get_entrant_ids(database, race_id):
    query = f"""
    SELECT DISTINCT entrant.entrant_id, horse.name
    FROM race
    JOIN track ON race.track_id = track.track_id
    JOIN entrant ON entrant.race_id = race.race_id
    JOIN odds ON odds.entrant_id = entrant.entrant_id
    JOIN horse ON horse.horse_id = entrant.horse_id
    WHERE race.race_id = {race_id};
    """
    return database.pushQuery(query)

def is_entrant_scratched(database, entrant_id):
    query = f"""
    SELECT entrant.is_scratched
        FROM race
        JOIN track ON race.track_id = track.track_id
        JOIN entrant ON entrant.race_id = race.race_id
        JOIN odds ON odds.entrant_id = entrant.entrant_id
    WHERE entrant.entrant_id = {entrant_id};
    """
    return database.pushQuery(query)[0][0]

def get_entrant_prices(database, entrant_id, race_id, platform_name):
    query = f"""
    SELECT odds.odds, odds.record_time
    FROM race
    JOIN track ON race.track_id = track.track_id
    JOIN entrant ON entrant.race_id = race.race_id
    JOIN odds ON odds.entrant_id = entrant.entrant_id
    WHERE entrant.entrant_id = {entrant_id}
    AND race.race_id = {race_id}
    AND odds.platform_name = '{platform_name}'
    ORDER BY record_time ASC;
    """
    return database.pushQuery(query)

def get_horse_name(database, entrant_id):
    query = f"""
    SELECT horse.name FROM
        entrant JOIN horse
            ON entrant.horse_id = horse.horse_id
        WHERE entrant.entrant_id = {entrant_id};
    """
    return database.pushQuery(query)[0][0]

database = databaseOperations()
database.initConnection()
    
races = get_races(database)
race_details = []

for race in races:
    race_id = race[0]
    track_name = race[1]
    platform_names = get_platform_names(database, race_id)
    entrant_ids = get_entrant_ids(database, race_id)
    entrant_price_details = []

    for entrant in entrant_ids:
        entrant_id = entrant[0]
        
        if is_entrant_scratched(database, entrant_id):
            continue
        platform_price_details = []
        num_prices = 0

        race_entrants_timeseries = []
        
        for platform in platform_names:
            platform_name = platform[0]
            prices = get_entrant_prices(database, entrant_id, race_id, platform_name)
            platform_price_details.append({'platform': platform_name, 'prices': prices})
            
            odds = []
            record_times = []
            num_prices = max(num_prices,len(prices))
            for entry in prices:
                if len(odds) >= 1:
                    odds.append(odds[len(odds)-1])
                    record_times.append(entry[1] - timedelta(seconds=1))
                if entry[0] != -1:
                    odds.append(entry[0])
                    record_times.append(entry[1])
                    
            race_entrants_timeseries.append([odds,record_times,platform_name])
        
        latest_time = None
        for entrant_timeseries in race_entrants_timeseries:
            last_time_entry = entrant_timeseries[1][len(entrant_timeseries[1])-1]
            if latest_time == None:
                latest_time = last_time_entry
            elif last_time_entry > latest_time:
                latest_time = last_time_entry
                
        for entrant_timeseries in race_entrants_timeseries:
            entrant_timeseries[0].append(entrant_timeseries[0][len(entrant_timeseries[0])-1])
            entrant_timeseries[1].append(latest_time)
            
            plt.plot(entrant_timeseries[1], entrant_timeseries[0], label=entrant_timeseries[2], **{'marker': 'o'})
        
        if num_prices > 1:
            plt.xlabel('Time (timestamp)')
            plt.ylabel('Odds')
            plt.title(f'Entrant Prices for Entrant ID: {entrant_id} in Race ID: {race_id}')
            plt.legend()
            plt.show()
        else:
            plt.clf()   

        entrant_price_details.append({'entrant_name': get_horse_name(database, entrant_id), 'entrant_id': entrant_id, 'platform_offerings': platform_price_details})

    track_details = database.get_round_and_track_name_by_id(race_id)
    race_details.append({'track': track_details[0], 'round': track_details[1], 'race_id': race_id, 'track_name': track_name, 'entrants': entrant_price_details})
    
database.closeConnection()

arbs = []
for race_instance in race_details:
    best_entrant_odds = []
    for entrant in race_instance['entrants']:
        best_price = None
        best_platform = None
        for platform_offers in entrant['platform_offerings']:
            platform_name = platform_offers['platform']
            for price in platform_offers['prices']:
                if best_price is None:
                    best_price = price
                    best_platform = platform_name
                if price[0] > best_price[0]:
                    best_price = price
                    best_platform = platform_name
        best_entrant_odds.append({'entrant_id': entrant['entrant_id'], 'name': entrant['entrant_name'], 'odds': best_price[0], 'platform': best_platform, 'ROI': 1 / best_price[0]})

    i_p = 0
    for best_price in best_entrant_odds:
        i_p += best_price['ROI']
    arbs.append({'race_id': race_instance['race_id'], 'track': race_instance['track'], 'round': race_instance['round'], 'i_p': i_p, 'options': best_entrant_odds})

STAKE = 500
bank = 0
wins = 0
loss = 0
for arb in arbs:
    if arb['i_p'] < 1:
        wins += 1
    else:
        loss += 1
    bank += (STAKE / arb['i_p']) - STAKE

print(f"percentage: {wins / (wins + loss)} amt: {bank}")



#data = "2.7, 6, 6.5, 8, 11, 11, 12, 13, 15, 19, 23, 26, 51, 71, 126"
#data = data.split(" ")
#for idx in range(0,len(data)):
#    data[idx] = float(data[idx])
#starting_price = [5.5, 2.9, 2.8, 19, 26, 12, 13, 41, 26, 41, 41, 41]
#highest = [5.5, 3.8, 4.2, 21.5, 26, 16, 21.5, 43, 51, 61, 71, 81, 101]
#data = starting_price

#data = [3, 5.2, 5.5, 6.5, 9.5, 11, 126, 126, 151]
#data = sorted(data)
#i_p = 0
#for entry in data:
#    i_p += 1/entry
#    print(i_p,1/entry,entry)
#print(i_p)


#arbitrage_sums = {
#    "Pakenham": {
#        "R1": 0.9774838893873888,
#        "R2": 1.0124144228498009,
#        "R3": 0.9466670636010056
#    },
#    "Sunshine Coast": {
#        "R1": 0.7657071722209816,
#        "R2": 0.8347985347985349,
#        "R3": 0.6752681533752564
#    },
#    "Grafton": {
#        "R1": 0.8564596191424296,
#        "R2": 0.8118106465749874,
#        "R3": 0.7497156941751799
#    },
#    "Hawkesbury": {
#        "R1": 0.950938712642747,
#        "R2": 0.8334012008541227,
#        "R3": 0.22772693979910463
#    },
#    "Hobart": {
#        "R1": 0.9608393598739559,
#        "R2": 0.9738429358571726,
#        "R3": 0.9351591624829391
#    },
#    "Carnarvon": {
#        "R1": 1.0114566666874938,
#        "R2": 0.9670505767577643,
#        "R3": 0.8774645786479649
#    },
#    "Port Augusta": {
#        "R1": 0.9165323582966736,
#        "R2": 0.775137168033343,
#        "R3": 0.851233638265015
#    }
#}
#
#stake = 500
#loss = 0
#win = 0
## Calculate minimum returns
#returns = []
#for location, race_data in arbitrage_sums.items():
#    for race, arbitrage_sum in race_data.items():
#        if arbitrage_sum > 1:
#            loss += 1
#        else:
#            win += 1
#        returns.append((stake / arbitrage_sum) - stake)
#print(sum(returns),win,loss,win/(win+loss))
#print(((sum(returns)/len(returns))*31)+sum(returns))