from Lib import DPLIB 
from Lib import Common
import numpy as np
import os
from PyGIS import GIS
from PyGIS import GISKS2
from .CPDP_LSH import CPDP_LSH_Binary
import traceback
import random
from Lib import RejectedDatasetsTracker, DatasetUtils
from Lib import  ValidationType, ValidationSetManager

class myRunner:

    def __init__(self, train, test, files, file, savePath, dp, pars):

        self.dp = dp        
        self.features = pars['featuresList']
        self.iters = pars['iters']
        self.folds = pars['folds']
        self.file = file
        self.files=files
        self.vSetCount = pars['vSetCount']
        self.vSetMaxDSSize = pars['vSetMaxDSSize']
        self.lrnrs = [pars['lrnr']]
        self.savePath=savePath
        self.train = train
        self.test = test
        self.pars = pars
        self.isCount = pars.get('isCount',False)
        self.expType = pars['type']    
        if 'isKS' not in pars.keys():
            pars['isKS'] = False
        self.isKS = pars['isKS']
        self.gis = None
        self.lsh = None


    def doGIS(self,trainSet, testSet, vSets, clfName):
        
        #set thresholdManager's threshold value
        self.gis.fit(trainSet, testSet, vSets, self.pars['vSetType'], clfName)
        predictions = self.gis.predict(testSet, testLabels)
        return predictions

    def score(self, predictions, testLabels):

        if self.isCount:
            pass
        else:
            if testLabels != None:
                confs, measures = DPLIB.getConfAndExtMeasures(testLabels, predictions)
                return confs, measures
            return None

    
    def run(self):
        lrnrnames = self.lrnrs
        try:
            rnd = random.Random(Common.getCurrentTimeMil())            
            if self.expType == 'GIS':
                if self.isKS:
                    self.gis = GISKS2(self.pars,self.file)
                else:
                    self.gis = GIS(self.pars)
            elif self.expType == 'LSH':
                lsh = CPDP_LSH_Binary(self.pars, self.file)

            trainSetAll = DPLIB.LoadCSV(self.train, self.dp, self.features, convertToBinary = not self.isCount);
            testSetAll = DPLIB.LoadCSV(self.test, self.dp, self.features, convertToBinary = not self.isCount);  
            

            ft = 'A'
            indi = None

            if not self.isCount:

                if self.pars['features'] == 'Iterative InfoGain Subsetting':
                    ft = 'IG'
                    indi = DPLIB.fSelectInfoGain(trainSetAll);

            
            if self.pars['features'] == 'All':
                print ('All')

            if self.pars['features'] == 'PCA':
                ft = 'PCA'
                print ('PCA')
                trainSetAll, testSetAll = DPLIB.applyPCA(trainSetAll, testSetAll, 0.95)
                        
            for lk in range(len(lrnrnames)):                

                lrnr = "-" + lrnrnames[lk];

                clfName = lrnrnames[lk];

                vSets = None                                
                
                if not self.isCount:
                    if self.pars['features'] == 'Iterative InfoGain Subsetting':

                        indis2 = DPLIB.iterativeInfoGainSubsetting(trainSetAll, indi, clfName);
                        trainSetAll = DPLIB.fSelectSet(trainSetAll, indis2);
                        testSetAll = DPLIB.fSelectSet(testSetAll, indis2);
                
                if self.pars['vSetType'] in ['Single Random','Multiple Random']:
                    vSets = DatasetUtils.getRandomDatasets()
                c = 0
                while (c < self.iters):

                    print("Start:" + self.file + ": " + str(c));
                    print("====================================================");
                    #fout.write("#ITERINFO:For File=" +self.file + "-Iter:" + str(c) + "\n");

                    stages = None
                    buckets = None
                    sbtx = ""
                                                                    
                    if self.expType == 'GIS':
                        self.doGIS(trainSetAll, testSetAll, "FIXED-VMUL-GEN-"+ft, lrnr, fout, vSets, False, clfName, gis=gis);
                        gis.prnt('---------------------------------------\n')
                    
                        
                    elif self.expType == 'LSH':
                        lsh.CreateBucketsTune(trainSetAll, testSetAll, vSets, name= "LSHTune-ALL-TOP-SUPER" + sbtx + lrnr, testCut= self.pars['tunecut'], iternum=c, save=False, superbit=self.pars['lshType'] =='SuperBit', clfName=clfName,tunelrn = self.pars['tunelrnr']);
                        lsh.prnt('---------------------------------------\n')

                    c+=1
                    
            #fout.write("===================================================================\n");
            #fout.close();

            print("File Processing Ended:" +self.file);
        except Exception as e:

            try:
                print (str(e))
                print(traceback.format_exc())                
            except Exception as ex2:
                print("X2", str(ex2));
                print(traceback.format_exc())
                
        if self.expType == 'GIS':
            return gis
        elif self.expType == 'LSH':
            return lsh

        
