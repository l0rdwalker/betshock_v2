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

race_id = 1825

while True:
    plt.clf()  # Clear the current figure
    curr_time = datetime.now()
    entrants = get_entrant_ids(database, race_id)
    platforms = get_platform_names(database, race_id)
    entrant_timeseries = []
    for entrant in entrants:
        entrant_platform_prices = []
        if not is_entrant_scratched(database, entrant[0]):
            platforms_timeseries = []
            for platform in platforms:
                prices = get_entrant_prices(database, entrant[0], race_id, platform[0])
                odds = []
                record_times = []
                for entry in prices:
                    if len(odds) >= 1:
                        odds.append(odds[len(odds)-1])
                        record_times.append(entry[1] - timedelta(seconds=1))
                        odds.append(entry[0])
                        record_times.append(entry[1])
                    elif entry[0] != -1:
                        odds.append(entry[0])
                        record_times.append(entry[1])
                if len(odds) > 0:
                    record_times.append(curr_time)
                    odds.append(odds[len(odds)-1])
                platforms_timeseries.append([odds, record_times, platform[0]])
            entrant_platform_prices.append([platforms_timeseries, entrant[1]])
        entrant_timeseries.append(entrant_platform_prices)
    
    implyed_fav = {}
    for entrant in entrants:
        market_prices = get_market_prices(database,entrant[0])
        if len(market_prices) == 0:
            continue
        price_odds = []
        timesteps = []
        for market_price in market_prices:
            if len(price_odds) == 0:
                price_odds.append(market_price[0])
                timesteps.append(market_price[1])
            else:
                price_odds.append(price_odds[len(price_odds)-1])  
                timesteps.append(market_price[1] - timedelta(seconds=1))
                price_odds.append(market_price[0])
                timesteps.append(market_price[1])
        if not entrant[1] in implyed_fav:
            implyed_fav[entrant[1]] = [price_odds,timesteps]
                
    #implyed_fav = {}
    #curr = get_start_time(database,race_id)[0][0] + timedelta(minutes=1)
    #end_time = get_end_time(database,race_id)[0][0]
    #while curr < end_time:
    #    all_prices = []
    #    for entrant in entrants:
    #        price = get_recent_known_market(database,entrant[0],curr)
    #        if len(price) > 0:
    #            all_prices.append([price,entrant[1]])
    #    all_prices = sorted(all_prices, reverse=True, key=lambda x: x[0])
    #    count = 1
    #    for price in all_prices:
    #        price.append(count)
    #        count += 1
    #    for price in all_prices:
    #        if not price[1] in implyed_fav:
    #            implyed_fav[price[1]] = [[price[2]],[curr]]
    #        else:
    #            implyed_fav[price[1]][0].append(price[2])
    #            implyed_fav[price[1]][1].append(curr)
    #    curr += timedelta(minutes=1)

    height = math.ceil(len(entrant_timeseries) / 2)
    width = 2
    fig_height = height * 5  # Adjust this multiplier to increase the height of the figure

    fig, axs = plt.subplots(height, width, figsize=(15, fig_height))
    axs = axs.flatten()  # Flatten in case axs is a 2D array
    
    for idx, entrant in enumerate(entrant_timeseries):
        if not entrant:
            continue
        entrant = entrant[0]
        horse_name = entrant[1]
        platforms = entrant[0]
        for platform_entry in platforms:
            axs[idx].plot(platform_entry[1], platform_entry[0], label=platform_entry[2], marker='o')
        axs[idx].set_title(horse_name)
        axs[idx].legend()

    # Create a new figure for the overarching line chart
    fig2, ax2 = plt.subplots(figsize=(15, 4))
    for horse_name, time_series in implyed_fav.items():
        ax2.plot(time_series[1], time_series[0], label=horse_name)
    ax2.set_title('Market Prices Over Time')
    ax2.legend()

    fig.tight_layout()  # Adjust subplots to fit into figure area.
    fig2.tight_layout()  # Adjust the overarching chart to fit into figure area.

    plt.show()

    time.sleep(10)
    print('reset')
