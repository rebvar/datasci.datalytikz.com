"""
Chromosome structure for genetic algorithm for dataset instance selection. Includes evaluation 
fields for classification predictions.
"""

from .IChrm_Module import IChrm
import numpy as np

class CHRM_GIS(IChrm):

    def __init__(self, ds, confs_measures, fixedTrainSize = True , extraAsFitness=None):
        """
        Initializer
        """
        self.fixedTrainSize = fixedTrainSize
        self.isCount = False
        self.ds = ds
        self.confs_measures = confs_measures
        self.bestCF = 0.5
        self.extra = None
        self.allCFs = None
        self.extraAsFitness = extraAsFitness


    def isFixedSize(self):
        return self.fixedTrainSize

    def isCount(self):
        return self.isCount

    def addToExtra(self,key,val):
        """
        Adds or replaces an item in a Generic Key value dictionary, that can be used for different purposes
        """
        if self.extra == None:        
            self.extra = {}                
        self.extra[key] = val
    

    def getFitness(self):
        """
        Returns the fitness. If a custom fitness value is specified, it should be added to Extras
        """

        if self.extraAsFitness!=None:
            return self.extra[self.extraAsFitness]
        
        fit = self.getMeanFitness('F')
        if (np.isnan(fit)):
            return 0   
        return float(int(fit*1000.0))/1000.0        
        
    
    def getMin(self, field):    
        """
        Returns the minimum value for each field of a particular fitness when evaluated on multiple
        validation datasets
        """        
        return np.min([self.fitnesses[i][field] for i in range(len(self.fitnesses))])
    

    def getMean(self, field):
        """
        Returns the average value for each field of a particular fitness when evaluated on multiple
        validation datasets
        """

        return np.mean([self.fitnesses[i][field] for i in range(len(self.fitnesses))])
    
    def getSTD(self, field):
        """
        Returns the standard deviation value for each field of a particular fitness when evaluated on
        multiple validation datasets
        """
        return np.std([self.fitnesses[i][field] for i in range(len(self.fitnesses))])


    ###Use the above funtions with specific metric names
    

    def getMeanFitness(self, measure):
        if self.extraAsFitness!=None:
            return self.extra[self.extraAsFitness]
        return self.getMean(measure)      
        
    def SetTrSet(self,value):
        """
        Replaces the dataset. For reusing the instance or for deleting the memory.
        """
        self.ds = value

