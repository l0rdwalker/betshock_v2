import os
import json
import dataManagement as dm
from datetime import datetime, timedelta, timezone
from priorityQueue import queue
from engine.multiTask import multitask

class taskSchedular:
    def __init__(self) -> None:
        self.file = os.path.dirname(os.path.abspath(__file__))

        self.tasks = [] #queue()
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
        self.tasks.append((datetime.now().astimezone(timezone.utc),function))

    def step(self) -> None:
        self.currentDatetime = datetime.now().astimezone(timezone.utc)
        self.tasks = sorted(self.tasks, key=lambda x: x[0])
        if self.tasks[0] != None:
            if self.tasks[0][0] < self.currentDatetime:
                priority,currentTask = self.tasks.pop(0)
                mextRun = self.performTask(currentTask)
                self.tasks.append((mextRun,currentTask))
            
    def performTask(self,currentTask):
        try:
            self.log(f"starting {currentTask['type']} on {currentTask['platform']}.")
            data = currentTask['driver'].init(currentTask['data'])
            self.log(f"{currentTask['type']} on {currentTask['platform']} succeeded.")
        except Exception as e:
            self.log(e,error=True)
            self.log(f"{currentTask['type']} on {currentTask['platform']} failed.",error=True)
        return currentTask['driver'].get_next_run()

    def contains_key(self,key_value,search_data):
        match_status = False
        for key,value in search_data.items():
            if match_status:
                return match_status
            if isinstance(value, dict):
                match_status = self.contains_key(key_value,value)
            elif key_value[0] == key and key_value[1] == value:
                match_status = True
        return match_status
            
    def searchFunctions(self,data,searchData=None):
        if searchData == None:
            searchData = self.functions
        
        if len(data) > 0:
            for key,item in data.items():
                key_data = (key,item)
                data.pop(key)
                break
            
            releventFunctions = []
            for function in searchData:
                if self.contains_key(key_data,function):
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

flex_dates = {
    'sport':'horses',
    'flex_dates' : True
}
non_flex_dates = {
    'sport':'horses',
    'flex_dates' : False
}

getArbUpdater = {
    'type':'arbUpdate'
}
get_date_reviser = {
    'type':'revise_dates'
}
getMarket_updater = {
    'type':'arbie_updateMarkets'
}

get_market_updater = {
    'platform' : 'betfair'
}

test = taskSchedular()

on_day_functions:list = []
on_day_param = timedelta(days=0)

nxt_day_functions:list = []
nxt_day_param = timedelta(days=1)

flex_functions:list = test.searchFunctions(flex_dates)
non_flex_functions:list = test.searchFunctions(non_flex_dates)
for function in flex_functions:
    on_day_functions.append((function,on_day_param))
    nxt_day_functions.append((function,nxt_day_param))
for function in non_flex_functions:
    on_day_functions.append((function,on_day_param))

postScrapeTasks = []
postScrapeTasks.extend(test.searchFunctions(get_date_reviser))
postScrapeTasks.extend(test.searchFunctions(getArbUpdater))

market_update_arbie = test.searchFunctions(getMarket_updater)
market_update_scrape = [(test.searchFunctions(get_market_updater)[0],on_day_param)]
market_update_multitask = multitask(market_update_scrape,market_update_arbie)
test.addFunction(market_update_multitask.returnFunctionConfig())

horces_on_day = multitask(on_day_functions,postScrapeTasks)
horces_on_day = horces_on_day.returnFunctionConfig()
test.addFunction(horces_on_day)

horces_nxt_day = multitask(nxt_day_functions,postScrapeTasks)
horces_nxt_day = horces_nxt_day.returnFunctionConfig()
test.addFunction(horces_nxt_day)

now_time = datetime.now() + timedelta(hours=6)

while True:
    test.step()