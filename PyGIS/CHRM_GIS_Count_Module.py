"""
Chromosome structure for genetic algorithm for dataset instance selection. Includes evaluation 
fields for regression predictions.
"""

from .IChrm_Module import IChrm
import numpy as np

class CHRM_GIS_Count(IChrm):

    def __init__(self, ds, fitness, fitnesses=None, extraAsFitness = None):
        
        """
        Initializer
        Parameters:
        ds : corresponding dataset
        fitness: Asscociated fitness value
        fitnesses: a list of fitness values when evaluated on multiple validation datasets
        extraAsFitness: Specify custom field as fitness
        """
        self.ds = ds
        self.fitness = fitness
        self.fitnesses = fitnesses        
        self.extra = None
        self.extraAsFitness = extraAsFitness


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
        return self.getCustom()
        
    
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
    
    def getMeanFitness(self):
        return 1.0/(self.getMean("are")+1.0)       
    
    def getCustom(self):
        return 1.0/(self.getMean("are")+1.0)    
    
    
    def SetTrSet(self,value):
        """
        Replaces the dataset. For reusing the instance or for deleting the memory.
        """
        self.ds = value

