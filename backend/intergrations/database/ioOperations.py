import hashlib
import os
from datetime import datetime
import heapq
import tensorflow as tf
import json
import numpy as np
from itertools import combinations
from clock import clock
import re

baseFile = os.path.dirname(os.path.abspath(__file__))
imageDirectory = os.path.join(os.path.dirname(baseFile),'assets')

modelDir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'test_modelTwo.h5')
model = tf.keras.models.load_model(modelDir)

def readCache(path):
    try:
        data = []
        with open(path, 'r') as file:
            for line in file:
                data.append(line.strip())
        return data
    except:
        return []
    
def matchHash(teams,standardize=True):
    if (isinstance(teams,list)):
        matchName = ''.join([element['name'] for element in teams]).replace(' ','')
        matchName = matchName.lower()
    else:
        matchName = teams
    if (standardize):
        matchName = ''.join(sorted(matchName))

    matchName = sanitiseData(matchName)
    sha256_hash = hashlib.sha256()
    matchName = sha256_hash.update(matchName.encode('utf-8'))
    matchName = int((format(int(sha256_hash.hexdigest(),16), 'x'))[:15],16)

    return matchName

def generateMatchID(data):
    pass

def sanitiseData(data:str):
    data = data.replace("'","")
    data = data.replace('"','"')
    return re.sub(r'[^a-zA-Z0-9 ]', '', data)

def addWinner(data,database):
    for x in range(0,len(data)):
        try:
            entry = data[x]
            database.imposeWinner(entry['name'],entry['startTime'],entry['winner'])
        except:
            continue

def updateDatabase(data,database):
    modifyedMatches = set()
    currentTime = datetime.now().isoformat()
    database.imposeSport(sanitiseData(data['sport']))
    database.imposePlatform(sanitiseData(data['platform']))

    for match in data['data']:
        try:
            match['name'] = sanitiseData(match['name'])
            matchID = ''
            for participent in match['teams']:
                participent['name'] = sanitiseData(participent['name'])
                matchID += f'{participent["name"]} '
                database.imposeTeam(participent['name'],data['sport'])
            if not match['name'] == 'auto':
                matchID = match['name']

            if isinstance(match['startTime'],datetime):
                date = datetime.strptime(match['startTime'], '%Y-%m-%dT%H:%M:%S')
            else:
                date = datetime.fromisoformat(match['startTime'])    

            matchForignID = database.imposeMatch(matchID,date,data['sport'],match['participants'])
            database.deleteAllParticipents(matchForignID)
            for participent in match['teams']:
                if (database.imporseParticipation(participent['name'],float(participent['odds']),matchForignID,data['platform'],currentTime)):
                    modifyedMatches.add(matchForignID)
        except:
            continue

def computeArbs(matchIDs,database):
    for matchID in matchIDs:
        try:
            participents = getValueBets(database.getCrossPlatformOdds(matchID[len(matchID)-1]))
            database.deleteValueBets(matchID[len(matchID)-1])
            totalROI = 0
            while len(participents) > 0:
                INCLUDE = False
                participent = heapq.heappop(participents)
                ROI = participent[0]
                PARTICIPENT = participent[1]
                if ROI + totalROI < 1:
                    totalROI += ROI
                    INCLUDE = True
                database.imposeValueBets(PARTICIPENT[0],PARTICIPENT[1],matchID[len(matchID)-1],PARTICIPENT[3],PARTICIPENT[5],ROI,INCLUDE)
        except:
            continue

def getValueBets(offerings):
    participents = []
    organiseByTeam = {}
    for offering in offerings:
        if not offering[0] in organiseByTeam:
            organiseByTeam[offering[0]] = []
            heapq.heappush(organiseByTeam[offering[0]],(1/float(offering[1]),offering))
        else:
            heapq.heappush(organiseByTeam[offering[0]],(1/float(offering[1]),offering))
    for key,value in organiseByTeam.items():
        heapq.heappush(participents,heapq.heappop(value))
    return participents

def returnArbs(database):
    arb_data = {}
    arbs = database.getArbIds()
    for arb in arbs:
        roi, arb_id, match_id,sport,startTime = arb
        arb_details = database.getArbDetails(arb_id, match_id)

        deetsList = []
        platforms = []
        leastLastUpdated = None
        for x in range(0,len(arb_details)):
            deetsDist = {}
            deets = list(arb_details[x])
            deets[3] = float(deets[3])
            deets[5] = deets[5].isoformat()

            deetsDist['team'] = deets[2]
            deetsDist['odds'] = deets[3]
            deetsDist['platform'] = deets[4]
            deetsDist['dateUpdated'] = deets[5]
            platforms.append(deets[4])

            if leastLastUpdated == None:
                leastLastUpdated = deets[len(deets)-1]
            elif leastLastUpdated < deets[len(deets)-1]:
                leastLastUpdated = deets[len(deets)-1]
            deetsList.append(deetsDist)

        tempIdFix = round(int(f'{arb_id}')/1000)
        arb_data[tempIdFix] = {'title': tempIdFix,'roi': float(roi), 'platforms':platforms, 'sport': sport, 'startTime':startTime.isoformat(), 'lastUpdated':leastLastUpdated, 'details': deetsList}
    return arb_data

def differentiateArbStates(currentState,previousState):
    differences = {}
    for key,value in currentState.items():
        if key in previousState:
            if previousState[key] == value:
                break
        differences[key] = value
    return differences

def getTeamImage(team:str):
    candidateNames = [f'{team}.png',f'{team.replace(" ","-")}.png']
    for candidate in candidateNames:
        imagePath = os.path.join(imageDirectory,candidate)
        if os.path.isfile(imagePath):
            return imagePath
    return None

def pad_sequences(data):
    return tf.keras.preprocessing.sequence.pad_sequences(data, padding='post', maxlen=24, dtype='float32')

def runModel(matches,dataabse):
    data = []
    for match in matches:
        try:
            odds = dataabse.getValueBetOdds(match[len(match)-1])
            oddsData = []
            for odd in odds:
                oddsData.append(float(odd[0]))
            oddsDataIsolated = pad_sequences([np.array(oddsData)])
            predictions = model.predict(oddsDataIsolated,verbose=0)
            dataabse.imposeOddsGuard(match[len(match)-1],predictions[0][0] < 0.5,predictions[0][0])
        except:
            continue
        
def setWinner(database,data):
    for entry in data:
        winnerName = sanitiseData(entry['winnerName'])
        #must include dates
        forignID = database.getNumericMatchID(entry['name'],entry['startTime'])
        database.imposeWinner(forignID,winnerName)
        
        transactionIds = database.getWinningBetsTransactionIds(forignID,winnerName)
        for transactionId in transactionIds:
            bets = database.getPlacedBets(transactionId[0])
            ROI = 0
            WIN_STATUS = True
            for bet in bets:
                if bet[0] == winnerName and bet[6] == False:
                    WIN_STATUS = False
                    break
                if bet[6] == True:
                    ROI += bet[5]
            if WIN_STATUS:
                initialDebt = database.getDebtTransaction(transactionId)
                investment = initialDebt[2]
                userID = initialDebt[0]
                WINNINGS = investment/ROI
                database.addWinningIncome(userID,investment,transactionId)
                  
def placeBet(database,userID,amount,matchID):
    transactionID = database.createDebt(userID,amount)
    bets = database.getValueBets(matchID)
    for bet in bets:
        database.addPlacedBet(bet[0],bet[1],bet[2],bet[3],bet[4],bet[5],bet[6],transactionID)
    

    