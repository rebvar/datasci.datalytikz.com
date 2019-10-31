import numpy as np
import random

class RejectedDatasetsTracker:
    def __init__(self, threshold):
        self.updateThreshold(threshold)
    
    def reset(self):
        self.threshold = thresholdDef
        self.thresholds = [threshold]
        self.ejectedFits.clear()
        self.rejectedPerfs.clear()
        self.rejectedTestPerfs.clear()

    def updateThreshold(self, threshold):
        self.thresholdDef = threshold
        self.threshold = threshold
        self.thresholds = [threshold]
        self.ejectedFits = []
        self.rejectedPerfs = []
        self.rejectedTestPerfs = []

class DatasetUtils:


    def getRandomSubSetUnique(size,inputSet):
        uinds = set()
        rSet = []
        j = 0
        inputLength = len(inputSet)
        while (j < size):
            index = np.random.randint(inputLength)
            if (not  index in uinds):
                uinds.add(index)       
            else:         
                continue
            rSet.append(inputSet[index])        
            j+=1               
        return np.array(rSet)


    def getRandomSubSetWithReplacement(size,inputSet):
        rSet = []
        j = 0
        inputLength = len(inputSet)
        while (j < size):
            index = np.random.randint(inputLength)
            rSet.append(inputSet[index])        
            j+=1
               
        return np.array(rSet)

    def getRandomSubsetsLimitClass(inputSet, maxSize,countClasses, countSets):
        retSets = []
        for i in range(countSets):
            retSets.append(vSets.append(np.array(getRandomSubsetUniqueLimitClass(inputSet, maxSize,countClasses))))
        return retSets

    def getRandomSubsetUniqueLimitClass(inputSet, maxSize, countClasses = 2):
        
        vSet = []
        size = int(maxSize / 2) + np.random.randint(0,maxSize / 2);
        
        dividers = sorted(random.sample(range(1, size), countClasses - 1))
        sizes = [a - b for a, b in zip(dividers + [size], [0] + dividers)]
        inputSet = np.copy(inputSet)
        np.random.shuffle(inputSet)
        j = 0

        cntClasses = [0 for _  in range(countClasses)]

        while True:
            k = int(inputSet[j,-1])                
            if(cntClasses[k] < sizes[k]):
                vSet.append(inputSet[j])
                cntClasses[k]+=1
            j+=1     
        return vSet