CREATE TABLE Sports (
    sport VARCHAR(50),
    Description VARCHAR(250),
    PRIMARY KEY(sport)
);

CREATE TABLE Platforms (
    platformName VARCHAR(50),
    PRIMARY KEY (platformName)
);

CREATE TABLE Teams (
    teamName VARCHAR(50),
    teamSport VARCHAR(50),
    PRIMARY KEY (teamName),
    FOREIGN KEY (teamSport) REFERENCES Sports(sport)
);

CREATE TABLE Match (
    matchID VARCHAR(100),
    participants int, 
    sport VARCHAR(50),
    startTime TIMESTAMP,
    forignId SERIAL,
    PRIMARY KEY(matchID, startTime),
    FOREIGN KEY (sport) REFERENCES Sports(sport),
    UNIQUE (forignId)
);

CREATE TABLE ParticipatesIn (
    team VARCHAR(50),
    odds DECIMAL(8, 4),
    matchID int,
    platform VARCHAR(50),
    forignID SERIAL,
    dateModifyed TIMESTAMP,
    FOREIGN KEY (team) REFERENCES Teams(teamName),
    FOREIGN KEY (matchID) REFERENCES Match(forignId),
    FOREIGN KEY (platform) REFERENCES Platforms(platformName),
    PRIMARY KEY (team, matchID, platform),
    UNIQUE (forignID)
);

CREATE TABLE valueBets (
    team VARCHAR(50),
    odds DECIMAL(8, 4),
    matchID int,
    platform VARCHAR(50),
    dateModifyed TIMESTAMP,
    ROI DECIMAL(8,4),
    included BOOLEAN,
    FOREIGN KEY (team) REFERENCES Teams(teamName),
    FOREIGN KEY (matchID) REFERENCES Match(forignId),
    FOREIGN KEY (platform) REFERENCES Platforms(platformName),
    PRIMARY KEY (team, matchID, platform)
);

CREATE TABLE winners (
    matchID int,
    participant VARCHAR(50), 
    FOREIGN KEY (matchID) REFERENCES Match(forignId),
    FOREIGN KEY (participant) REFERENCES Teams(teamName),
    PRIMARY KEY (matchID)
);

CREATE TABLE oddGuard (
    matchID int,
    status BOOLEAN,
    certainty DECIMAL(4, 4),
    FOREIGN KEY (matchID) REFERENCES Match(forignid),
    PRIMARY KEY (matchID)
);

CREATE TABLE users (
    name VARCHAR(50),
    password VARCHAR(50),
    forignId SERIAL,
    UNIQUE (forignId),
    PRIMARY KEY(name,password)
);

CREATE TABLE balance (
    userID int,
    amount DECIMAL(15, 4),
    PRIMARY KEY (userID)
);

CREATE TABLE debt (
    userID int,
    date timestamp,
    amount DECIMAL(15, 4),
    forignID serial,
    UNIQUE (forignID),
    FOREIGN KEY (userID) REFERENCES users(forignid),
    PRIMARY KEY (userID,date,amount)
);

CREATE TABLE placedBets (
    team VARCHAR(50),
    odds DECIMAL(8, 4),
    matchID int,
    platform VARCHAR(50),
    dateModifyed TIMESTAMP,
    ROI DECIMAL(8,4),
    included BOOLEAN,
    transactionID int,
    FOREIGN KEY (team) REFERENCES Teams(teamName),
    FOREIGN KEY (matchID) REFERENCES Match(forignId),
    FOREIGN KEY (platform) REFERENCES Platforms(platformName),
    FOREIGN KEY (transactionID) REFERENCES debt(forignid),
    PRIMARY KEY (team, matchID, platform)
);

CREATE TABLE income (
    userID int,
    date timestamp,
    amount DECIMAL(15, 4),
    forignID serial,
    UNIQUE (forignID),
    FOREIGN KEY (userID) REFERENCES users(forignid),
    PRIMARY KEY (userID,date,amount)
);

CREATE TABLE bets (
    transactionID int,
    matchID int,
    ROI DECIMAL(8,4),
    FOREIGN KEY (matchID) REFERENCES Match(forignid),
    FOREIGN KEY (transactionID) REFERENCES debt(forignid)
);