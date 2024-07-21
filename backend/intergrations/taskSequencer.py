import os
import json
import dataManagement as dm
from database.databaseOperations import databaseOperations
from datetime import datetime, timedelta
from priorityQueue import queue
from engine.multiTask import multitask

class taskSchedular:
    def __init__(self) -> None:
        self.file = os.path.dirname(os.path.abspath(__file__))

        self.tasks = queue()
        self.functions = []
        self.threads = []
        self.currentDatetime = datetime.now()
        
        self.database:databaseOperations = databaseOperations()

        self.log('Initalizeing task schedular')
        sportObjectsDir = os.path.join(self.file,'engine')
        for platform in [entry for entry in os.listdir(sportObjectsDir) if os.path.isdir(os.path.join(sportObjectsDir,entry))]:
            try:
                platformDriver = dm.getModuleByPath(os.path.join(sportObjectsDir,platform),platform)
                for function in platformDriver.getFunctions():
                    self.functions.append(function)
                self.log(f'Successfully imported {platform} dependencys')
            except Exception as e:
                self.log(e)
                
    def addFunction(self,function):
        self.tasks.enqueue((function['driver'].whenNextRun(),function))

    def step(self) -> None:
        self.currentDatetime = datetime.now()
        if self.tasks.peek() != None:
            if self.tasks.peek()[0] < self.currentDatetime:
                priority,currentTask = self.tasks.dequeue()
                mextRun = self.performTask(currentTask)
                self.tasks.enqueue((mextRun,currentTask))
            
    def performTask(self,currentTask):
        try:
            self.log(f"starting {currentTask['type']} on {currentTask['platform']}.")
            data = currentTask['driver'].init(currentTask['data'])
            self.log(f"{currentTask['type']} on {currentTask['platform']} succeeded.")
            if currentTask['type'] == 'scrape' or currentTask['type'] == 'multiTask':
                self.processData(data)
        except Exception as e:
            self.log(e,error=True)
            self.log(f"{currentTask['type']} on {currentTask['platform']} failed.",error=True)
        return currentTask['driver'].whenNextRun() 
    
    def processData(self,update_data):
        try:
            date_race_store = {}
            scratched_horses = {}
            self.database.initConnection()
            
            for platform in update_data:
                if (platform['platform'] == 'diamondbet'):
                    continue
                platform_id = self.database.impose_platform(platform['platform'])
                for race in platform['data']:
                    track_id = self.database.impose_track(race['name'])
                    race_id = self.database.impose_race(track_id,race['start_time'],race['round'])
                    for entrant in race['entrants']:
                        horse_name = entrant['name'].replace("'","").strip().lower()
                        horse_id = self.database.impose_horse(horse_name)
                        entrant_id = self.database.impose_entrant(horse_id,race_id,entrant['scratched'])
                        
                        self.database.impose_odds(entrant_id,platform_id,entrant['odds'])
                        
                        if (entrant['scratched']):
                            scratched_horses[str(entrant_id)] = 1
                        if not str(race_id) in date_race_store:
                            date_race_store[str(race_id)] = [race['start_time']]
                        else:
                            date_race_store[str(race_id)].append(race['start_time'])
            
            for race_id,date_list in date_race_store.items():
                date_occurence = {}
                for date in date_list:
                    if not date in date_occurence:
                        date_occurence[date] = 1
                    else:
                        date_occurence[date] += 1
                frequent_date = None
                frequency = 0
                for date,date_frequency in date_occurence.items():
                    if frequent_date == None or date_frequency > frequency:
                        frequency = date_frequency
                        frequent_date = date
                self.database.correct_race_start_time(race_id,frequent_date)
            self.database.closeConnection()
        except Exception as e:
            print(e)
            self.database.closeConnection()

    def searchFunctions(self,data,searchData=None):
        if searchData == None:
            searchData = self.functions
        
        if len(data) > 0:
            for key,item in data.items():
                keyData = (key,item)
                data.pop(key)
                break
            
            releventFunctions = []
            for function in searchData:
                if keyData[0] in function:
                    if function[keyData[0]] == keyData[1]:
                        releventFunctions.append(function)
                elif keyData[0] in function['data']:
                    if function['data'][keyData[0]] == keyData[1]:
                        releventFunctions.append(function)
            return self.searchFunctions(data,releventFunctions)
        else:
            return searchData
        
    def getFunctions(self):
        return self.functions

    def log(self,message,error=False):
        blackCode = '\033[0m'
        colorCode = blackCode
        if error:
            colorCode = '\033[91m'

        message = str(message)
        message = message.replace("\n","")
        self.clock = datetime.now()

        strDate = f'{self.clock.day}_{self.clock.month}_{self.clock.year}'
        strDateTime = f'{strDate}:{self.clock.hour}_{self.clock.minute}_{self.clock.second}'
        message = f'{strDateTime}: {message}'

        self.logDir = os.path.join(self.file,'logs')
        self.dayLog = os.path.join(self.logDir,f'{strDate}.txt')
        dm.writeFile(self.dayLog,message)

        print(f'{colorCode}{message}{blackCode}\n',end=" ")

customSearchJson = {
    'sport':'horses'
}
getResults = {
    'type':'getResults'
}
getUpdater = {
    'type':'update'
}
getArbUpdater = {
    'type':'arbUpdate'
}
#getOddGuard = {
#    'type':'oddGuard'
#}

test = taskSchedular()
functions:list = test.searchFunctions(customSearchJson)
#
postScrapeTasks = []
postScrapeTasks.extend(test.searchFunctions(getUpdater))
#postScrapeTasks.extend(test.searchFunctions(getArbUpdater))
postScrapeTasks.extend(test.searchFunctions(getResults))
##postScrapeTasks.extend(test.searchFunctions(getOddGuard))
#
horces = multitask(functions,postScrapeTasks)
horces = horces.returnFunctionConfig()
test.addFunction(horces)

while True:
    test.step()