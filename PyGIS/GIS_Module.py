from Lib import DPLIB
from Lib import ValidationSetManager
from Lib import Common
from .GA_Module import GA
from Lib import GLOB
from .CHRM_GIS_Module import CHRM_GIS
from .CHRM_GIS_Count_Module import CHRM_GIS_Count
import numpy as np
import copy
from Lib import RejectedDatasetsTracker, DatasetUtils

class GIS:

    def __init__(self, pars):    
        self.rejectTracker = RejectedDatasetsTracker(threshold = 0.1)
        self.popSize = pars['popSize']
        self.chrmSize = pars['chrmSize']
        self.folds = pars['folds']
        self.numGens = pars['numGens']
        self.numParts = pars['numParts']
        self.sizeTopP = pars['sizeTop']
        self.count = 1
        self.doCluster = False;
        self.rejectTracker = rejectTracker
        self.trdID = 0
        self.output = []
        self.FinalPrediction = []
        self.isCount = ('isCount' in pars.keys()) and (pars['isCount'] == True)
        self.countComp = 0
        self.mad = 0
        self.keySet = self.getKeySetKeys()
        self.fixedTrainSize = (pars['trainType'] == 'FX')

    def setRejectTrackerThreshold(self,threshold):
        self.rejectTracker.updateThreshold(threshold)

    def prnt (self, *args):
        self.output.append('  '.join([str(a) for a in args]))
    
    def getKeySetKeys(self):
        if self.isCount:
            self.keySet = list(DPLIB.getMeasuresCount([0,1,2,3],[0,1,2,3]).keys())
        else:
            self.keySet = list(DPLIB.MEASURES_BIN.keys())
        return self.keySet
            
    def predict(self, testSet):
        
        if self.isCount:
            pass    
        else:                
            l = GLOB(clfName).getClassifier()
            l.buildClassifier(self.FinalDataset);                
            predictions = l.evaluateModel(testPart);
            return predictions


    def setIsFixedTrainSize (self,fixedTrainSize):
        self.fixedTrainSize = fixedTrainSize

    def getIsFixedTrainSize(self):
        return self.fixedTrainSize

    def fit(self, trainSet, testSet, vSets, vSetType, clfName):
        
        if self.isCount:
            self.mad = GA.getBugSTDForMutation(trainSet)
        
        if len(set(list(trainSet[:,-1])))<2:
            self.prnt('Error: Number of classes can not be less than two.')
            print('Error: Number of classes can not be less than two.')
            return
        
        trainSet, testSet = np.copy(trainSet), np.copy(testSet)

        tstSize = len(testSet)
        partSize = int(tstSize / self.numParts)
        
        isOK = True
        
        np.random.shuffle(testSet)
        self.FinalLearner = None
        self.FinalDataset = None
        
        
        diffs = []
        
            
        vSets = ValidationSetManager.getValidationSets(vSets,vSetType,trainSet,testPart)
        pop = GA.createInitialPopulation(trainSet, self.popSize, fixedTrainSize, self.chrmSize)
        pop = GA.assignFitness(pop, GLOB(clfName).getClassifier(),vSets, self.isCount)
        pop = DPLIB.SortPopulation(pop)
        
        for g in range(self.numGens):
            self.prnt(str(g)+" ");                
            newPop = GA.generateNewPopulation(pop,self.sizeTopP, selectionType = 'TORNAMENT',isCount = self.isCount, mad = mad)
            newPop = GA.assignFitness(newPop, GLOB(clfName).getClassifier(),vSets, self.isCount)
            newPop = DPLIB.SortPopulation(newPop)    
            newPop, rdel = DPLIB.CombinePops(pop, newPop);
            rdel = None;              
            diff, exit = GA.checkExit(pop, newPop, self.countComp)

            diffs.append(diff)
            pop.clear()
            pop = newPop
                
            if (pop[0].getFitness() > 0.0) and (exit):
                break
        self.FinalDataset = pop[0].ds
        