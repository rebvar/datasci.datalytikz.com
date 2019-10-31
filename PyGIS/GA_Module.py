"""
Genetic Algorithm Operators. 
"""


from Lib import DPLIB
import numpy as np
import random
from .CHRM_GIS_Module import CHRM_GIS
from .CHRM_GIS_Count_Module import CHRM_GIS_Count

class GA:
    


    def getChromosomeSize (fixedTrainSize, maxChrmSize):
        if (fixedTrainSize):
            return maxChrmSize
        else:
            return np.random.randint(maxChrmSize)+10
           
        
    def select(pop, selectionType = 'TORNAMENT'):
        idx1 = 0;
        idx2 = 0;
        while (idx1 == idx2):
            if selectionType == 'TORNAMENT':
                idx1 = GA.tornament(pop);
                idx2 = GA.tornament(pop);
            elif selectionType == 'ROULETE_WHEEL':
                pass
            else:
                idx1 = np.random.randint(0,len(pop))
                idx2 = np.random.randint(0,len(pop))    
        ds1 = pop[idx1].ds
        ds2 = pop[idx2].ds;
        return ds1, ds2
    
    def getBugSTDForMutation(trainSet):
        labels = trainSet[:,-1].tolist()
        return int(np.std(labels)+1)

    def GetMeanFittness(hmm,count):
        """
        Calculates the average fitness of the top :count population members. All members if :count=0
        """
        if (count == 0):
            count = len(hmm)
        return np.sum([h.getFitness() for h in hmm])/count     
    
    def generateNewPopulation(pop, sizeTop = 0, selectionType = 'TORNAMENT', isCount = False, mad = 0) :
        newPop = []
        for i in range(sizeTop):
            newPop.append(pop[i])
        i = 0
        for i in range(0 , len(pop) - sizeTop,2):
            ds1, ds2 = GA.select(pop, selectionType=selectionType)
                    
            #Ensure two labels for the created offsprings
            while True:
                ds1,ds2 = GA.crossOver(ds1, ds2, ds1.isFixedSize(), isCount = ds1.isCount())
                if len(set(list(ds1[:,-1])))>=2 and len(set(list(ds2[:,-1])))>=2:
                    break

            while True:
                ds1 = GA.Mutate(ds1, isCount = ds1.isCount(), mad = mad)
                if len(set(list(ds1[:,-1])))>=2:                            
                    break

            while True:
                ds2 = GA.Mutate(ds2, isCount = ds2.isCount(), mad = mad)
                if len(set(list(ds2[:,-1])))>=2:
                    break
                    
            newPop.append(ds1)
            newPop.append(ds2)
        return newPop


    def assignFitness(pop, clf, vSets, isCount):
        for i in range(len(pop)):
            clf.buildClassifier(pop[i]);                
            all_confs_measures = []
            all_predictions = clf.evaluateMultiModel(vSets)
            if isCount:
                pass
            else:
                for index, predictions in enumerate(all_predictions):
                    confs_measures = DPLIB.getConfMatrixAndExtMeasures(vSets[index][:,-1],predictions)
                    all_confs_measures.append(confs_measures)
                h = CHRM_GIS(pop[i], all_measures, all_confs_measures);
                pop[i]=h
        return pop

    def createInitialPopulation(pool, popSize, fixedTrainSize, maxChromosomeSize):
        pop = []
        for i in range(popSize):
            uinds = set()
            size = GA.getChromosomeSize(fixedTrainSize,maxChromosomeSize)
            while True:
                #Select a subset that has noth classes
                trSet = DPLIB.getRandomSubSet(size,pool)
                if len(set(list(trSet[:,-1])))>=2:
                    break
            pop.append(trSet)
        return pop
            

    def checkExit(pop, newPop, countComp):
        diff = abs(GA.GetMeanFittness(pop, countComp) - GA.GetMeanFittness(newPop, countComp))
        if (diff < 0.000001):
            exit = True
        else:
            exit = False
        return diff, exit        
    
    def Mutate(ds, mProb = 0.1, mCount = 1, isCount = False, mad = 0.0):
        """
        Performs mutation with specified parameters. 
        Please note that the mutation should consider the fact that datasets might contain 
        repeated instances of the same data row, and the operation should consider consistency. 
        After performing mutation, all instances with exact same data should have a consistent label.

        """
        
        r2 = np.random.rand()        
        if (r2 <= mProb):
            rands = set()
            i=0
                                                
            while(i<mCount):
                            
                r1 = np.random.randint(0,len(ds))
                if len(rands)==len(ds):
                    return ds;
                
                if (r1 in rands):
                    continue
                instLabel = ds[r1,-1]
                
                #Mutation for non binary class values. Shift Using normal distribution random value
                if isCount:
                    shift = int(np.random.randn()*mad)
                    classVal = instLabel + shift
                    if (classVal<0):                    
                        classVal = 0    
                else:
                    classVal = (1 - instLabel)

                st = DPLIB.FindAllSimilarInstancesIndexes(r1, ds)
                
                for r1 in st:
                    rands.add(r1)
                    ds[r1,-1] = classVal
                
                i+=1                               
        return ds    
    



    def roulleteWheel(hmm):
        """
        Roullete Wheel chromosome selection method. One of the selection operators for Genetic algorithm
        """
        weight_sum = np.sum([h.getFitness() for h in hmm])        
        value = np.random.rand() * weight_sum
        current = 0
        for i in range(len(hmm)):
            current += hmm[i].getFitness()
            if (current > value):
                return i                    
        return len(hmm)-1

    
    def tornament(hmm):   
        """
        Tournament Selection operator. Size is kept as two for simplicity, but can be any size.
        """
        vals = [np.random.randint(0,len(hmm)),np.random.randint(0,len(hmm))]
        
        maxInd=-1
        maxFit = 0
        for i in range(len(vals)):        
            if (hmm[i].getFitness()>maxFit):            
                maxFit = hmm[i].getFitness()
                maxInd = i                    
        
        return vals[maxInd]



    def crossOver(ds1, ds2, fixedSize, isCount=False):
        """
        Cross over operator. It supports both one point and two point cross over methods. 
        Further, it can keep the datasets the same size, as well as change the data in a way to
        generate varying size chromosomes. 

        Please note that the cross over should consider the fact that datasets might contain 
        repeated instances of the same data row, and the operation should consider consistency. 
        This is especially inportant since, data can come from multiple sources, as well as, the effect of
        mutation on particular instances from previous generations. 
        After performing crossover, all instances with exact same data should have a consistent label.
        This is done through majority voting rule in the cross over operations.


        """
        ss = len(ds1)
        point1=0
        point2=0

        if (fixedSize):        
            point1 = np.random.randint(ss)
            point2 = point1        
        else:        
            point1 = np.random.randint(ss)
            point2 = np.random.randint(len(ds2))
        
            if (len(ds1)>=4000):            
                point1 = int(len(ds1)/2)

            if (len(ds2)>=4000):            
                point2 = int(len(ds2)/2)        
        
        
        
        np.random.shuffle(ds1)
        np.random.shuffle(ds2)
        ds1c = np.copy(ds1[:point1,:])
        ds2c = np.copy(ds2[:point2,:])
        
        ds1c = np.append(ds1c, ds2[point2:,:], axis=0)
        ds2c = np.append(ds2c, ds1[point1:,:], axis=0)

        
        pSet = set()
        
        for i in range(len(ds1c)):
            if i in pSet:
                continue
            t = list(DPLIB.FindAllSimilarInstancesIndexes(i, ds1c))
            lbl = 0            
            
            
            index=-1;
            for j in range(len(t)):
                index = t[j]
                lbl+=ds1c[index,-1]
                pSet.add(index)            
            
            
            lbl = lbl/(len(t))
            if not isCount:
                if (lbl>=0.5):
                    lbl=1
                else:
                    lbl=0
            else:
                if lbl<0:
                    lbl = 0
            for j in range(len(t)):
                
                index = t[j]
                #Process extra
                #if ((int)ds1c.instance(index).classValue()!=(int)lbl)
                #    ds1c.instance(index).SetExtra(ds1c.instance(index).GetExtra() +"-C="+String.valueOf((int)(1-lbl))+">"+String.valueOf((int)lbl));
                ds1c[index, -1]=lbl
            
        
        
        pSet.clear()
        for i in range(len(ds2c)):        
            if (i in pSet):
                continue
            t = list(DPLIB.FindAllSimilarInstancesIndexes(i, ds2c))
            lbl = 0            
            index=-1;
            for j in range(len(t)):
                index = t[j]
                lbl+=ds2c[index,-1]
                pSet.add(index)            
            
            
            lbl = lbl/len(t)

            if not isCount:

                if (lbl>=0.5):
                    lbl=1
                else:
                    lbl=0
            else:
                if lbl<0:
                    lbl = 0

            for j in range(len(t)):
                
                index = t[j]
                #Process extra
                #if ((int)ds2c.instance(index).classValue()!=(int)lbl)
                #    ds2c.instance(index).SetExtra(ds2c.instance(index).GetExtra() +"-C="+String.valueOf((int)(1-lbl))+">"+String.valueOf((int)lbl));
                ds2c[index, -1]=lbl
            
        
        return ds1c, ds2c

    
    
    
     