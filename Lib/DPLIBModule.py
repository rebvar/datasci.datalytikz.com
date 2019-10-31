
import numpy as np
import os
import math 
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_selection import mutual_info_classif
from sklearn.model_selection import StratifiedKFold
from .GLOBModule import GLOB

class DPLIB:

    replaces = [['END','\\\\\\hline']
            ,['-log','-LOG'],['-nb','-NB'],['-dt','-DT'],['-bn','-BN'],['-j48','-J48']
            ,['FIXED-','FX-'],['VAR-','VR-'],['LSHTune','LSH'],
            ['GEN','GIS'],['TNNFILTER-A','NNF'],['NNFILTER-A','NNF'],['.arff',''],['ALL-TOP-',''],            
            ['SUPER-',''],
            ['CLFTU-TUNE-v20-vmx250--','LRNTune-'], ['TUNE-v20-vmx250--','-'], ['TUNEDCLF','LRNTune'],['LRNTune-','Tuned'],
            ['NNF-10','NNF'],['--','-'], 
            ['FX-VNN-GIS','GIS(FX-VNN)'],['VR-VNN-GIS','GIS(VR-VNN)'],['VR-VMUL-GIS','GIS(VR-VMUL)'],['FX-VMUL-GIS','GIS(FX-VMUL)']
            ,['TunedNNF-0','NNF'],['TuneNNF-0','NNF'], ['LOC-50','LOC50']
           ]


    CONF_KEYS = ["tp", "tn", "fp", "fn"]

    MEASURES_BIN = {'F': lambda rec,prec: 2*(rec*prec)/(rec+prec) if rec+prec>0 else 0, 
                    'F2': lambda rec, prec: 5*rec*prec/(rec+4*prec) if (rec+4*prec)>0 else 0,
                    'F0.5': lambda rec, prec: 1.25*rec*prec/(rec+0.25*prec) if (rec+0.25*prec)>0 else 0,
                    'rec': lambda tp,tn,fp,fn: tp / (tp + fn) if (tp+fn)>0 else 0,
                    'prec' : lambda tp,tn,fp,fn: tp / (tp + fp) if (tp+fp)>0 else 0,
                    'accu': lambda tp,tn,fp,fn: (tp + tn) / (tp + fp + tn + fn) if (tp + fp + tn + fn)!=0 else 0,
                    'pf': lambda tp,tn,fp,fn:  fp/(fp+tn) if (fp+tn)!=0 else 0,
                    'bal': lambda rec, pf: 1-(math.sqrt(pf*pf+(1-rec)*(1-rec))/math.sqrt(2)),
                    'mcc': lambda tp,tn,fp,fn: (tp*tn-fp*fn)/math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn)) if math.sqrt((tp+fp)*(tp+fn)*(tn+fp)*(tn+fn))!=0 else 0,
                    'tnr': lambda tp,tn,fp,fn:  tn/(tn+fp) if (tn+fp)>0 else 0,
                    'fnr': lambda tp,tn,fp,fn:  fn/(fn+tp) if (fn+tp)>0 else 0,
                    "GMean1":lambda rec, prec: math.sqrt(rec*prec),
                    "GMean2": lambda rec, pf: math.sqrt(rec*(1-pf)), 
                    'auc':getAUCSet
        }


    DefaultCF = 0.5
    ep = 0.000000001

    def doReplaces(line):
        for r in DPLIB.replaces:
            line = line.replace(r[0],r[1])
        return line

    def readArff(name):
        lines = []
        o = open(name)
        relation = None
        dataFound = False
        id = 0
        while True:
            line = o.readline()
            if not relation:
                if line.lower().find('@relation')>=0:
                    relation = line.replace('\n','').split(' ')[1]
            if line == '':
                break
            line = line.replace('\n','')
            if line.strip().lower().startswith('@data'):
                dataFound = True
                continue

            if not dataFound:
                continue

            line = line.strip()

            if len(line)<5:
                continue

            if line.find(',')<0:
                continue
            
            line = [float(t) for t in line.split(',')]
            if len(line)>0:
                lines.append([relation+'-'+str(id)]+line)
                id+=1
        return np.array(lines,dtype = 'O')

    
    def getPartRange(partNumber, partSize, totalSize):
        start = partNumber * partSize
        end = (partNumber + 1) * partSize
        if (end > totalSize):
            end = totalSize;
        if (partSize >= totalSize):
            end = totalSize

        return start, end


    def checkSimilarity(data1,data2):
        from scipy.stats import ks_2samp
        smp = 0
        count = 0
        numFeats = data1.shape[1]
        p_vals = []
        for i in range(1, numFeats):
            col1 = data1[:,i]
            col2 = data2[:,i]
            s,p = ks_2samp (col1,col2)
            p_vals.append(p)
            smp+=p
            if p>0.05:
                count+=1
        #out = [count, count/data1.shape[1]]
        #return out
        if count!=numFeats-1:
            return (smp/(numFeats-1-count)) , p_vals
        return smp, p_vals


    def LoadCSVFile(file, dp, ft):

        files = [file]        
        return DPLIB.LoadCSV(files, dp, ft)
    

    def LoadCSV(files, dp, ft, convertToBinary = True):
        dp = ''
        id = 0
        try:
            ft = sorted(ft);

            f = files[0];
            
            insts = DPLIB.readArff(dp+f)
            
            
            
            numAttrs = insts.shape[1]
    
    
            for f2 in files[1:]:
                f1 = f2.strip()
                insts2 = DPLIB.readArff(dp+f1)
                
                num = len(insts2)
                
                insts = np.append(insts,insts2, axis = 0)

                #Find a way to set the ID.
            

            for i in range(numAttrs - 1 - 1): #
                attrInd = numAttrs - 1 - 1 - i

                if attrInd not in ft:
                    insts = np.delete(insts,attrInd,1)    
    
            numAttrs = len(ft)+1

            num = len(insts)
    
            #insts = insts.real
                
            if convertToBinary:

                for i in range(num):
                    if insts[i,numAttrs - 1] > 0:
                        insts[i,numAttrs - 1] = 1
                        #Set Extra to 1    
                    else:
                        insts[i,numAttrs - 1] = 0
                        #Set Extra to 0    
            else:
                pass
                #for i in range(num):
                    #Set Extra to number of bugs
                #    pass                                    
            return insts;       
        except Exception as ex:            
            print (ex)
            input()



    def applyPCA(trainSet,testSet, variance = 0.95):
        pca = PCA(variance)
        pca.fit(trainSet[:,1:-1])
        
        train_pca = pca.transform(trainSet[:,1:-1])
        test_pca = pca.transform(testSet[:,1:-1])

        train_pca = np.append(train_pca,trainSet[:,-1].reshape((len(trainSet),1)),axis = 1)
        #ID
        train_pca = np.insert(train_pca,0,trainSet[:,0],axis = 1)
        test_pca = np.append(test_pca,testSet[:,-1].reshape((len(testSet),1)),axis = 1)
        #ID
        test_pca = np.insert(test_pca,0,testSet[:,0],axis = 1)
        return train_pca,test_pca


    def MAD(numbers):    
        med = np.median(numbers)        
        return np.median([abs(med - num) for num in numbers])


    def getConfMatrix(actuals, predictions, cf=0.5, targetClass = 1):
        tp = 0.0
        fp = 0.0
        tn = 0.0
        fn = 0.0

        iscflist = isinstance(cf,list)        
        cfi = 0.5
        for p in range(len(actuals)):

            act = actuals[p]
            pred = predictions[p]
            
            if iscflist:
                cfi = cf[i]
            else:
                cfi = cf

            actInt = 1-targetClass
            if (act >= cfi): 
                act = targetClass
                actInt = targetClass
            else:
                act = 1-targetClass
                actInt = 1-targetClass
            

            predInt = 1-targetClass
            if (pred >= cfi):
                pred = targetClass
                predInt = targetClass
            else:
                pred = 1-targetClass
                predInt = 1-targetClass
            

            if (actInt == 1-targetClass and predInt == 1-targetClass):
                tn += 1
            elif (actInt == targetClass and predInt == targetClass):
                tp += 1
            elif (actInt == 1-targetClass and predInt == targetClass):
                fp += 1
            elif (actInt == targetClass and predInt == 1-targetClass):
                fn += 1

        return {"tp":tp, "tn":tn, "fp":fp, "fn":fn}



    def getConfMatrixSet(actuals,predictionsSet,cf = 0.5, targetClass = 1):
        
        if len(predictionsSet)==1:
            return DPLIB.getConfMatrix(actuals,predictionsSet[0],cf)

        num = len(actuals)
        
        predictions = []

        cnt = len(predictionsSet)

        for i in range(num):        
            predictions.append(np.sum([predictionsSet[k][i] for k in range(cnt)])/cnt)
            
        return DPLIB.getConfMatrix(actuals,predictions,cf, targetClass)


    def getFiles(path,ext = '.arff'):
        return [path + file for file in os.listdir(path) if file.endswith(ext)]



    def getMeasuresCount(actual, preds):
        
        
        aae = 0
        are = 0
        prec = 0
        prec0 = 0
        prec1 = 0
        precp = 0
        count0 = 0
        count1 = 0
        rmse = 0
        for p in range(len(actual)):

            act = actual[p]
            predicted = preds[p]

            actInt = int(act)
            predictedInt = int(predicted+0.5)

            if (actInt == predictedInt):
                prec+=1
                if (actInt == 0):
                    prec0+=1
                else:
                    prec1+=1
                
            

            if (actInt == 0):
                count0+=1
            else:
                count1+=1
            

            
            aae+=abs(predicted - act)
            are+=abs(predicted-act)/(act+1)
            
            if (actInt > 0 and predictedInt > 0):
                precp+=1
            

            rmse += (actInt - predictedInt) * (actInt - predictedInt)

        

        aae=aae/len(actual)
        are=are/len(actual)
        
        prec = prec / len(actual)
        rmse = math.sqrt(rmse / len(actual))
        vals = {"prec": prec, "rmse": rmse,
                "prec0/cnt0":prec0/count0,
                "prec1/cnt1": prec1/count1,
                "precp/cnt1": precp/count1,
                "aae": aae,"are": are
                }
        
        return vals
    
        

    def getMeasuresCountSet(actuals, predss):
        
        
        countAll = 0
        aae = 0
        are = 0
        prec = 0
        prec0 = 0
        prec1 = 0
        precp = 0
        count0 = 0
        count1 = 0
        rmse = 0


        for i in range(len(actuals)):
            actual = actuals[i]
            preds = predss[i]

            countAll += len(actual);
            

            for p in range(len(actual)):

                act = actual[p]
                predicted = preds[p]

                actInt = int(act)
                predictedInt = int(predicted+0.5)

                if (actInt == predictedInt):
                    prec+=1
                    if (actInt == 0):
                        prec0+=1
                    else:
                        prec1+=1
                
            

                if (actInt == 0):
                    count0+=1
                else:
                    count1+=1
        
                if (actInt > 0 and predictedInt > 0):
                    precp+=1
            

                aae+=abs(predicted - act)
                are+=abs(predicted-act)/(act+1)
                        
                
                rmse += (actInt - predictedInt) * (actInt - predictedInt);

            
        
        aae = aae/countAll;
        are = are/countAll;
        
        prec = prec / countAll;
        rmse = math.sqrt(rmse / countAll);


        vals = {"prec": prec, "rmse": rmse,
                "prec0/cnt0":prec0/count0,
                "prec1/cnt1": prec1/count1,
                "precp/cnt1": precp/count1,
                "aae": aae,"are": are
                }
        
        return vals
    
        



    def SaveToCsv(instances, name):   
        
        name2 = "D:/GISOUT/FILE-DS--File=[" + name + "].txt"
        
        fout = open(name2, 'w')
        
        for i in range(len(instances)):
        
            out = ','.join(['%.4f'%t for t in list(instances[i])])+'\n'            
            fout.write(out)        
        
        fout.close()
        return True
    



    def tied_rank(p):

        x = [pi for pi in p]
        orders = [i for i in range(len(p))]
        
        for i in range(len(x)):
            for j in range(i + 1, len(x)):
                if (x[i] > x[j]):
                    x[i], x[j] = x[j],x[i]
                    orders[i], orders[j] = orders[j], orders[i]                    

        r = [0 for _ in range(len(x))]
        
        cur_val = x[0]
        last_rank = 0;
        for i in range(len(x)):
            if (cur_val != x[i]):
                cur_val = x[i]
                for j in range(last_rank, i):
                    r[orders[j]] = float(last_rank + 1 + i) / 2.0;
                
                last_rank = i;
            
            if (i == len(x)- 1):
                for j in range(last_rank, i + 1):
                    r[orders[j]] = float(last_rank + 2 + i) / 2.0;
                
            
        
        return r;
    

    def getAUC(actuals, predictions):

        r = DPLIB.tied_rank(predictions)
        P = 0.0
        N = 0.0
        for i in range(len(actuals)):
            if int(actuals[i]) == 1:
                P += 1
            else:
                N += 1
        sumPos = 0;
        for i in range(len(actuals)):
            if int(actuals[i])==1:
                sumPos += r[i]
            
        
        if (N * P == 0):
            #print ('Class is only 0 or only 1')                       
            return 0
        
        auc = ((sumPos - P * (P + 1) / 2.0) / (N * P));
        return auc
    



    
    def getAUCCV(actualss, predictionss):
        actuals = []
        predictions = []
        for i in range(len(actualss)):
            actuals+=actualss[i]
            predictions+=predictionss[i]
        return DPLIB.getAUC(actuals,predictions)

        
   
    def getAUCSet(actuals, predictions):
        if isinstance(actuals[0], list):
            actuals = [item for sublist in actuals for item in sublist]
        if isinstance(predictions[0], list):
            predictions = [item for sublist in predictions for item in sublist]
        return DPLIB.getAUC(actuals,predictions)

    def Instance2Str (inst):
        return ','.join(['%.4f'%t for t in list(inst[i])])+'\n'
    
    def Combine(allds, inds):
        ret = np.copy(allds[inds[0]])
        for ind in inds[1:]:
            ret = np.append(ret, allds[ind], axis = 0)        
        return ret
    
    def SortPopulation(hmm):        
        newlist = sorted(hmm, key=lambda x: x.getFitness(), reverse=True)     
        return newlist

    
    def CombinePops(hmm, newHMM):
        i = 0
        j = 0
        ret = []
        rdel = []
        while (len(ret) < len(hmm)):
            if (hmm[i].getFitness() >= newHMM[j].getFitness()):
                ret.append(hmm[i])
                i += 1
            else:
                ret.append(newHMM[j])
                j += 1
            
        
        rdel = []
        
        return ret,rdel;    
    

    def getConfMatrixAndExtMeasures(actuals, predictions, cf=0.5):

        if actuals is None:
            return None, None
        if isinstance(predictions[0], list):
            conf0 = DPLIB.getConfMatrixSet(actuals,predictions,cf, targetClass = 0)
            conf1 = DPLIB.getConfMatrixSet(actuals,predictions,cf, targetClass = 1)
        else:
            conf0 = DPLIB.getConfMatrix(actuals,predictions,cf, targetClass = 0)
            conf1 = DPLIB.getConfMatrix(actuals,predictions,cf, targetClass = 1)
        measures0 = DPLIB.getExtMeasures(conf0)
        measures1 = DPLIB.getExtMeasures(conf1)
        
        ### Not sure
        measures0['auc'] = MEASURES_BIN['auc'](actuals, predictions)
        measures1['auc'] = MEASURES_BIN['auc'](actuals, predictions)
        return {'conf0':conf0, 'conf1':conf1, 'measures0':measures0, 'measures1':measures1}

    def getExtMeasures(vals):
        measures = {}
        tp, tn, fp, fn = vals["tp"], vals["tn"], vals["fp"], vals["fn"]

        for m in ['rec','prec','tnr', 'fnr', 'pf','accu','mcc']:
            measures[m]= MEASURES_BIN[m](tp,tn,fp,fn)
        rec, prec =  measures['rec'], measures['prec']
        for m in ['F','F0.5','F2','GMean1']:
            measures[m]= MEASURES_BIN[m](rec,prec)
        fp = measures['fp']
        for m in ['bal','GMean2']:
            measures[m]= MEASURES_BIN[m](rec,fp)

        return measures
    
    
    def getMeasures(vals):
        return DPLIB.getExtMeasures(vals)
    
    

    def getActuals(ds):                
        return ds[:,-1]
    

    def MinMaxNormalize(dsin):
        ds = np.copy(dsin)
        numAttrs = len(ds[0,:])
        cnt = len(ds)
        for i in range(1,numAttrs):
            mn = np.min(ds[:,i])
            mx = np.max(ds[:,i])
            
            diff = max - min;
            if (diff == 0):
                continue
            
            for j in range(cnt):
                ds[j,i] = (ds[j,i] - min) / diff
        
        return ds;       



    def attMean(ds, attIndex):
        return sum([ds[i, attindex] for i in range(len(ds))])/len(ds);              


    def Cluster(insts):        
        #for example xmeans
        raise NotImplementedError()
    

    def getLargestClusterKey(m):        
        raise NotImplementedError()
    

    def getLargestCluster(m):
        raise NotImplementedError()

    def SMOTE_OverSample(inp, per):
        raise NotImplementedError()
        


    def NNFilterAndRandom():
        raise NotImplementedError()

    def RangeFilter():
        raise NotImplementedError()



    def FindInstance(ins, st):

        numAttrs = len(ins)

        for i in range(len(st)):
            eq = True;
            for j in range(1,numAttrs):
                if ins[j] != st[i,j]:
                    eq = False
                    break                            
            if (eq):
                return st.instance(i)                    
        return null
    

    def FindInstanceIndex(ins, st, numAttrs = -1):
        
        if numAttrs == -1:
            numAttrs = len(ins)

        for i in range(len(st)):
            eq = True;
            for j in range(1,numAttrs):        
                if ins[j] != st[i,j]:
                    eq = False
                    break                            
            if (eq):
                return i                    
        
        return -1;
    

    def FindInstanceIndexNoLabel(ins, st):
        numAttrs = len(ins)-1

        return DPLIB.FindInstanceIndex(ins,st,numAttrs)

    
    def FindAllSimilarInstancesIndexes(index,st):
        
        
        indexSet = set()
        ins = st[index,:]
                 
        numInsts = len(st)   
        numAttrs = len(ins)-1
        
        for i in range(numInsts):
            if (i == index):
                indexSet.add(i)
                continue
            
            eq = True;
            for j in range(1,numAttrs):
                if (ins[j] != st[i,j]):
                    eq = False
                    break

                
            
            if (eq):
                indexSet.add(i)
            
        
        return indexSet;
    

    def getDSClass1Count(ds):
        
        return len([d for d in ds[:,-1] if d>0])
    
    def getDSClass0Count(ds):
        
        return len([d for d in ds[:,-1] if d<=0])
    
    def getallDistChars(numbers):
        raise NotImplementedError()

    def getStats(st, extIDS, extExts, extChrs):
        
        raise NotImplementedError()

        retVal = ""

        numAttrs = st.shape[1]
        numRows = len(st)
        res = None
        if (extChrs):
            
            res = []
            tres=None;
            for i in range(numAttrs):
                numbers = st[:,i]
                
                tres = DPLIB.getallDistChars(numbers)
                
                res+=tres
                tres = None
            

            retVal += "DstChr=[" + ','.join(res)+ "];;"
            
            numbers = None
            res = None
            tres = None
            
        
        classCounts = [getDSClass0Count(), getDSClass1Count()]
                
        
        retVal += "ClsCnt=[" + str(classCounts)+"]"

        ids=[]
        if (extIDS):
            pass
            #
            #for (int i = 0; i < set.numInstances(); i+=1) {
            #    ids[i] = set.instance(i).GetID();
            #}
        

        exts = []
        if (extExts):
            pass




    def fSelectSet(s, indices):
        
        nS = s[:,:]
        i = nS.shape[1]-2
        while i >= 1:
            if not i in indices:
                nS = np.delete(nS,i,1)
            i-=1        
        return nS


    def fSelectInfoGain(train):

        x = mutual_info_classif(train[:,1:-1], train[:,-1].astype(int), discrete_features=True)
        inds = np.argsort(x)
        inds = inds[::-1]
        inds = [i+1 for i in inds]
        return inds


    def iterativeInfoGainSubsetting(trainSet, ranks, clfName):
        
        folds = 10;
        f = 0;
        
        count = 2;


        tranks = []
        while (count < len(ranks)):
            vals = None

            skf = StratifiedKFold(n_splits=folds)
            X = trainSet[:,:-1]
            y = trainSet[:,-1]
            j = 0
            tranks = ranks[:count+1]

            for train_index, test_index in skf.split(X , y.astype(int)):

                cvtrain, cvtest = X[train_index], X[test_index]
                cvtrainY, cvtestY = y[train_index], y[test_index]

                cvtrain = np.append(cvtrain,cvtrainY.reshape((len(cvtrainY),1)), axis = 1)        
                cvtest = np.append(cvtest,cvtestY.reshape((len(cvtestY),1)), axis = 1)

                trCV = DPLIB.fSelectSet(cvtrain, tranks)
                tsCV = DPLIB.fSelectSet(cvtest, tranks)

                l = GLOB(clfName).getClassifier()
                l.buildClassifier(trCV)

                vec = l.evaluateModel(tsCV)

                if (vals == None):
                    vals = DPLIB.getConfMatrix(tsCV[:,-1],vec)
                else:
                    v2 = DPLIB.getConfMatrix(tsCV[:,-1],vec);
                    for k in v2:
                        vals[k] += v2[k]

            
            vals2 = DPLIB.getMeasures(vals)
            if (f < vals2["F"]):
                f = vals2["F"]
                count+=1
            else:
                break
        return tranks




    
    def NNFilter(train, test, count):
          
        trainCopy = train[:,1:-1]
        testCopy = test[:,1:-1]                
        
        out = []
                
        knn = NearestNeighbors(count, metric = 'euclidean')
        knn.fit(trainCopy)
        distances, indices = knn.kneighbors(testCopy)

        instSet = set()
        for row in indices:
            for ind in row:
                if ind in instSet:
                    continue
                out.append(train[ind])
                instSet.add(ind)
        return np.array(out)

    def NNFilterMulti(train, test, count):
                            

        metrics = ['chebyshev','euclidean','minkowski']

        trainCopy = train[:,1:-1]
        testCopy = test[:,1:-1]                
        


        out = []
        instSet = set()

        for m in metrics:                
            knn = NearestNeighbors(count,metric=m)        
            knn.fit(trainCopy)
            distances, indices = knn.kneighbors(testCopy)

            
            for row in indices:
                for ind in row:
                    if ind in instSet:
                        continue
                    out.append(train[ind])
                    instSet.add(ind)
        return np.array(out)