class BCC:
    
    def toDict(lds):
        measures = None
        expNames = ('GIS','LSH','FIXED','VAR','VR','FX',)
        out = {}

        for line in DPLIB.doReplaces('\n'.join(['\n'.join(l) for l in lds])).split('\n'):
            line = line.strip()
            if line.startswith(expNames):
                parts = line.replace("': ","'=>").split(':')
                perf = parts[2].replace('{','').replace('}','').strip()
                method = parts[0]
                ds = parts[1]
                learner = method.split('-')[-1]
                apprName = method[:method.rfind('-')]
                featureSpace = apprName.split('-')[-1]
                vals = []
                measures = []
                for p in perf.split(','):
                    p = p.strip().split('=>')
                    p[0] = p[0].strip().replace("'","")
                    p[1] = p[1].strip()
                    if p[0] not in measures:
                        measures.append(p[0])
                        vals.append(float(p[1]))
                if method not in out.keys():
                    out[method] = {}
                if ds not in out[method].keys():
                    out[method][ds] = {}
                    out[method][ds]['measures'] = {}
                    out[method][ds]['confs'] = []
                for mindex, m in enumerate(measures):
                    if m not in out[method][ds]['measures'].keys():
                        out[method][ds]['measures'][m] = []
                    out[method][ds]['measures'][m].append(vals[mindex])
            elif line.startswith("#CONF-TEST:"):
                parts = line.replace("': ","'=>").split(':')[1:]
                perf = parts[2].replace('{','').replace('}','').strip()
                method = parts[0]
                ds = parts[1]
                learner = method.split('-')[-1]
                apprName = method[:method.rfind('-')]
                featureSpace = apprName.split('-')[-1]
                
                if method not in out.keys():
                    out[method] = {}
                if ds not in out[method].keys():
                    out[method][ds] = {}
                    out[method][ds]['measures'] = {}
                    out[method][ds]['confs'] = []
                out[method][ds]['confs'].append(perf)

        return out
                    
    def RunTests(uid, type, pars, basedir):                
        
        folds=10
        pars['folds'] = folds
        iters = pars['iters']
        #0 for ID
        features = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21]
        pars['featuresList'] = features

        dp = basedir+'/DataPacks/D5-Reg/'
        
        savePath = basedir+'/SavePath/'
        Path = savePath;
        
        PathFolder = Path
        if not os.path.exists(PathFolder):
            os.makedirs(PathFolder)
        datasets = pars['datasets']
        files = []
        for ds in datasets:
            if not ds.startswith('!'):
                continue
            fol, file = ds[1:].split(';')
            files.append('DataPacks/'+fol+'/'+file)
        #files = DPLIB.getFiles(dp);
        pars['files'] = files
        pars['tests'] = []
        pars['trains'] = []
        endTST = ''
        startTST = ''
        procs = []
        
        for file in files:
            if (len(endTST) > 0 and file>endTST):
                break
            
            if (file>startTST):
                train = []
                for file2 in files:
                    
                    if (file2!=file):
                        train.append(file2)                      
                test = []
                test.append(file)
                pars['tests'].append(file)
                pars['trains'].append(train)
                procs.append(myRunner(train, test, files, file, savePath,dp, pars));
                

        rets = []
        expModels = []
        #####Run the procs
        if len(procs)>0:
            for pr in procs:
                model = pr.run()
                rets.append(model.output)

                

                expModels.append(model)
                #think about yield
            print ('OK!!!')

            return BCC.toDict(rets), expModels
        else:
            print ('None')            
            return None, None
             