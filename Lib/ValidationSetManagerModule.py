from .DatasetLibModule import DatasetUtils

from enum import Enum

class ValidationType (Enum):
    NN_FILTER = 1
    SINGLE_RANDOM = 2
    MULTIPLE_RANDOM = 3
    TRAIN_SET = 4


class ValidationSetManager:
    def getValidationSets(vSets,vSetType,trainSet,testPart):
        if (vSets==None or len(vSets)==0):
            if (vSets == None):
                vSets = []
            vSet = None
            if (vSetType=='Train Set'):               
                vSet = trainSet                                             
            elif (vSetType=='NN-Filter'):
                vSet = DPLIB.NNFilter(trainSet, testPart, 1)
            #If random, but not fed into the func, generate one randomly, with size of testPart
            elif (vSetType == 'Multiple Random' or vSetType == 'Single Random'):
                vSet = DatasetUtils.getRandomSubSetUnique(size = len(testPart), inputSet = trainSet)
            if vSet!= None:
                vSets.append(vSet)
        return vSets