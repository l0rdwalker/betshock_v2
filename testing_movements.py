import matplotlib.pyplot as plt 
import numpy as np 
import math
import time
from datetime import datetime, timedelta
from backend.intergrations.engine.arbie.sports.database.databaseOperations import databaseOperations


#data = [[215,81,46],[103,35,31],[99,41,27],[82,1.75,2],[78,67,35],[76,2.25,2.35],[75,6,7],[74,71,67],[63,71,34]]
#
#count = 1
#sorted_by_odds = sorted(data, key=lambda x: x[1])
#for entry in sorted_by_odds:
#    entry.append(count)
#    count += 1
#
#sorted_by_market = sorted(sorted_by_odds, reverse=True, key=lambda x: x[0])
#sort_by_new_odds = sorted(sorted_by_odds, key=lambda x: x[2])
#predicted_movements = []
#
#for odds_idx in range(0,len(sorted_by_odds)):
#    for shifted_odds_idx in range(0,len(sorted_by_market)):
#        odds_entry = sorted_by_odds[odds_idx]
#        market_entry = sorted_by_market[shifted_odds_idx]
#        if odds_entry[3] == market_entry[3]:
#            if odds_idx < shifted_odds_idx:
#                predicted_movements.append(['up',sorted_by_odds[odds_idx][1]<sorted_by_odds[odds_idx][2]])
#            elif odds_idx > shifted_odds_idx:
#                predicted_movements.append(['down',sorted_by_odds[odds_idx][1]>sorted_by_odds[odds_idx][2]])
#            else:
#                predicted_movements.append(['n/a',sorted_by_odds[odds_idx][1]==sorted_by_odds[odds_idx][2]])
#            break
print('epic')

database = databaseOperations()
database.initConnection()

def get_all_races(database):
    query = f"""
        SELECT race.race_id FROM race WHERE start_time < NOW() AND DATE(start_time) = DATE(NOW()) ORDER BY start_time ASC;
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

def get_market_prices(database, entrant_id):
    query = f"""
    SELECT price, record_time FROM market_conditions WHERE entrant_id = {entrant_id} ORDER BY record_time ASC;
    """
    return database.pushQuery(query)

def get_start_time(database,race_id):
    query = f"""
        SELECT record_time FROM 
            race JOIN entrant
            ON race.race_id = entrant.race_id
            JOIN market_conditions
            ON market_conditions.entrant_id = entrant.entrant_id
        WHERE race.race_id = {race_id}
        ORDER BY record_time ASC LIMIT 1;
    """
    return database.pushQuery(query)

def get_end_time(database,race_id):
    query = f"""
        SELECT record_time FROM 
            race JOIN entrant
            ON race.race_id = entrant.race_id
            JOIN market_conditions
            ON market_conditions.entrant_id = entrant.entrant_id
        WHERE race.race_id = {race_id}
        ORDER BY record_time DESC LIMIT 1;
    """
    return database.pushQuery(query)

def get_recent_known_market(database,entrant_id,curr_time:datetime):
    query = f"""
        SELECT total FROM
        (SELECT entrant_id,sum(price) as total FROM market_conditions WHERE entrant_id = {entrant_id} AND record_time < '{curr_time.isoformat()}'
        GROUP BY entrant_id) as sub; 
        
    """
    return database.pushQuery(query)

def get_current_odds(database:databaseOperations,entrant_id,time:datetime):
    query = f"""
        SELECT odds FROM odds WHERE entrant_id = {entrant_id}
        AND record_time < '{time.isoformat()}' ORDER BY record_time DESC, odds DESC LIMIT 1;
        
        --AND record_time < '{time.isoformat()}' 
        --BY record_time DESC,
    """
    return database.pushQuery(query)

races = get_all_races(database)

for race in races:
    implyed_fav = {}
    try:
        race_id = race[0]
        curr_time = datetime.now()
        entrants = get_entrant_ids(database, race_id)

        curr = get_start_time(database,race_id)[0][0] + timedelta(minutes=1)
        end_time = get_end_time(database,race_id)[0][0]
        while curr < end_time:
            all_prices = []
            for entrant in entrants:
                price = get_recent_known_market(database,entrant[0],curr)[0][0]
                all_prices.append([price,entrant[0]])
            all_prices = sorted(all_prices, reverse=True, key=lambda x: x[0])
            count = 1
            for price in all_prices:
                price.append(count)
                count += 1
            for price in all_prices:
                if not price[1] in implyed_fav:
                    implyed_fav[price[1]] = [[price[2]],[curr]]
                else:
                    implyed_fav[price[1]][0].append(price[2])
                    implyed_fav[price[1]][1].append(curr)
            curr += timedelta(minutes=1)
            
        selected_odds = []
        for horse_name, series_data in implyed_fav.items():
            dates = series_data[1]
            positions = series_data[0]
            prev_pos = None
            for idx in range(0,len(positions)):
                curr_pos = positions[idx]
                if prev_pos == None:
                    prev_pos = curr_pos
                else:
                    if prev_pos - curr_pos > 1:
                        odds = get_current_odds(database,horse_name,dates[idx]-timedelta(minutes=5))[0][0]
                        selected_odds.append(odds)
                        break
                    elif not idx+1 < len(positions):
                        odds = get_current_odds(database,horse_name,dates[idx]-timedelta(minutes=5))[0][0]
                        selected_odds.append(odds)      
        i_p = 0
        for odds in selected_odds:
            i_p += 1/odds
        print(i_p,race_id)
    except Exception as e:
        continue
database.closeConnection()