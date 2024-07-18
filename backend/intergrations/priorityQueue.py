import math
import random

class queue:
    def __init__(self,minMax=True) -> None:
        self.elements = []
        self.size = 0
        self.minHeap = minMax

    def peek(self):
        if (len(self.elements) == 0):
            return None
        return self.elements[0]

    def isEmpty(self):
        return len(self.elements) == 0
    
    def getLevelFromIndex(self,index:int) -> None:
        return math.floor(math.log2(index+1))
    
    def nodeNumOnLevel(self,index:int) -> None:
        return (2**(index+1)) - 1
    
    def getParentNodeIndex(self,index:int) -> None:
        if (index > 1):
            indexLevel = self.getLevelFromIndex(index)
            nodesOnLevel = index - self.nodeNumOnLevel(indexLevel-1)
            parentIndex = self.nodeNumOnLevel(indexLevel-2) + math.ceil(nodesOnLevel/2)
            return parentIndex
        else:
            return 0
        
    def getChildNodes(self,index):
        if index > 0:
            index = index + 1
            localIndex = index - self.nodeNumOnLevel(self.getLevelFromIndex(index)-1)
            localChildIndex = ((localIndex - 1)*2)
            globalChildIndex = self.nodeNumOnLevel(self.getLevelFromIndex(index)) + localChildIndex
            globalChildIndex = globalChildIndex - 1
            return globalChildIndex
        return 1
        
    def enqueue(self,element):
        if not (isinstance(element, tuple)) and not (isinstance(element,list)):
            element = [len(self.elements),element]
        else:
            element = [element[0],element[1]]
        self.elements.append(tuple(element))
        self.upheap(len(self.elements)-1)

    def upheap(self,index):
        while index > 0:
            parentIndex = self.getParentNodeIndex(index)
            if self.compare(self.elements[index][0],self.elements[parentIndex][0]): #compare swap operation
                temp = self.elements[index]
                self.elements[index] = self.elements[parentIndex]
                self.elements[parentIndex] = temp
                index = parentIndex
            else:
                break

    def dequeue(self):
        if len(self.elements) == 0:
            return None
        elif len(self.elements) == 1:
            element = self.elements.pop()
            return element
        else:
            return self.downheap()

    def downheap(self):
        elementReturn = self.elements[0]
        self.elements[0] = self.elements.pop()
        index = 0
        
        while (True):
            childIndex = self.getChildNodes(index)
            if (childIndex+1 <= len(self.elements)-1):
                if self.compare(self.elements[childIndex][0],self.elements[childIndex+1][0]): #compare swap operation
                    smallest = childIndex
                else:
                    smallest = childIndex+1
                if self.compare(self.elements[smallest][0],self.elements[index][0]): #compare swap operation
                    temp = self.elements[smallest]
                    self.elements[smallest] = self.elements[index]
                    self.elements[index] = temp
                    index = smallest
                else:
                    break
            else:
                break
        return elementReturn
    
    def compare(self,eleOne,eleTwo):
        if (self.minHeap):
            return eleOne < eleTwo
        else:
            return eleTwo < eleOne