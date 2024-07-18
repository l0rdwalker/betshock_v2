import ioOperations
import psycopg2
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from datetime import datetime, timedelta
import json
import os

class databaseOperations:
    def __init__(self) -> None:
        self.file = os.path.dirname(os.path.abspath(__file__))
        credentials:list = ioOperations.readCache(os.path.join(self.file,"credentials.json"))
        
        self.credentials = json.loads(" ".join(credentials))
        self.commands = []

    def initConnection(self):
        self.conn = psycopg2.connect(
            host=self.credentials['host'],
            database=self.credentials['database'],
            user=self.credentials['user'],
            password=self.credentials['password']
        )
        self.cursor = self.conn.cursor()

    def closeConnection(self):
        self.conn.close()

    def pushQuery(self,query):
        print(query)
        data = None
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
    
    def addTeam(self,teamName:str,teamSport:str):
        sql = f"INSERT INTO teams (teamname,teamsport) VALUES ('{teamName}','{teamSport}')"
        self.pushQuery(sql)

    def imposeTeam(self,teamName:str,teamSport:str):
        sql = f"SELECT EXISTS (SELECT 1 FROM teams WHERE teamname = '{teamName}' AND teamsport = '{teamSport}' ) AS team_exists"
        entryExists = self.pushQuery(sql)[0][0]
        if (entryExists == False):
            self.addTeam(teamName,teamSport)

    def addSport(self,sport,description='na'):
        sql = f"INSERT INTO sports (sport,description) VALUES ('{sport}','{description}')"
        self.pushQuery(sql)

    def imposeSport(self,sport):
        sql = f"SELECT EXISTS (SELECT 1 FROM sports WHERE sport = '{sport}' ) AS sport_exists"
        sportExists = self.pushQuery(sql)[0][0]
        if (sportExists == False):
            self.addSport(sport)

    def imposeMatch(self,matchID,startTime:datetime,sport,participants):
        matchTime = startTime.strftime('%Y-%m-%d %H:%M:%S')
        sql = f"SELECT * FROM match WHERE matchID = '{matchID}' AND starttime BETWEEN TO_TIMESTAMP('{matchTime}', 'YYYY-MM-DD HH24:MI:SS') - interval '15' minute AND TO_TIMESTAMP('{matchTime}', 'YYYY-MM-DD HH24:MI:SS') + interval '15' minute AND sport = '{sport}'"
        entryExists = self.pushQuery(sql)
        if (len(entryExists) == 0):
            matchID = self.addMatch(matchID,startTime,sport,participants)
            return matchID[0][0]
        else:
            self.updateMatch(matchID,startTime,sport,participants)
        return entryExists[0][4]

    def addMatch(self,matchID,startTime:datetime,sport,participants):
        sql = f"INSERT INTO match(matchID, sport, starttime, participants) VALUES ('{matchID}','{sport}', '{startTime.isoformat()}','{participants}') RETURNING forignid"
        return self.pushQuery(sql) 
    
    def updateMatch(self,matchID,startTime:datetime,sport,participants):
        sql = f"UPDATE match SET participants={participants} WHERE matchID='{matchID}' AND starttime='{startTime.isoformat()}' AND sport='{sport}'"
        self.pushQuery(sql) 

    def addPlatform(self,platformName):
        sql = f"INSERT INTO Platforms (platformName) VALUES ('{platformName}')"
        self.pushQuery(sql)

    def imposePlatform(self,platformName):
        sql = f"SELECT EXISTS (SELECT 1 FROM platforms WHERE platformname = '{platformName}' ) AS platform_exists"
        platformExists = self.pushQuery(sql)[0][0]
        if (platformExists == False):
            self.addPlatform(platformName)

    def addPlatformOffering(self,platform,sport):
        sql = f"INSERT INTO Platforms (platformName,sport) VALUES ('{platform}','{sport}')"
        self.pushQuery(sql)

    def getSports(self):
        sql = f'SELECT * FROM sports'
        return self.pushQuery(sql)
    
    def getPlatforms(self):
        sql = f'SELECT * FROM platforms'
        return self.pushQuery(sql)
    
    def getTeams(self):
        sql = 'SELECT * FROM teams'
        return self.pushQuery(sql)
    
    def imporseParticipation(self,team,odds,matchid,platformname,time):
        sql = f"SELECT EXISTS (SELECT 1 FROM participatesin WHERE team = '{team}' AND matchid = {matchid} AND platform = '{platformname}') AS match_exists"
        participationExists = self.pushQuery(sql)[0][0]
        outcome = None
        if (participationExists == False):
            outcome = self.addParticipation(team,odds,matchid,platformname,time)
        else:
            outcome = self.updateParticipation(team,odds,matchid,platformname,time)
        return not (len(outcome) == 0)

    def addParticipation(self,team,odds,matchid,platformname,time):
        sql = f"INSERT INTO participatesin(team, odds, matchid, platform, dateModifyed) VALUES ('{team}', {odds}, {matchid}, '{platformname}', '{time}') RETURNING matchid"
        return self.pushQuery(sql)

    def updateParticipation(self,team,odds,matchid,platformname,time):
        sql = f"UPDATE participatesin SET odds={odds}, dateModifyed='{time}' WHERE odds!={odds} AND team='{team}' AND matchid={matchid} AND platform='{platformname}' RETURNING matchid"
        return self.pushQuery(sql)
    
    def getTeamsBySport(self,sport):
        sql = f"SELECT teamname FROM teams WHERE teamsport = '{sport}'"
        data = self.pushQuery(sql)
        return data
    
    def getLikeTeam(self,team,sport):
        sql = f"SELECT * FROM teams WHERE teamname LIKE '%{team}%' AND teamsport = '{sport}'"
        return self.pushQuery(sql)
    
    def findTeam(self,nameProspect,existingTeamNames):
        return nameProspect
        #teamNames = process.extract(nameProspect, existingTeamNames, limit=5)
        #searchName = nameProspect.lower()
        #for teamName in teamNames:
        #    name:str = teamName[0].lower()
        #    if searchName in name or name in searchName or name == searchName:
        #        return teamName[0]
        #return nameProspect
    
    def getFutureMatches(self):
        startTime = datetime.now()
        sql = f"SELECT * FROM match WHERE startTime > TO_TIMESTAMP('{startTime.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS')"
        return self.pushQuery(sql)
    
    def getSportSpecificFutureMatches(self,sport):
        startTime = datetime.now() - timedelta(days=7)#Must correct for normal operations
        #sql = f"SELECT * FROM match WHERE startTime < TO_TIMESTAMP('{startTime.strftime('%Y-%m-%d %H:%M:%S')}', 'YYYY-MM-DD HH24:MI:SS') AND sport = '{sport}'"
        sql = f"SELECT * FROM match WHERE sport ='{sport}'"
        return self.pushQuery(sql)
    
    def getValueBetOdds(self,matchid):
        sql = f"SELECT AVG(odds) as odds FROM participatesin WHERE matchid = {matchid} GROUP BY team ORDER BY odds ASC;"
        return self.pushQuery(sql)
    
    def getCrossPlatformOdds(self,matchID):
        sql = f"SELECT * FROM participatesin WHERE matchid = '{matchID}' ORDER BY platform DESC,Team DESC"
        return self.pushQuery(sql)
    
    def getMatchStartTime(self,matchId):
        sql = f"SELECT starttime FROM match WHERE forignid = {matchId}"
        return self.pushQuery(sql)[0][0]
    
    def getAllPlatforms(self):
        return self.pushQuery('SELECT * FROM platforms')
    
    def getAllSports(self):
        return self.pushQuery('SELECT sport FROM sports')
    
    def deleteValueBets(self,matchid):
        sql = f"DELETE FROM valueBets WHERE matchID = {matchid}"
        self.pushQuery(sql)
    
    def imposeValueBets(self,team,odds,matchid,platform,dateModifyed,ROI,included):
        sql = f"SELECT EXISTS (SELECT 1 FROM valuebets WHERE team = '{team}' AND matchid = {matchid} AND platform = '{platform}') AS valuebet_exists"
        participationExists = self.pushQuery(sql)[0][0]
        if participationExists:
            sql = f"UPDATE valuebets SET included={included},odds={odds},dateModifyed='{dateModifyed.isoformat()}',ROI={ROI} WHERE team='{team}' AND matchid='{matchid}' AND platform='{platform}'"
        else:
            sql = f"INSERT INTO valueBets(team, odds, matchid, platform, dateModifyed,ROI,included) VALUES ('{team}', {odds}, {matchid}, '{platform}', '{dateModifyed.isoformat()}', {ROI}, {included})"
        self.pushQuery(sql)
        
    def deleteAllParticipents(self,id):
        sql = f'DELETE FROM participatesin WHERE forignid = {id}'
        self.pushQuery(sql)

    def imposeWinner(self,matchName,matchDate:datetime,winner):
        sql = f"SELECT forignid FROM match WHERE matchid = '{matchName}' AND starttime BETWEEN '{matchDate}'::timestamp - interval '5 minutes' AND '{matchDate}'::timestamp + interval '5 minutes'"
        result = self.pushQuery(sql)
        
        if 0 < len(result) < 2:
            matchid = result[0][0]
            sql = f"SELECT EXISTS (SELECT 1 FROM winners WHERE matchid = '{matchid}') AS winner_exists"
        else:
            raise Exception('Match could not be found.')
        
        result = self.pushQuery(sql)[0][0]
        if result:
            self.updateWinner(matchid,winner)
        else:
            self.addWinner(matchid,winner)
    
    def addWinner(self,matchID,winnerName):
        sql = f"INSERT INTO winners(matchID,participant) VALUES ({matchID},'{winnerName}')"
        self.pushQuery(sql)

    def updateWinner(self,matchID,winnerName):
        sql = f"UPDATE winners SET participant='{winnerName}' WHERE matchID={matchID}"
        self.pushQuery(sql)

    def getNumericMatchID(self,matchName,startTime):
        sql = f"SELECT forignID FROM match WHERE matchid = '{matchName}' AND starttime = '{startTime}'"
        return self.pushQuery(sql)[0][0]
    
    def devExercuter(self,sql):
        return self.pushQuery(sql)
    
    def imposeOddsGuard(self,id,status,certainty):
        sql = f"SELECT EXISTS (SELECT 1 FROM oddGuard WHERE matchid = {id})"
        status = self.pushQuery(sql)[0][0]
        if status:
            self.updateOddGuard(id,status,certainty)
        else:
            self.addOddGuard(id,status,certainty)
        
    def addOddGuard(self,id,status,certainty):
        sql = f"INSERT INTO oddGuard(matchID,status,certainty) VALUES ({id},{status},{certainty})"
        self.pushQuery(sql)
        
    def updateOddGuard(self,id,status,certainty):
        sql = f"UPDATE oddGuard SET status={status},certainty={certainty} WHERE matchID={id}"
        self.pushQuery(sql)
        
    def getBankBalence(self,id):
        sql = f"SELECT COALESCE((SELECT SUM(amount) FROM income WHERE userId = {id}), 0) + COALESCE((SELECT SUM(amount) FROM debt WHERE userId = {id}), 0) AS total"
        return self.pushQuery(sql)[0][0]
    
    def createDebt(self,userID,amount):
        sql = f"INSERT INTO debt(userid, date, amount) VALUES ('{userID}', NOW(), '{amount}') RETURNING forignID"
        return self.pushQuery(sql)[0][0]
        
    def getUserID(self,name,password):
        sql = f"SELECT forignid FROM users WHERE name='{name}' AND password = '{password}'"
        return self.pushQuery(sql)[0][0]

    def getValueBets(self,matchID):
        sql = f"SELECT * FROM valuebets WHERE matchid='{matchID}'"
        return self.pushQuery(sql)
    
    def addPlacedBet(self,team,odds,matchid,platform,datemodifyed,roi,included,transactionid):
        sql = f"INSERT INTO placedbets(team, odds, matchid, platform, datemodifyed, roi, included, transactionid) VALUES ('{team}', {odds}, {matchid}, '{platform}', '{datemodifyed}', {roi}, {included}, {transactionid});"
        self.pushQuery(sql)
    
    def addWinningIncome(self,userid,amount,forignid):
        sql = f"INSERT INTO income(userid, date, amount, forignid) VALUES ({userid}, NOW(), {amount}, {forignid});"
        self.pushQuery(sql)
        
    def getDebtTransaction(self,transactionID):
        sql = f"SELECT * FROM debt WHERE forignid = {transactionID}"
        
    def getPlacedBets(self,matchid,transactionID):
        sql = f"SELECT * FROM placedbets WHERE matchid={matchid} AND transactionID={transactionID}"
        return self.pushQuery(sql)
    
    def getWinningBetsTransactionIds(self,matchid):
        sql = f"SELECT DISTINCT transactionID FROM placedbets WHERE matchid={matchid}"
        return self.pushQuery(sql)