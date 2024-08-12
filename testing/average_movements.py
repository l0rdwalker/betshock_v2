import matplotlib.pyplot as plt 
import numpy as np 
import math
import time
from datetime import datetime, timedelta
from backend.intergrations.engine.arbie.sports.database.databaseOperations import databaseOperations

database = databaseOperations()
database.initConnection()

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

def get_entrant_prices(database, entrant_id, race_id, platform_name, time_iterator:datetime):
    query = f"""
    SELECT odds.odds, odds.record_time
    FROM race
    JOIN track ON race.track_id = track.track_id
    JOIN entrant ON entrant.race_id = race.race_id
    JOIN odds ON odds.entrant_id = entrant.entrant_id
    WHERE entrant.entrant_id = {entrant_id}
    AND race.race_id = {race_id}
    AND odds.platform_name = '{platform_name}'
    AND odds.record_time < '{time_iterator.isoformat()}'
    ORDER BY record_time DESC
    LIMIT 1;
    """
    return database.pushQuery(query)

def get_market_prices(database, entrant_id, time_iterator:datetime):
    query = f"""
    SELECT price, record_time 
        FROM market_conditions 
    WHERE 
        entrant_id = {entrant_id} AND 
        record_time < '{time_iterator.isoformat()}' 
    ORDER BY record_time DESC
    LIMIT 1;
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

race_id = 1684

while True:
    plt.clf()  # Clear the current figure
    curr_time = datetime.now()
    
    entrants = get_entrant_ids(database, race_id)
    platforms = get_platform_names(database, race_id)
    entrant_timeseries = []
    
    start_time = get_start_time(database,race_id)[0][0]
    end_time = get_end_time(database,race_id)[0][0]
    if curr_time < end_time:
        end_time = curr_time
    
    for entrant in entrants:
        if not is_entrant_scratched(database, entrant[0]):
            time_iterator = start_time
            betfair_prices = []
            while time_iterator < end_time:
                current_market_price = get_market_prices(database,entrant[0],time_iterator)
                if len(current_market_price) == 0:
                    time_iterator += timedelta(minutes=5)
                    continue
                betfair_prices.append((current_market_price[0][0],time_iterator))
                time_iterator += timedelta(minutes=5)
                
            time_iterator = start_time
            all_platforms = []
            for platform in platforms:
                local_time_series = []
                while time_iterator < end_time:
                    odds_price = get_entrant_prices(database,entrant[0],race_id,platform[0],time_iterator)
                    if len(odds_price) == 0:
                        time_iterator += timedelta(minutes=5)
                        continue
                    local_time_series.append((odds_price[0],time_iterator))
                    time_iterator += timedelta(minutes=5)
                if len(local_time_series) > 0:
                    all_platforms.append(local_time_series)
            
            average_market = []
            for idx in range(0,len(all_platforms[0])):
                average_market.append([0,0])
            
            for entry_idx in range(0,len(average_market)):
                count = 0
                for platform_idx_series in range(0,len(all_platforms)):
                    average_market[entry_idx][0] += all_platforms[platform_idx_series][entry_idx][0][0]
                    average_market[entry_idx][1] = all_platforms[platform_idx_series][entry_idx][1]
                    count += 1
                average_market[entry_idx][0] = average_market[entry_idx][0]/count
                
            entrant_timeseries.append([average_market,betfair_prices,entrant[1]])
                
    height = math.ceil(len(entrant_timeseries) / 2)
    width = 2
    fig_height = height * 5  # Adjust this multiplier to increase the height of the figure

    fig, axs = plt.subplots(height, width, figsize=(15, fig_height))
    axs = axs.flatten()  # Flatten in case axs is a 2D array
    
    for idx, entrant in enumerate(entrant_timeseries):
        if not entrant:
            continue
        average_series = entrant[0]
        berfair = entrant[1]
        horse_name = entrant[2]
        
        average_odds = []
        average_times = []
        for entry in average_series:
            average_odds.append(entry[0])
            average_times.append(entry[1])
        axs[idx].plot(average_times, average_odds, label="average", marker='o')
            
        betfair_odds = []
        betfair_times = []
        for entry in berfair:
            betfair_odds.append(entry[0])
            betfair_times.append(entry[1])
        axs[idx].plot(betfair_times, betfair_odds, label="betfair", marker='o')
            
            
        axs[idx].set_title(horse_name)
        axs[idx].legend()

    fig.tight_layout()
    plt.show()

    time.sleep(10)
    print('reset')
