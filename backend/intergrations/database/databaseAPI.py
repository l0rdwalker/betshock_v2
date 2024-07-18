from flask import Flask, request, jsonify, Response, send_file
from flask_socketio import SocketIO,emit
from databaseOperations import databaseOperations
import ioOperations as commonOpporations
from flask_cors import CORS 
import json

global dataCache
dataCache = {}

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app,cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    global dataCache

    print('client connected')
    if len(dataCache) == 0:
        compute_arbs()
    else:
        send_updated_data(dataCache)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def send_updated_data(data):
    socketio.emit('update_data',data)

@app.route('/update',methods=['POST'])
def update():
    try:
        database = databaseOperations()
        database.initConnection()
        data = request.json
        if 'data' in data:
            commonOpporations.updateDatabase(data,database)
            database.closeConnection()
            return Response(status=200)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(status=400)
    
@app.route('/updateArbs',methods=['POST'])
def updateArbs():
    try:
        database = databaseOperations()
        database.initConnection()
        data = request.json
        if 'sport' in data:
            sport = data['sport']
            if (sport == None):
                matches = database.getFutureMatches()
            else:
                matches = database.getSportSpecificFutureMatches(sport)
            data = commonOpporations.computeArbs(matches,database) ### I only want to compute the arbs for data which has realistically changed
            database.closeConnection()
            return jsonify(data)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(status=400)
    
@app.route('/setWinners',methods=['POST'])
def setWinners():
    try:
        database = databaseOperations()
        database.initConnection()
        data = request.json
        commonOpporations.addWinner(data,database)
        database.closeConnection()
        return Response(200)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(400)

@app.route('/computeValueBets',methods=['POST'])
def compute_valuebets():
    try:
        database = databaseOperations()
        database.initConnection()
        matchIds = database.devExercuter('SELECT forignid FROM match')
        corrected = []
        for matchId in matchIds:
            corrected.append(matchId[0])
        commonOpporations.computeArbs(corrected,database) ### I only want to compute the arbs for data which has realistically changed
        database.closeConnection()
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(status=400)
    
@app.route('/computeArbs', methods=['POST']) ###needs to be completelty reworked
def compute_arbs():
    global dataCache
    try:
        database = databaseOperations()
        database.initConnection()
        
        newState = commonOpporations.returnArbs(database)
        stateDifferences = commonOpporations.differentiateArbStates(newState,dataCache)
        database.closeConnection()

        dataCache = newState
        send_updated_data(newState)

        return jsonify(dataCache)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(status=400)
    
@app.route('/getImage',methods=['POST'])
def get_image():
    try:
        data = request.json
        team = data['team']
        if not (team == None):
            imageDirectory = commonOpporations.getTeamImage(team)
            if (imageDirectory == None):
                return Response(status=200)
            else:
                return send_file(imageDirectory)
    except Exception as e:
        return Response(status=201)
    
@app.route('/getPlatforms',methods=['POST','GET'])
def getAllPlatforms():
    try:
        database = databaseOperations()
        database.initConnection()
        data = database.getAllPlatforms()
        database.closeConnection()
        return jsonify(data)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(status=201)
    
@app.route('/getSports',methods=['POST','GET'])
def getAllSports():
    try:
        database = databaseOperations()
        database.initConnection()
        data = database.getAllSports()
        database.closeConnection()
        return jsonify(data)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(status=201)
    
@app.route('/updateOddGuard',methods=['POST'])
def runModel():
    try:
        database = databaseOperations()
        database.initConnection()
        data = request.json
        if 'sport' in data:
            sport = data['sport']
            if (sport == None):
                matches = database.getFutureMatches()
            else:
                matches = database.getSportSpecificFutureMatches(sport)
            commonOpporations.runModel(matches,database)
        database.closeConnection()
        return Response(200)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(400)
    pass
    
@app.route('/devQuery',methods=['POST','PUT'])
def devExercuter():
    try:
        database = databaseOperations()
        database.initConnection()
        data = database.devExercuter(request.json['query'])
        database.closeConnection()
        return jsonify({'data':data})
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(status=201)

@app.route('/createUser',methods=['POST'])
def createUser():
    try:
        database = databaseOperations()
        database.initConnection()
        userDetails = request.json
        userName = commonOpporations.sanitiseData(userDetails['name'])
        password = commonOpporations.sanitiseData(userDetails['password'])
        userID = database.devExercuter(f"INSERT INTO users (name,password) VALUES ('{userName}','{password}') RETURNING forignid")
        database.closeConnection()
        return jsonify({'userID':userID})
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(400)

@app.route('/deleteUser',methods=['POST'])
def deleteUser():
    try:
        database = databaseOperations()
        database.initConnection()
        userDetails = request.json
        userName = commonOpporations.sanitiseData(userDetails['name'])
        password = commonOpporations.sanitiseData(userDetails['password'])
        database.devExercuter(f"DELETE FROM users WHERE name='{userName}' AND password='{password}'")
        database.closeConnection()
        return Response(200)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(400)
    
@app.route('/getBankBalence',methods=['POST'])
def getBankBalence():
    try:
        database = databaseOperations()
        database.initConnection()
        userDetails = request.json

        userID = userDetails['userID']
        balence = database.getBankBalence(userID)
        
        database.closeConnection()
        return jsonify({'balence':balence})
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(400)
    
@app.route('/placeBet',methods=['POST'])
def placeBet():
    try:
        database = databaseOperations()
        database.initConnection()
        userDetails = request.json

        matchId = userDetails['matchId']
        stake = userDetails['stake']
        userID = userDetails['userID']
        
        balence = getBankBalence(userID)
        
        if (stake < balence):
            database.devExercuter(f"")
        else:
            raise Exception('InsufficentFunds')
        
        database.closeConnection()
        return Response(200)
    except Exception as e:
        print(e)
        database.closeConnection()
        return Response(400)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=8081, debug=True)
