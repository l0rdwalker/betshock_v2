class clock:
    def __init__(self,data,depth=3,minIndex=0) -> None:
        self.currentHand = data
        self.depth = depth
        self.size = len(self.currentHand)

        self.justTicked = False

        self.minIndex = minIndex
        self.maxIndex = self.minIndex+self.size-(self.minIndex+depth)-1
        self.index = self.minIndex

        if (depth > 0):
            self.bank = clock(data,depth-1,self.minIndex+1)
        else:
            self.bank = None

    def reduce_range(self):
        self.minIndex += 1
        if not (self.minIndex >= self.maxIndex):
            if (isinstance(self.bank,clock)):
                self.bank.reduce_range()
            self.index = self.minIndex

    def hault(self):
        return self.index == self.maxIndex

    def tick(self):   
        if type(self.bank) == clock:
            self.bank.tick()
            if (self.bank.canTick(self.index)):
                self.index += 1
                self.justTicked = True
            else:
                self.justTicked = False
        elif (self.index < len(self.currentHand)-1):
            self.justTicked = True
            self.index += 1
        else:
            self.justTicked = False

    def getState(self):
        if type(self.bank) == clock:
            previous,existingTeams = self.bank.getState()
            subjectTeam = tuple(self.currentHand[self.index])
            if not subjectTeam[0] in existingTeams:
                existingTeams[subjectTeam[0]] = True
                previous.append(subjectTeam)
                return previous,existingTeams
            else:
                return None
        else:
            return [tuple(self.currentHand[self.index])],{self.currentHand[self.index][0]:True}
        
    def getStateWpr(self):
        state = self.getState()
        if not (state == None):
            return state[0]
        return state
    
    def canTick(self,parentIndex):
        rangeCheck = self.index == self.maxIndex
        parentIndexCheck = parentIndex+1 < self.index
        if (rangeCheck and (self.justTicked == False) and parentIndexCheck):
            self.reduce_range()
            return True
        return False