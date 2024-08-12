from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import os
import dataManagement

class platformManager(ABC):
    def __init__(self,database,router) -> None:
        self.functions = {}
        self.setPlatformName()
        self.runNext = datetime.now()

        baseFile = os.path.dirname(os.path.abspath(__file__))
        sportObjectsDir = os.path.join(os.path.join(baseFile,self.name), 'sports')

        for file in os.listdir(sportObjectsDir):
            if file.endswith('.py'):
                plainName = file[:-3]
                platform,sport = plainName.split('_')
                self.functions[plainName.split('_')[1]] = dataManagement.getModuleByPath(sportObjectsDir, plainName, database, router, [platform,sport])
    
    def getFunctions(self): #This is only really run once on startup. Not typically used during ongoing operations. (At least at the time of writing 10/02/2024)
        functions = []
        for key,item in self.functions.items():
            functions.append(
                {                                
                    'driver':item,
                    'platform':self.name,
                    'type':item.operation,
                    'data':{
                        'sport':key,
                        'function_cofigs':item.get_function_config()
                    }
                }
            )

        return functions
    
    @abstractmethod
    def setPlatformName():
        pass
