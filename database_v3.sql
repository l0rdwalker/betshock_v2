CREATE TABLE track (
    track_id SERIAL PRIMARY KEY,
    track_name VARCHAR(100) UNIQUE,
    track_type VARCHAR(10),
    address VARCHAR(200)
);

CREATE TABLE horse (
    horse_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    sex VARCHAR(5),
    parent_1 VARCHAR(50),
    parent_2 VARCHAR(50)
);

CREATE TABLE trainer (
    trainer_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE
);

CREATE TABLE jocky (
    jocky_id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE
);

CREATE TABLE race (
    race_id SERIAL PRIMARY KEY,
    track_id int,
    start_time TIMESTAMP,
    round int,
    FOREIGN KEY (track_id) REFERENCES track(track_id)
);

CREATE TABLE entrant (
    entrant_id SERIAL PRIMARY KEY,
    horse_id int,
    jocky_id int,
    trainer_id int,
    race_id int,
    jocky_weight float,
    FOREIGN KEY (horse_id) REFERENCES horse(horse_id),
    FOREIGN KEY (jocky_id) REFERENCES jocky(jocky_id),
    FOREIGN KEY (trainer_id) REFERENCES trainer(trainer_id),
    FOREIGN KEY (race_id) REFERENCES race(race_id)
);

CREATE TABLE entrant_results (
    entrant_id int PRIMARY KEY,
    placement int,
    first_segment int,
    seccond_segment int,
    margin float,
    FOREIGN KEY (entrant_id) REFERENCES entrant(entrant_id)
);

CREATE TABLE weather (
    race_id int PRIMARY KEY,
    temperature float,
    apparent_temperature float,
    rain float,
    wind_speed_100m float,
    wind_direction_100m float,
    FOREIGN KEY (race_id) REFERENCES race(race_id)
);

CREATE TABLE platforms (
    platform_name varchar(80) PRIMARY KEY
);

CREATE TABLE odds (
    entrant_id int,
    platform_name varchar(80),
    odds float,
    record_time TIMESTAMP,
    PRIMARY KEY (entrant_id, record_time),
    FOREIGN KEY (platform_name) REFERENCES platforms(platform_name)
);
