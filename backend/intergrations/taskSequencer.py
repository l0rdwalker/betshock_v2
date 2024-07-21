import os
import json
import dataManagement as dm
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
            if currentTask['type'] == 'scrape':
                self.processData(data)
        except Exception as e:
            self.log(e,error=True)
            self.log(f"{currentTask['type']} on {currentTask['platform']} failed.",error=True)
        return currentTask['driver'].whenNextRun() 
    
    def processData(self,update_data):
        pass

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
#postScrapeTasks.extend(test.searchFunctions(getUpdater))
postScrapeTasks.extend(test.searchFunctions(getArbUpdater))
#postScrapeTasks.extend(test.searchFunctions(getResults))
##postScrapeTasks.extend(test.searchFunctions(getOddGuard))
#
horces = multitask(functions,postScrapeTasks)
horces = horces.returnFunctionConfig()
test.addFunction(horces)

while True:
    test.step()