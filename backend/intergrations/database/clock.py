class clock:
    def __init__(self,data) -> None:
        for key,value in data.items():
            self.localList = value
            data.pop(key)
            break
        
        self.index = 0
        if (len(data) > 0):
            self.bank = clock(data)
        else:
            self.bank = None

    def tick(self):   
        if self.tickOver():
            self.index = 0
            if self.bank:
                self.bank.tick()
        else:
            self.index += 1

    def hault(self):
        if self.bank == None:
            return self.tickOver()
        return self.bank.hault()

    def getState(self):
        if type(self.bank) == clock:
            data = []
            data.extend([self.localList[self.index]])
            data.extend(self.bank.getState())
            return data
        else:
            return [self.localList[self.index]]
    
    def tickOver(self):
        return self.index+1 > len(self.localList)-1