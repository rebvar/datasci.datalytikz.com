from Lib import DPLIB
from Lib import Common
from .GA_Module import GA
from Lib import GLOB
from .CHRM_GIS_Module import CHRM_GIS
from .CHRM_GIS_Count_Module import CHRM_GIS_Count

import numpy as np
import copy

class GISKS2:

    
    def __init__(self, pars, file):
        

        self.popSize = pars['popSize']
        self.chrmSize = pars['chrmSize']
        self.folds = pars['folds']
        self.numGens = pars['numGens']
        self.numParts = pars['numParts']
        self.sizeTopP = pars['sizeTop']
        self.iters = pars['iters']
        self.count = 1
        self.doCluster = False;
        self.file = file
        self.trdID = 0
        self.output = []
        self.FinalPrediction = []

        #Default to Binary Prediction
        if 'isCount' in pars.keys():
            self.isCount = pars['isCount']
        else:
            self.isCount = False
        self.pars = pars
        

    def prnt (self, *args):
        self.output.append('  '.join([str(a) for a in args]))

    def run(self, trainSeti, testSeti, name, fout, vSets, vSetType, fixedTrainSize, log, ignoreOK, threshold, 
            thresholds, rejectedFits, rejectedPerfs, rejectedTestPerfs, clfName):
        
        mad = 0.0
        if self.isCount:
            keySet = list(DPLIB.getMeasuresCount([0,1,2,3],[0,1,2,3]).keys())
            mad = DPLIB.SetBugCountForMut(trainSeti)
        else:
            keySet = list(DPLIB.getExtMeasures({"tp":1,"tn":2,"fp":3,"fn":4}).keys())
        startTime = Common.getCurrentTimeMil()
        tempTime = 0
        spentISTime = 0

        #For Binary Prediction, isCount = False
        auc = 0
        preds = []
        pop = []
        

        trainSet = np.copy(trainSeti)
        testSet = np.copy(testSeti)
        pop.clear()

        tstSize = len(testSet)
        partSize = int(tstSize / self.numParts)
        preds.clear()
        diffs = []
        auc = 0.0
        

        #For isCount = True
        actuals = []
        prrs = []

        if (log):        
            self.prnt("#GIS-OPTIONS;;For="+name+"@"+":iters=" + str(self.iters) + "-POPSIZE=" + str(self.popSize) + "-NumParts=" + str(self.numParts) 
                       + "-NumGens=" + str(self.numGens) + "-sizeTop=" + str(self.sizeTopP) + "-Learner=" + clfName+"\n");
        
        
        
        isOK = True
        
        np.random.shuffle(testSet)
        self.FinalLearners = []
        self.FinalDatasets = []
        for p in range(self.numParts):
        
            diffp = []
                        
            self.prnt("\n"+str(p) + ": ")            
            
            tempTime = Common.getCurrentTimeMil()
            pop.clear()
            start = p * partSize
            end = (p + 1) * partSize
            if (end > tstSize):
                end = tstSize;
            
            if (p == self.numParts - 1):
                end = tstSize
            

            testPart = testSet[start:end,:]
            
            spentISTime += Common.getCurrentTimeMil() - tempTime;
            
            uinds = set()
            if (vSets==None or len(vSets)==0):
            
                if (vSets == None):
                    vSets = []
                
                vSet = None
                retVal = ""
                if (vSetType=='Train Set'):
                
                    vSet = trainSeti
                    if (log):                    
                        retVal = DPLIB.getStats(vSet, True, True, True);
                        self.prnt("#VSETINFO;;prt="+str(p)+";;For="+name+"@"+":"+retVal+"\n");
                        
                        retVal = None;
                                                        
                elif (vSetType=='NN-Filter'):
                    tempTime = Common.getCurrentTimeMil()
                    vSet = DPLIB.NNFilter(trainSet, testPart, 1)
                    spentISTime+=Common.getCurrentTimeMil() - tempTime
                    
                    if (log):
                    
                        retVal = DPLIB.getStats(vSet, True, True, True);
                        self.prnt("#VSETINFO;;prt="+str(p)+";;For="+name+"@"+":"+retVal+"\n");                        
                        retVal = None
                    
                
                #If random, but not fed into the func, generate one randomly, with size of testPart
                elif (vSetType == 'Multiple Random' or vSetType == 'Single Random'):
                                    
                    size = len(testPart)
                    vSet = []
                    j = 0;
                    while (j < size):
                        index = np.random.randint(trainSet.numInstances())

                        if (not  index in uinds):
                            uinds.add(index)                        
                        else:                        
                            continue                        

                        vSets.append(trainSet[index])
                        
                        j+=1
                    
                    if (log):
                    
                        retVal = DPLIB.getStats(vSet, true, true, True);
                        self.prnt("#VSETINFO;;prt="+str(p)+";;For="+name+"@"+":"+retVal+"\n");                        
                        retVal = None;
                    
                    vSet = np.array(vSet)
                                   

                elif (vSetType == '!!TEST!!'):
                

                    #Upper Bound. Should not be used.
                    self.prnt ("Should not be used.")
                    vSet = testSeti;
                    if (log):
                    
                        retVal = DPLIB.getStats(vSet, True, True, True);
                        self.prnt("#VSETINFO;;prt="+str(p)+";;For="+name+"@"+":"+retVal+"\n");                        

                        retVal = None;
                    
                
                elif vSetType == 'KS2':
                    vSet = None
                vSets.append(vSet)
            
            else:
            
                retVal = "";
                for vSet in vSets:
                
                    if (log):                     
                        retVal = DPLIB.getStats(vSet, True, True, True);
                        self.prnt("#VSETINFO;;prt="+str(p)+";;For="+name+"@"+":"+retVal+"\n");                        
                        retVal = None;
                     
                
                                                         

            
            
            
            for i in range(self.popSize):
                tempTime = Common.getCurrentTimeMil()
                uinds.clear()
                
                size = 0
                
                if (fixedTrainSize):
                    size = self.chrmSize
                else:
                    size = np.random.randint(self.chrmSize)+10
                
                
                while True:
                    trSet = []
                    j = 0
                    while (j < size):
                        index = np.random.randint(len(trainSet))
                    
                        trSet.append(trainSet[index])
                    
                        if (not index in uinds):
                            uinds.add(index)
                    
                        j+=1;                
                
                    spentISTime += Common.getCurrentTimeMil() - tempTime
                    trSet = np.array(trSet)
                    if len(set(list(trSet[:,-1])))>=2:
                        break

                
                tempTime = Common.getCurrentTimeMil()
                
                pv, p_vals = DPLIB.checkSimilarity(trSet[:, :-1], testPart[:,:-1])
                                                                        
                if self.isCount:
                    h = CHRM_GIS_Count(trSet, None, extraAsFitness = 'p-val');
                    h.addToExtra('p-val', sum( p_vals))
                    pop.append(h)
                else:

                    h = CHRM_GIS(trSet, None, None, extraAsFitness = 'p-val');
                    h.addToExtra('p-val', sum( p_vals))
                    pop.append(h)
                
                spentISTime += Common.getCurrentTimeMil() - tempTime
                            
            
            tempTime = Common.getCurrentTimeMil()
            pop = DPLIB.MySort(pop);
            spentISTime += Common.getCurrentTimeMil() - tempTime
            
            cnt = 0;
            g = 0;
            for g in range(self.numGens):
                self.prnt(str(g)+" ");                
                if (log):
                    pass
                    #retVal = ""
                    #for i in range(len(pop)):
                    
                    #    chrm = pop[i]
                    #    retVal = DPLIB.getStats(chrm.ds, False, False, False);
                    #    self.prnt("#POPITNFO;;gn="+str(g)+";;prt="+str(p)+";;For="+name+"@"+":"+retVal+"\n");
                    #    self.prnt("#POPITVALS;;gn="+str(g)+";;prt="+str(p)+";;For="+name+"@"+":"+"rpaf="+str(chrm.fitness).replace(", ", ",")
                    #            +";;conf="+str(chrm.conf).replace(", ", ",")+";;fit="+str(chrm.getFitness())+";;TConf2="+str(chrm.testConf).replace(", ", ",")+";;TRpaf2="+str(chrm.testFitness).replace(", ", ",")+"\n");                        
                    #    retVal = None;

                

                tempTime = Common.getCurrentTimeMil()
                newPop = []
                for i in range(self.sizeTopP):
                    newPop.append(pop[i])
                
                
                
                i = 0
                for i in range(0 , len(pop) - self.sizeTopP,2):
                    idx1 = 0;
                    idx2 = 0;
                    while (idx1 == idx2):
                        if (cnt >= 3):
                            idx1 = np.random.randint(len(pop))
                            idx2 = np.random.randint(len(pop))
                        else:
                            idx1 = GA.tornament(pop);
                            idx2 = GA.tornament(pop);
                            cnt+=1
                        
                    
                    cnt = 0
                    ds1 = pop[idx1].ds
                    ds2 = pop[idx2].ds;
                    while True:

                        ds1,ds2 = GA.crossOver(ds1, ds2,fixedTrainSize, isCount = self.isCount);
                        if len(set(list(ds1[:,-1])))>=2 and len(set(list(ds2[:,-1])))>=2:
                            break
                        self.prnt ('repeat cross')
                    while True:
                        ds1 = GA.Mutate(ds1, isCount = self.isCount, mad = mad)
                        if len(set(list(ds1[:,-1])))>=2:                            
                            break
                        self.prnt ('repeat mut ds1, because all elements are of type one class')

                    while True:

                        ds2 = GA.Mutate(ds2, isCount = self.isCount, mad = mad)
                        if len(set(list(ds2[:,-1])))>=2:
                            break
                        self.prnt ('repeat mut ds1, because all elements are of type one class')
                    if self.isCount:
                        newPop.append(CHRM_GIS_Count(ds1, None, extraAsFitness = 'p-val'))
                        newPop.append(CHRM_GIS_Count(ds2, None, extraAsFitness = 'p-val'))
                    else:
                        newPop.append(CHRM_GIS(ds1, None,extraAsFitness = 'p-val'))
                        newPop.append(CHRM_GIS(ds2, None,extraAsFitness = 'p-val'))
                
                
                spentISTime += Common.getCurrentTimeMil() - tempTime;
                
                for i in range(len(newPop)):
                    
                    tempTime = Common.getCurrentTimeMil()
                    
                    
                    pv, p_vals = DPLIB.checkSimilarity(newPop[i].ds[:,:-1],testPart[:,:-1])                    
                    
                    newPop[i].addToExtra('p-val',sum( p_vals))
                    
                    spentISTime += Common.getCurrentTimeMil() - tempTime
                    
                
                
                tempTime = Common.getCurrentTimeMil();
                
                newPop = DPLIB.MySort(newPop);
                exit = False;
                countComp = 0;
                
                newPop, rdel = DPLIB.CombinePops(pop, newPop);
                
                
                if (log):
                    pass
                    #retVal = ""
                    #for i in range(len(rdel)):
                    
                    #    chrm = rdel[i];
                    #    retVal = DPLIB.getStats(chrm.ds, False, False, False);
                    #    self.prnt("#POPDELITNFO;;gn="+str(g)+";;prt="+str(p)+";;For="+name+"@"+":"+retVal+";;rpaf="+str(chrm.fitness).replace(", ", ",")
                    #            +";;conf="+str(chrm.conf).replace(", ", ",")+";;fit="+str(chrm.getFitness())+";;TConf2="+str(chrm.testConf).replace(", ", ",")+";;TRpaf2="+str(chrm.testFitness).replace(", ", ",")
                    #            +"\n");
                        
                    #    retVal = None;                    

                rdel = None;                                               
                
                diff = abs(GA.GetMeanFittness(pop, countComp) - GA.GetMeanFittness(newPop, countComp))
                if (diff < 0.000001):
                    exit = True;
                
                
                diffp.append(diff)
                
                pop = newPop;
                if (pop[0].getFitness() > 0.0) and (exit):
                    break
                
                exit = False;
                spentISTime += Common.getCurrentTimeMil() - tempTime;
            
            
            
            w = []
            if (self.count == 0):
                self.count = len(pop)
            
            for i in range(self.count):
                l = GLOB(clfName).getClassifier();
                tds = pop[i].ds
                self.FinalLearners.append(l)
                self.FinalDatasets.append(tds)
                testPartI = testPart;                                        
                    
                l.buildClassifier(tds);
                
                if self.isCount:
                    actual = DPLIB.getActuals(testPartI)
                    prr = l.evaluateModel(testPartI)
                    #vals = DPLIB.getMeasuresCount(actual,prr)
                
                    actall = None
                    predall = None
                    if (len(actuals) == self.count):
                
                        actuals[i] = actuals[i]+actual
                        prrs[i] = prrs[i] + prr                
                    else:                
                        actuals.append(actual)
                        prrs.append(prr)
                
                else:
                                                    
                    vec = l.evaluateModel(testPartI);
                
                    if (len(preds) == self.count):
                        preds[i]+=list(vec)
                    else:
                        preds.append(list(vec))
                
                    
                if (log):
                    pass
                    #retVal = DPLIB.getStats(tds, True, True, True);            
                    #self.prnt("#TRPRTNFO;;prt="+str(p)+";;For="+name+"@"+":"+retVal+"\n");

                    #retVal = DPLIB.getStats(testPart,true,true, True);            
                    #self.prnt("#TSTPRTNFO;;prt="+str(p)+";;For="+name+"@"+":"+retVal+"\n");
                    #vals = DPLIB.getConfMatrix(testPart[:,-1],vec)

                    #self.prnt("#TSTPRTVALS;;prt="+str(p)+";;For="+name+"@"+":"+
                    #        "rpaf="+str(DPLIB.getMeasures(vals)).replace(", ", ",")
                    #            +";;conf="+str(vals).replace(", ", ",")+"\n");
                    
                    #retVal = None;
                
                    
                w.append(pop[i].getFitness())                            
                    
        
        isOK = True

        if not isOK:
            pass
        else:
            thresholds.append(pop[0].getFitness())
        
        
        self.prnt();
        self.prnt("Best Top Fitness:"+str(pop[0].fitness))
        self.prnt("Best Fitness (mean):",pop[0].getMeanFitness())
                

        if self.isCount:
            vals = DPLIB.getMeasuresCountSet(actuals,prrs);
        else:
            vals1 = DPLIB.getConfMatrixSet(testSet[:,-1],preds)
            vals = DPLIB.getMeasures(vals1)
        
        
        if (isOK):
        
            if not self.isCount:

                if (len(preds) == 1):
                    auc = DPLIB.getAUC(testSet[:,-1],preds[0])
                else:
                    auc = DPLIB.getAUCSet(testSet[:,-1],preds);
            
                vals['auc'] = auc
                self.prnt();
                self.prnt("#CONF-TEST:"+name+":" + self.file + ": "+ str(vals1));            
            
                self.prnt();
                self.prnt(name+":" + self.file + ": "+str(vals));
            
                self.prnt();
            else:
                self.prnt();
                self.prnt(name+":" + self.file + ": "+str(vals));
                self.prnt();
        else:
        
            
            bestI = pop[0]
            rejectedFits.append(bestI.getFitness())
            
            rejVals = copy.deepcopy(bestI.fitness)
            rejectedPerfs.append(rejVals);
                        
            testRejVals = copy.deepcopy(vals);
                                    
            rejectedTestPerfs.eppend(testRejVals);
            
            
            self.prnt("#NOTOKPREDS----" + name+":" + self.file + ": "+ str(vals));
            
            if not self.isCount:
                self.prnt();
                self.prnt("#NOTOKPREDS----"+"#CONF-TEST:"+name+":" + self.file + ": "+ str(vals1));
                                                
                
        time = Common.getCurrentTimeMil()-startTime;
        
        
        self.prnt("#TIME-FOR:"+name+":" + self.file + ": "+str(time))
        
        self.prnt("#TIME-FOR-IS:"+name+":" + self.file + ": "+str(spentISTime));        
        
        return isOK;   