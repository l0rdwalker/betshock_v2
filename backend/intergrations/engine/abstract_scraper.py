from abc import ABC, abstractmethod
import os
from datetime import datetime,timedelta
import dataManagement
from abstract_task import task

class scraper(task):
    def __init__(self,attributes) -> None:
        super().__init__(attributes)
        self.startTimes = []
        self.operation = 'scrape'
        self.flex_dates = False
        
    def get_function_config(self):
        return {
            'flex_dates':self.flex_dates
        }
                    
    def init(self,data):
        try:
            data = self.aquireOdds(data)
            self.selectNextRunTime()
        except Exception as e:
            print(e)
        finally:
            return {'data':data, 'platform': self.platformName, 'sport': self.sport}
    
    def addStartTime(self,date:datetime):
        self.startTimes.append(date)
        
    def whenNextRun(self):
        return datetime.now() + timedelta(minutes=5)
    
    def get_flex_date_status(self):
        return self.flex_dates
        
    def selectNextRunTime(self):
        try:
            currentTime = datetime.now()
            smallest = currentTime + timedelta(days=1)
            smallest = smallest.replace(hour=6,minute=0,second=0,microsecond=0)
            for date in self.startTimes:
                if date > currentTime:
                    if smallest > date:
                        smallest = date
            self.startTimes = []
            nextToGo =  smallest
        except:
            nextToGo = currentTime
            
        timeElapsed = nextToGo - currentTime
        halfWayPoint = timeElapsed/2
        nextScheduled = currentTime + halfWayPoint

        if nextToGo - nextScheduled > timedelta(minutes=10):
            self.nextScheduledRun = nextScheduled
        else:
            self.nextScheduledRun = currentTime + timedelta(minutes=11)
        
    @abstractmethod
    def aquireOdds(self):
        pass
    
    