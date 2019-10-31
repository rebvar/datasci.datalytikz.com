import random
from Lib import DPLIB
from Lib import Common
import numpy as np
from sklearn.model_selection import StratifiedKFold
from Lib import GLOB

class Benchmarks(object):         
    
    def WCFolds (testSet,folds,file,fout,name,clfName):
    
        auc = 0
        preds = []
        actuals = []
        vals = None
        tssCopy = testSet[:,:]
        rnd = random.Random(Common.getCurrentTimeMil());
        np.random.shuffle(tssCopy)

        skf = StratifiedKFold(n_splits=folds)        
        X = tssCopy[:,:-1]
        y = tssCopy[:,-1]
        for train_index, test_index in skf.split(X , y):

            cvtrain, cvtest = X[train_index], X[test_index]
            cvtrainY, cvtestY = y[train_index], y[test_index]

            cvtrain = np.append(cvtrain,cvtrainY.reshape((len(cvtrainY),1)), axis = 1)
        
            cvtest = np.append(cvtest,cvtestY.reshape((len(cvtestY),1)), axis = 1)

            if (name.lower().find("infogain")>=0):
                pass
                #int indi[] = DPLIB.fSelectInfoGain(cvtrain);
                #if (DPLIB.useIterativeInfoGainSubsetting)
                #{
                #    indi = DPLIB.iterativeInfoGainSubsetting(cvtrain, indi, clfName);
                #}
                #else
                #    indi = DPLIB.getTopX(indi);
                #cvtrain = DPLIB.fSelectSet(cvtrain, indi);
                #cvtest = DPLIB.fSelectSet(cvtest, indi);
            
            
            m = GLOB(clfName).getClassifier()
            m.buildClassifier(cvtrain)

            
            vec = m.evaluateModel(cvtest);
            
            preds.append(vec);
            actuals.append(cvtestY)
            if vals == None:
            
                vals = DPLIB.getConfMatrix(cvtestY,vec)
            
            else:
            
                v2 = DPLIB.getConfMatrix(cvtestY,vec)
                
                for key in vals.keys():
                    vals[key] += v2[key]                                   
        
        auc = DPLIB.getAUCCV(actuals,preds)
        vals1 = DPLIB.getMeasures(vals)
        print(name+":" + file + ": "+ str(vals1) + " AUC = "+str(auc))                        
        fout.write("\n"+name+":" + file + ": " + " AUC = " + str(auc) + ";" + "Vals=" + str(vals1));
        
    
    
    def Basic(trainSet, testSet,file, fout,name, vecin,clfName, isCount = False):
    
        auc = 0 
        l = GLOB(clfName).getClassifier()
        l.buildClassifier(trainSet)
            
        vec = l.evaluateModel(testSet)
        actual = testSet[:,-1]
        
        if isCount:
            
            vals = DPLIB.getMeasuresCount(actual,vec)
            print(name+":" + file + ": " + str(vals))
            fout.write("\n"+name+":" + file + ": " + "Vals=" + str(vals))

        else:
            tvals = DPLIB.getConfMatrix(actual,vec)        
            vals = DPLIB.getMeasures(tvals)
            auc = DPLIB.getAUC(actual,vec)
            print(name+":" + file + ": " + str(vals)+" AUC = "+str(auc))
            fout.write("\n"+name+":" + file + ": " + " AUC = " + str(auc) + ";" + "Vals=" + str(vals));                
    
    
            
            
    def LOC50(testSeti,file, fout,name, locIndex):    
        startTime = Common.getCurrentTimeMil();
        spentISTime = 0;
        tempTime = 0;
        spentISTime = Common.getCurrentTimeMil()
        allloc = testSeti[:,locIndex]               
                        
        med = np.median(allloc)
        predicted = [1 if t>=med else 0 for t in allloc]
        actual = testSeti[:,-1]
        tvals = DPLIB.getConfMatrix(actual,predicted)
        
        print("#CONF-TEST-"+name+":" + file + ": " + str(tvals))
                  
        fout.write("#CONF-TEST-"+name+":" + file + ": ")
        fout.write(str(tvals));fout.write("\n")
        
        vals = DPLIB.getMeasures(tvals)
          
        auc = DPLIB.getAUC(actual,predicted)
        print(name+":" + file + ": " + str(vals)+ " AUC = "+str(auc))
                        
        fout.write(name+":" + file + ": ");
        fout.write(str(vals));
        fout.write(" AUC = "); 
        fout.write(str(auc));fout.write("\n");
        
        time= Common.getCurrentTimeMil()-startTime       
        
        print("#TIME-FOR:"+name+":" + file + ": "+str( time));
        fout.write("#TIME-FOR:"+name+":" + file + ": "+str(time)+"\n");
            
        print("#TIME-FOR-IS:"+name+":" + file + ": "+str( time))
        fout.write("#TIME-FOR-IS:"+name+":" + file + ": "+str(time)+"\n");
                            
    
    def NNFilter (trainSeti,  testSet, file, fout,name, vecin, count, clfName, tunelrn, vSets, testCut):
    
        startTime = Common.getCurrentTimeMil()
        spentISTime = 0
        tempTime = 0
        
        bestFit = 0.0
        bestCount = 0
        btrainSet = None
        cfbf = DPLIB.DefaultCF
          
        if (count == 0):
            for i in range(1,11):
            
                tempTime = Common.getCurrentTimeMil();
                  
                trainSet = DPLIB.NNFilter(trainSeti, testSet, i);

                spentISTime+=Common.getCurrentTimeMil()-tempTime;
                  
                l = GLOB(clfName, tunelrn).getClassifier()
                                
                if (tunelrn):                
                    l = l.getTunedCLF(trainSet, vSets,fout,name, file)
                  
                l.buildClassifier(trainSet)
                  
                  
                avgFit = 0.0
                j = 0;
                for j in range(len(vSets)):
                
                    vec = l.evaluateModel(vSets[j])
                
                    tvals = DPLIB.getConfMatrix(vSets[j][:,-1],vec)
                    measures = DPLIB.getExtMeasures(tvals);
                    fit = measures["F"]*measures["GMean1"]
                    avgFit += fit

                
                  
                avgFit/=len(vSets)
                                  
                if (avgFit>bestFit):
                    bestFit = avgFit
                    bestCount = i
                    btrainSet = trainSet[:,:]
                                                                  
              
              
            
            if (testCut):
                  
                
                cf = 0
                j = 0
                                            
                trainSet = btrainSet;
                                  
                l = GLOB(clfName, tunelrn).getClassifier()
                
                if (tunelrn):                
                    l = l.getTunedCLF(trainSet, vSets,fout,name, file);                                        
                
                l.buildClassifier(trainSet)                  
                avgFit = 0.0
                
                for j in range(len(vSets)):
                
                
                    vec = l.evaluateModel(vSets[j])
                    vCF = 0.1 
                    bestCF = 0
                    bestCFVal = -1
                    bestVals = None
                        
                    while True:
                        tvals = DPLIB.getConfMatrix(vSets[j][:,-1], vec, vCF)
                        measures = DPLIB.getExtMeasures(tvals)
                        fit = measures["F"]*measures["GMean1"]
                        if (fit>bestCFVal or bestVals == None):                        
                            bestCFVal = fit
                            bestCF = vCF
                            bestVals = tvals
                         
                        vCF+=0.1
                        if vCF>=1:
                            break                        
                    cf+=bestCF                
                    
                    
                cf/=vSets.size()
                cfbf = cf                      
          
        trainSet = None
        if (count == 0):
            trainSet = btrainSet
        else:
            tempTime = Common.getCurrentTimeMil()
            trainSet = DPLIB.NNFilter(trainSeti, testSet, count)
            spentISTime = Common.getCurrentTimeMil() - tempTime
            bestCount = count
        

        l = GLOB(clfName, tunelrn).getClassifier()
        
        if (tunelrn):        
            l = l.getTunedCLF(trainSet, vSets,fout,name, file)

            print("#TUNE-LRN-PARAMS-"+name+":" + file + ": " + str(l.selectedParams))
            fout.write("#TUNE-LRN-PARAMS-"+name+":" + file + ": ")
            fout.write(str(l.selectedParams));fout.write("\n")  
            sCheck= l.getCLFOptions()

            print("#SETSET-LRN-PARAMS-"+name+":" + file + ": " + str(sCheck))
            fout.write("#SETSET-LRN-PARAMS-"+name+":" + file + ": ")
            fout.write(str(sCheck));fout.write("\n")
        
        
        l.buildClassifier(trainSet)

                  
        
        vec = l.evaluateModel(testSet)
        
        vecin = vec;
          
        tvals = DPLIB.getConfMatrix(testSet[:,-1],vecin,cfbf)
        if (count == 0):
        
            print("#BESTCOUNT-"+name+":" + file + ": "+str(bestCount))          
          
            fout.write("#BESTCOUNT-"+name+":" + file + ": ");
            fout.write(str(bestCount));fout.write("\n");
          
            print("#BESTFIT-"+name+":" + file + ": "+str(bestFit));
            fout.write("#BESTFIT-"+name+":" + file + ": ");
            fout.write(str(bestFit));fout.write("\n");
          
        
          
        print("#CONF-TEST-"+name+":" + file + ": "+str(tvals))          
        fout.write("#CONF-TEST-"+name+":" + file + ": ");
        fout.write(str(tvals));fout.write("\n")
        if (testCut):
        
            print("#NN-BEST-CF-VALUE:"+name+":" + file + ": "+str(cfbf))
                      
            fout.write("#NN-BEST-CF-VALUE:"+name+":" + file + ": ")
            fout.write(str(cfbf));fout.write("\n")
        
        vals = DPLIB.getMeasures(tvals)
        auc = DPLIB.getAUC(testSet[:,-1],vecin)
        print(name+":" + file + ": "+str(vals) + " AUC = "+ str(auc))      
          
          
        fout.write(name+":" + file + ": ");
        fout.write(str(vals));
        fout.write(" AUC = ");          
        fout.write(str(auc));fout.write("\n");
        
        time= Common.getCurrentTimeMil()-startTime
        
        print("#TIME-FOR:"+name+":" + file + ": "+str(time));
        fout.write("#TIME-FOR:"+name+":" + file + ": "+str(time)+"\n");
            
        print("#TIME-FOR-IS:"+name+":" + file + ": "+str(spentISTime))
        fout.write("#TIME-FOR-IS:"+name+":" + file + ": "+str(spentISTime)+"\n");
                  
        return vecin;
    
    
    def NNFilterMulti (trainSeti,  testSet, file, fout,name, vecin, count, clfName, tunelrn,vSets):
    
        startTime = Common.getCurrentTimeMil();
        
        
        trainSet = DPLIB.NNFilterMulti(trainSeti, testSet, count);
          
          
        l = GLOB(clfName,tunelrn).getClassifier()
        if (tunelrn):
        
            l = l.getTunedCLF(trainSet, vSets,fout,name, file);
              
            print("#TUNE-LRN-PARAMS-"+name+":" + file + ": "+ str(l.selectedParams))                
              
            fout.write("#TUNE-LRN-PARAMS-"+name+":" + file + ": ");
            fout.write(str(l.selectedParams));fout.write("\n");                
            sCheck= l.getCLFOptions();
                
            print("#SETSET-LRN-PARAMS-"+name+":" + file + ": " + str(sCheck));                
            
            fout.write("#SETSET-LRN-PARAMS-"+name+":" + file + ": ");                
            fout.write(str(sCheck));fout.write("\n");
                
              
        
        
        l.buildClassifier(trainSet)
        
        vec = l.evaluateModel(testSet)
        
        vecin = vec;
        
        tvals = DPLIB.getConfMatrix(testSet[:,-1],vecin)
          
        print("#CONF-TEST-"+name+":" + file + ": "+str(tvals));
        
          
        fout.write("#CONF-TEST-"+name+":" + file + ": ");
        fout.write(str(tvals));fout.write("\n");
          
        auc = DPLIB.getAUC(testSet[:,-1],vec)
        vals = DPLIB.getMeasures(tvals)
          
        print(name+":" + file + ": "+ str(vals)+" AUC = "+str(auc))
        

        fout.write(name+":" + file + ": ");
        fout.write(str(vals));
        fout.write(" AUC = ");          
        fout.write(str(auc));fout.write("\n");
                    
        time= Common.getCurrentTimeMil()-startTime;
                
        print("#TIME-FOR:"+name+":" + file + ": "+str(time));
        fout.write("#TIME-FOR:"+name+":" + file + ": "+str(time)+"\n");        

        return vecin;
    
    
    
    
    def WMulti (files, file, testSet, fout,features,name, clfName, dp, convertToBinary = True):
        
        train = []
        for file2 in files:
            if (file2[0:3]==file[0:3] and file2<file<0):
                train.append(file2)
         
        
          
        if (len(train)):            
            trainSet = DPLIB.LoadCSV(train, dp, features,convertToBinary)
                        
            if (name.lower().find("infogain")>=0):            
                #int indi[] = DPLIB.fSelectInfoGain(trainSet);
                #if (DPLIB.useIterativeInfoGainSubsetting)
                #{
                #    indi = DPLIB.iterativeInfoGainSubsetting(trainSet, indi,clfName);
                #}
                #else
                #    indi = DPLIB.getTopX(indi);
                #trainSet = DPLIB.fSelectSet(trainSet, indi);
                #testSet = DPLIB.fSelectSet(testSet, indi);
                pass
            
            
            l = GLOB(clfName).getClassifier()
            l.buildClassifier(trainSet)            
            vec = l.evaluateModel(testSet)
            
            tvals = DPLIB.getConfMatrix(testSet[:,-1],vec)
            auc = DPLIB.getAUC(testSet[:,-1],vec)
            vals = DPLIB.getMeasures(tvals)
            print(name+":" + file + ": "+ str(vals)+" AUC = "+str(auc))

            fout.write("\n"+name+":" + file + ": " + " AUC = " + str(auc) + ";" + "Vals=" + str(vals));
 
        
        else:
        
            print(name+":" + file + ": "+"!!!"+   " AUC = !!!")
            fout.write("\n"+name+":" + file + ": !!!")



