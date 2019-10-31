from PyLSH import LSHSuperBit, SuperBit
from PyLSH import LSHMinHash, MinHash
from Lib import DPLIB
from Lib import Common
import numpy as np
import random
from Lib import GLOB
from PyGIS import CHRM_GIS
from PyGIS import CHRM_GIS_Count


class CPDP_LSH_Binary:

    def __init__(self, pars, file):
        
        self.file = file;
        self.pars = pars
        self.maxStages = pars['maxStages']
        self.minStages = pars['minStages']
        self.maxBuckets = pars['maxBuckets']
        self.minBuckets = pars['minBuckets']
        self.numOptions = pars['numOptions']
        self.isCount = pars.get('isCount',False)

        self.output = []

    def prnt (self, *args):
        self.output.append('  '.join([str(a) for a in args]))

    def CreateBucketsTune(self,trainSet, testSet, vSets, name, testCut, iternum, save, superbit, clfName, tunelrn):

        startTime = Common.getCurrentTimeMil()
        best = None
        bestStages = 0
        bestBuckets = 0
        bestOut = None
        spentTimeIS = 0
        tempTime = 0
        rand = random.Random(Common.getCurrentTimeMil())
        for i in range(self.numOptions):
        
            while True:
                stages = rand.randint(0,self.maxStages-1)+self.minStages
                buckets = rand.randint(0, self.maxBuckets-1)+self.minBuckets
                break
                #if buckets>stages:
                #    break

            chrm = None
            while (True):            
                chrm, out = self.CreateBuckets(trainSet, testSet, vSets, name, testCut, iternum, save, superbit, stages, buckets, False, clfName, tunelrn);
                if chrm != None:
                    break
            
            
            spentTimeIS+=float(chrm.extra["SPENT-TIME-IS"])
            
            if (best == None):            
                best = chrm
                bestBuckets = buckets
                bestStages = stages 
                bestOut = out           
            else:
                if (chrm.getFitness()>best.getFitness()):
                    best = chrm;
                    bestBuckets = buckets
                    bestStages = stages
                    bestOut = out       
        
        
        self.output += out
        time = Common.getCurrentTimeMil()-startTime
        
        
        self.prnt("#TIME-FOR:"+name+":" + self.file+ ": "+str(time)+"\n");        
        self.prnt("#TIME-FOR-IS:"+name+":" + self.file+ ": "+str(spentTimeIS)+"\n");   
        
        return best, out

    def CreateBuckets(self,trainSet, testSet, vSets, name, testCut, iternum, save, superbit, stages, buckets, doprint,clfName, tunelrn):
        
        out = []
        if self.isCount:
            keySet = list(DPLIB.getMeasuresCount([0,1,2,3],[0,1,2,3]).keys())
        else:
            keySet = list(DPLIB.getExtMeasures({"tp":1,"tn":2,"fp":3,"fn":4}).keys())
        
        
        out.append( "#STARTED FOR-"+name+":" + self.file+ ": ")
        
        startTime = Common.getCurrentTimeMil();
        spentIsTime = 0;
        tempTime = 0;
        
        out.append("#Using also Label For train in LSH");
        
        if (vSets == None):

            vSets = []
            vSets.append(trainSet);
  
        
        if (save):
            DPLIB.SaveToCsv(trainSet, "MAIN-TRAIN-FILE-"+"ITER="+str(iternum)+"--"+"METHOD="+name+"--FILE="+self.file+"--");
            DPLIB.SaveToCsv(testSet, "MAIN-TEST-FILE-"+"ITER="+str(iternum)+"--"+"METHOD="+name+"--FILE="+self.file+"--");
            for i in range(len(vSets)):
    
                DPLIB.SaveToCsv(trainSet, "VSET-FILE-"+"INDEX="+str(i)+"ITER="+str(iternum)+"--"+"METHOD="+name+"--FILE="+self.file+"--")
      
  
        
        np.random.shuffle(trainSet)
        np.random.shuffle(testSet)
        tempTime = Common.getCurrentTimeMil();
        count = len(trainSet)
        bins = {}
        # R^n
        n = trainSet.shape[1]-1
        
        binid = 0
        #lshmin = LSHMinHash(stages, buckets, n);
        try:
            lshsuper = LSHSuperBit(stages = stages,buckets = buckets,dimensions = n)
        except Exception as ex:
            print ('##SuperBit with specified parameters failed:'+str(ex))
            return None
        sp = 0.75;
        # Compute a SuperBit signature, and a LSH hash
        for i in range(count):
            vector = trainSet[i,1:].tolist()
      
            hash = None
            if (superbit):
                hash = lshsuper.hash(vector);
            else:
                ##Minhash support
                # #hash = lshmin.hash(vecBool);
                pass
                
            binid = hash[0]
            if not binid in bins.keys():
                bins[binid] = []
      

            bins[binid].append(trainSet[i])
  
        
        spentIsTime+=Common.getCurrentTimeMil()-tempTime;
        
        numBins = len(bins.keys())

        for binid in bins.keys():
            bins[binid] = np.array(bins[binid])


        out.append("#Number of BINS:" +name+":" + self.file+ ": " +str( numBins))

        pop = []
        
        
        for i in bins.keys():
            
            trSet = bins[i];
            l = GLOB(clfName, tunelrn).getClassifier()
            
            #if (tunelrn):    
            #    l = l.getTunedCLF(trSet, vSets,fout,name, file);
      
            l.buildClassifier(trSet)
            cf = 0
            j = 0
            
            allvecs = []
            confs = []
            allcfs = []
            allaucs = []
            valsA = None
            confsA = None
            aucA = 0.0
            for vSet in vSets:
        
                vec = None
                actuals = None
                      
                vec = l.evaluateModel(vSet)          
                actuals = vSet[:,-1]
                
                vals = None
                auc = 0
                if self.isCount:
                    vals = DPLIB.getMeasuresCount(actuals,vec)
                else:

                    auc = DPLIB.getAUC(actuals,vec)
                    aucA+=auc
                    allaucs.append(auc)
                    if (testCut):
                        vCF = 0.1;
                        bestCF = 0
                        bestCFVal = -1
                        bestVals = None

                        while True:
                                
                            tvals = DPLIB.getConfMatrix(actuals,vec,vCF)
                            measures = DPLIB.getMeasures(tvals)
                            fit = measures["F"]*measures["GMean1"]
                            if (fit>bestCFVal or bestVals == None):
                
                                bestCFVal = fit
                                bestCF = vCF
                                bestVals = tvals
                                      
                            vCF+=0.1
              
                            if(vCF>=1):
                                break
                    
                    
                    
                        if (confsA==None):
            
                            confsA = {key:0 for key in bestVals.keys()}
                        
              
                    
                    
                    
                        for j in confsA.keys():
                            confsA[j] += bestVals[j]
               
                    
                        confs.append(bestVals)
                    
                        vals = DPLIB.getMeasures(bestVals)
                        cf+=bestCF
                        allcfs.append(bestCF)
          
                    else:
        
                        tvals = DPLIB.getConfMatrix(actuals,vec)
                    
                        if (confsA==None):
            
                            confsA = {key:0 for key in tvals.keys()}
                     
              
                    
                        for j in confsA.keys():
                            confsA[j] += tvals[j]
               
                    
                        confs.append(tvals)
                    
                        vals = DPLIB.getMeasures(tvals);
                        allcfs.append(DPLIB.DefaultCF)

                
                allvecs.append(vals)
                
                if (valsA == None):
                    valsA = {key:0 for  key in keySet}
                    
          

                for j in keySet:
                    valsA[j] += vals[j]
          
      
            for j in keySet:
                valsA[j] /= len(vSets)
      
            h = None
            if not self.isCount:
                for j in confsA.keys():
                    confsA[j] /= len(vSets);
      
            
                if (testCut):    
                    cf/=len(vSets)
                  
                aucA/=len(vSets)
            
                h = CHRM_GIS(trSet, valsA, aucA)
                h.fitnesses = allvecs
                h.aucs = allaucs
                h.conf = confsA
                h.confs = confs
                h.allcfs = allcfs
                if (testCut):    
                    h.bestCF = cf;        
                else:    
                    h.bestCF = DPLIB.DefaultCF;
            else:
            
                
                h = CHRM_GIS_Count(trSet, valsA)
                h.fitnesses = allvecs
                
            pop.append(h)
            l = None
  
        
        tempTime = Common.getCurrentTimeMil();
        pop = DPLIB.MySort(pop)
        spentIsTime+= Common.getCurrentTimeMil() - tempTime;
        top = pop[0]
        
        out.append("#Instances in Top:" + str(len(top.ds)));

        out.append("#STAGES:" +name+":" + self.file+ ": " + str(stages));
        out.append("#BUCKETS:" +name+":" + self.file+ ": " + str(buckets));
        if not self.isCount:
            out.append("#BEST-CF-VALUE:" +name+":" + self.file+ ": " + str(top.bestCF));

        l = GLOB(clfName, tunelrn).getClassifier()
        
        if (tunelrn):

            l = l.getTunedCLF(top.ds, vSets,fout,name, file);
                        
            out.append("#TUNE-LRN-PARAMS-"+name+":" + self.file+ ": " + str(l.selectedParams))
            sCheck = l.getCLFOptions()
            out.append("#SETSET-LRN-PARAMS-"+name+":" + self.file+ ": " + str(sCheck))


        l.buildClassifier(top.ds)
        
        vec = l.evaluateModel(testSet)
        
        out.append("#LSH-FOR-TOP-ONLY")

        if self.isCount:
            vals = DPLIB.getMeasuresCount(testSet[:,-1],vec)
            out.append(name+":" + self.file+ ": "+str(vals))
        else:        
            tvals = DPLIB.getConfMatrix(testSet[:,-1],vec,top.bestCF)        
            out.append("#CONF-TEST-"+name+":" + self.file+ ": "+str(tvals));
            vals = DPLIB.getMeasures(tvals)
            auc = DPLIB.getAUC(testSet[:,-1],vec)
            vals['auc'] = auc
            out.append(name+":" + self.file+ ": "+str(vals))

        for i in range(len(pop)):

            pop[i] = None
  
        
        pop = None
        
        for i in bins.keys():    
            bins[i] =  None
            
          
        
        bins = None       
        
        time = Common.getCurrentTimeMil()-startTime;
        
        if (name.find("LSHTune")<0):
            out.append("#TIME-FOR:"+name+":" + self.file+ ": "+str( time));
            out.append("#TIME-FOR-IS:"+name+":" + self.file+ ": "+str( spentIsTime));
            self.output =+ out

        
        top.addToExtra("SPENT-TIME-IS", float(spentIsTime));
        
        return top, out;    
    
    def CreateBucketsPerTestInstance(self,trainSet, testSet, vSets,name, testCut, iternum, save,clfName):
        """
        Planned: Per instance LSH traing set data.
        """
        pass
