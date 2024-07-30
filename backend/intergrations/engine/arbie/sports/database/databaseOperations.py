import psycopg2
from datetime import datetime, timedelta
from threading import Lock, Thread
import json
import os

def readCache(path):
    try:
        data = []
        with open(path, 'r') as file:
            for line in file:
                data.append(line.strip())
        return data
    except:
        return []

class databaseOperations:
    def __init__(self) -> None:
        self.file = os.path.dirname(os.path.abspath(__file__))
        credentials:list = readCache(os.path.join(self.file,"credentials.json"))
        self.lock = Lock()
        
        self.credentials = json.loads(" ".join(credentials))
        self.commands = []
        self.connection_open = False

    def initConnection(self):
        self.conn = psycopg2.connect(
            host=self.credentials['host'],
            database=self.credentials['database'],
            user=self.credentials['user'],
            password=self.credentials['password']
        )
        self.cursor = self.conn.cursor()
        self.connection_open = True

    def closeConnection(self):
        self.conn.close()
        self.connection_open = False

    def pushQuery(self,query):
        query = query.replace("\n","")
        query = query.strip()
        query = query.split()
        query = ' '.join(query)
        data = None
        with self.lock:
            try:
                data = self.cursor.execute(query)
                if query.strip().lower().startswith('select') or 'returning' in query.strip().lower():
                    data = self.cursor.fetchall()
                self.conn.commit()
            except Exception as e:
                print(e)
                print("\033[91m" + query + "\033[0m")
                self.conn.rollback()
        return data
    
    def impose_platform(self,platform_name):
        return self.pushQuery(f"""
        WITH ins AS (
            INSERT INTO platforms(platform_name)
                VALUES ('{platform_name}')
            ON CONFLICT DO NOTHING
                RETURNING platform_name
        )
        SELECT platform_name FROM ins
            UNION ALL
        SELECT platform_name FROM public.platforms WHERE platform_name = '{platform_name}'
            LIMIT 1;
        """)[0][0]
    
    def impose_horse(self,horse_name):
        return self.pushQuery(f"""
        WITH ins AS (
            INSERT INTO public.horse(
                name, sex, parent_1, parent_2)
            VALUES ('{horse_name}', 'n/a', 'n/a', 'n/a')
                ON CONFLICT DO NOTHING
            RETURNING horse_id
        )
        SELECT horse_id FROM ins
            UNION ALL
        SELECT horse_id FROM public.horse WHERE name = '{horse_name}'
            LIMIT 1;
        """)[0][0]
    
    def impose_race(self,track_id,start_time:datetime,round):
        existing_race = self.pushQuery(f"""
            SELECT * FROM race WHERE
                track_id = {track_id} AND DATE(start_time) = DATE('{start_time}') AND round={round}
            LIMIT 1; 
        """)
        if (len(existing_race) == 0):
            return self.pushQuery(f"""
            WITH ins AS (
                INSERT INTO public.race(
                    track_id, start_time, round)
                VALUES ('{track_id}', '{start_time}', {round})
                    ON CONFLICT DO NOTHING
                RETURNING race_id
            )
            SELECT race_id FROM ins
                UNION ALL
            SELECT race_id FROM public.race WHERE track_id = '{track_id}' AND start_time = '{start_time}' AND round = '{round}'
                LIMIT 1;
            """)[0][0]
        else:
            return existing_race[0][0]
        
    def get_race_entrant_ids(self, race_id):
        return self.pushQuery(f"""
            SELECT entrant.entrant_id, horse.name FROM entrant
                JOIN horse ON horse.horse_id = entrant.horse_id
            WHERE race_id = {race_id};               
                              """)
        
    def get_specific_entrant_id_by_name_and_race(self,race_id,horse_name):
        data = self.pushQuery(f"""
            SELECT entrant_id FROM entrant
                JOIN horse ON horse.horse_id = entrant.horse_id
            WHERE race_id = {race_id} AND horse.name = '{horse_name}'
            LIMIT 1;
        """)
        if len(data) == 0:
            return None
        return data[0][0]
        
    def get_round_and_track_name_by_id(self,race_id):
        data = self.pushQuery(f"""
            SELECT track.track_name, race.round FROM
                race JOIN track
                    ON race.track_id = track.track_id
                WHERE race.race_id = {race_id};
                              """)
        return data[0]
        
    def delete_by_entrant_id(self,entrant_id):
        self.pushQuery(f"""DELETE FROM public.market_conditions WHERE entrant_id={entrant_id};""")
        
        self.pushQuery(f"""DELETE FROM public.odds WHERE entrant_id={entrant_id};""")
        
        self.pushQuery(f"""
            DELETE FROM public.entrant
	            WHERE entrant_id = {entrant_id};
                       """)
    
    def impose_track(self,track_name):
        return self.pushQuery(f"""
        WITH ins AS (
            INSERT INTO public.track(track_name, track_type, address)
                VALUES ('{track_name}', 'n/a', 'n/a')
            ON CONFLICT DO NOTHING
                RETURNING track_id
        )
        SELECT track_id FROM ins
            UNION ALL
        SELECT track_id FROM public.track WHERE track_name = '{track_name}'
            LIMIT 1;
        """)[0][0]
        
    def impose_odds(self,entrant_id,platform_name,odds,record_time):
        if odds == -1:
            return None
        existing_entry = self.pushQuery(f"""
            SELECT odds FROM odds WHERE entrant_id={entrant_id} AND platform_name='{platform_name}' ORDER BY record_time DESC LIMIT 1;
                                        """)
        
        apply_update = False
        if len(existing_entry) == 0:
            apply_update = True
        elif not existing_entry[0][0] == odds:
            apply_update = True
        
        if apply_update:
            self.pushQuery(f"""
                INSERT INTO public.odds(
                    entrant_id, platform_name, odds, record_time)
                VALUES ({entrant_id}, '{platform_name}', {odds}, '{record_time}')
                    ON CONFLICT DO NOTHING;
            """)
            
    def correct_race_start_time(self,race_id, start_time):
        self.pushQuery(f"""
            UPDATE public.race
                SET start_time='{start_time}'
            WHERE race_id={race_id};
        """)
        
    def impose_entrant(self,horse_id,race_id,is_scratched):
        scratched_int = 0
        if is_scratched:
            scratched_int = 1
        else:
            scratched_int = 0
        
        existing_entrant = self.pushQuery(f"""
            SELECT * FROM entrant WHERE
                horse_id = {horse_id} AND race_id={race_id}
            LIMIT 1;
        """)
        if (len(existing_entrant) == 0):
            return self.pushQuery(f"""
                INSERT INTO public.entrant(
                    horse_id, jocky_id, trainer_id, race_id, jocky_weight, is_scratched)
                VALUES ({horse_id}, 0, 0, {race_id}, 0, {scratched_int})
                    ON CONFLICT DO NOTHING
                RETURNING entrant_id 
            """)[0][0]
        self.pushQuery(f"""
            UPDATE public.entrant
                SET is_scratched={scratched_int}
            WHERE horse_id={horse_id} AND race_id={race_id};
        """)
        return existing_entrant[0][0]

    def update_scratched(self,entrant_id,is_scratched):
        self.pushQuery(f"""
            UPDATE public.entrant
                SET is_scratched={is_scratched}
            WHERE entrant_id={entrant_id};
                       """)
        
    def deduce_race_id_by_entrant(self,entrants,start_time):
        entrant_list = "("
        for entrant_idx in range(0,len(entrants)):
            if entrant_idx+1 < len(entrants):
                entrant_list += f"'{entrants[entrant_idx]}',"
            else:
                entrant_list += f"'{entrants[entrant_idx]}')"
        
        race_id_data = self.pushQuery(f"""
            SELECT race.race_id FROM entrant
                JOIN horse ON entrant.horse_id = horse.horse_id
                JOIN race ON race.race_id = entrant.race_id
            WHERE horse.name IN {entrant_list} AND DATE(race.start_time) = DATE('{start_time}');
        """)
        if race_id_data == None:
            return None
        if len(race_id_data) == 0:
            return None
        return race_id_data[0][0]
    
    def deduce_entrant_id(self,race_id,horse_id):
        entrant_id_data = self.pushQuery(f"""
            SELECT entrant_id from entrant WHERE race_id = {race_id} AND horse_id = {horse_id};
                                         """)
        if len(entrant_id_data) == 0:
            return None
        return entrant_id_data[0][0]
    
    def impose_market_condition(self,entrant_id,price):
        self.pushQuery(f"""
            INSERT INTO public.market_conditions(
	            entrant_id, price, record_time)
	        VALUES ({entrant_id}, {price}, NOW());
                       """)
        
    def is_imposed(self,entrant_id):
        data = self.pushQuery(f"""SELECT is_scratched FROM entrant WHERE entrant_id = {entrant_id};""")
        if len(data) == 0:
            return None
        return data[0][0]
    
    def impose_platform_race_identifyer(self,identifyer,platform_name,race_id):
        existing_entry = self.pushQuery(f"""
            SELECT race_api_identifyer, platform_name, race_id
                FROM public.race_platform_links
            WHERE platform_name = '{platform_name}' AND race_id = {race_id};
            """)
        if len(existing_entry) > 0:
            self.pushQuery(f"""
            UPDATE public.race_platform_links
                SET race_api_identifyer='{json.dumps(identifyer)}'
            WHERE race_id = {race_id} AND platform_name = '{platform_name}';        
            """)
        else:
            self.pushQuery(f"""
            INSERT INTO public.race_platform_links(
                race_api_identifyer, platform_name, race_id)
            VALUES ('{json.dumps(identifyer)}', '{platform_name}', {race_id});
            """)
            
    def get_platform_api_links(self,race_id):
        return self.pushQuery(f""" 
            SELECT * FROM race_platform_links WHERE race_id = {race_id};        
                              """)
        
    def get_future_races(self):
        return self.pushQuery(f"""
            SELECT * FROM race WHERE start_time > NOW();
                              """)
        
    def get_entrant_platform_offerings(self,entrant_id):
        return self.pushQuery(f"""
            SELECT DISTINCT platform_name FROM odds WHERE entrant_id={entrant_id};
                              """)
    
    def get_entrant_odds_by_platform(self,entrant_id,platform_name):
        data = self.pushQuery(f"""
            SELECT odds, record_time FROM odds WHERE entrant_id={entrant_id} AND platform_name='{platform_name}'
            ORDER BY record_time DESC; 
                              """)
        if len(data) == 0:
            return None
        return data