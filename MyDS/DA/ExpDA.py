import json
import os
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from Lib import Security
import config

class ExpDA:
    """description of class"""
    
    def getExpHash(exp):
        return Security.GenerateMD5(exp.results)

    def generateViolinPlots(exp, forceCreate = False):
        md5Name = ExpDA.getExpHash(exp)
        
        rd = json.loads(exp.results)
        methods = sorted(list(rd.keys()))

        
        compPath = config.plotsPath+md5Name+'/'
        if os.path.exists(compPath+'done.confirm') and not forceCreate:
            return md5Name
        

        mesMtdData = {}
        perDsMtdData = {}
        
        measures = None

        datasets = None

        PerMeasureMethods = {}

        for method in methods:
            mesMtdData = {}
            if datasets == None:
                datasets = sorted(list(rd[method].keys()))
            
            if measures == None:
                measures = sorted(list(rd[method][datasets[0]]['measures'].keys()))
                
            for m in measures:
                mesMtdData[m] = []
                if m not in PerMeasureMethods:
                    PerMeasureMethods[m] = {}
                    PerMeasureMethods[m][method] = []
            for m in measures:
                for ds in datasets:
                    mesMtdData[m]+=rd[method][ds]['measures'][m]
                    PerMeasureMethods[m][method]+=rd[method][ds]['measures'][m]

            
            fig,ax = plt.subplots(ncols = 1,nrows = 1,figsize=(10,3))
            fig.tight_layout()     
            ax.set_ylim([0, 1])
            ax.set_xlim([0,len(mesMtdData.keys())+1])
            ax.set_xticks([i+1 for i  in range(len(mesMtdData.keys()))])

            ax.set_title("Measures for Method: "+method)
        
            skeys = sorted(mesMtdData.keys(), key=lambda k: np.median(mesMtdData[k]))
            pos = 1
            for lbl in skeys:
                ax.text(pos-0.5, 0.3+len(lbl)/70, lbl, rotation=90) 
                pos+=1
    
            #ax.set_xticklabels(lbls)        
            prt=ax.violinplot([mesMtdData[m] for m in skeys],showmeans=True,showmedians = True)
            prt['cmeans'].set_facecolor('black')
            prt['cmeans'].set_edgecolor('black')
            prt['cmeans'].set_linestyle('--')
            prt['cmeans'].set_linewidth(3)
        
            if not os.path.exists(compPath):
                os.makedirs(compPath)

            fig.savefig(compPath+'MethodMeasure_'+method+'.svg', format='svg')
            #fig.savefig(picPath+'1'+names[field]+'.jpg', format='jpg', dpi=100)
            #plt.cla()
            #plt.clf()
            fig.clf()
            ax.cla()
            plt.close('all')
            fig = None
            ax = None




        #Make it better, not good.
        #for m in measures:
        #    for ds in datasets:
        #        fig,ax = plt.subplots(ncols = 1,nrows = 1,figsize=(10,3))
        #        fig.tight_layout()     
        #        ax.set_ylim([0, 1])
        #        ax.set_xlim([0,len(methods)+1])
        #        ax.set_xticks([i+1 for i  in range(len(methods))])

        #        skeys = sorted(methods, key=lambda k: np.median(rd[k][ds]['measures'][m]))
        #        pos = 1
        #        for lbl in skeys:
        #            ax.text(pos-0.5, 0.3+len(lbl)/70, lbl, rotation=90) 
        #            pos+=1
    
        #        #ax.set_xticklabels(lbls)        
        #        prt=ax.violinplot([rd[sk][ds]['measures'][m] for sk in skeys],showmeans=True,showmedians = True)
        #        prt['cmeans'].set_facecolor('black')
        #        prt['cmeans'].set_edgecolor('black')
        #        prt['cmeans'].set_linestyle('--')
        #        prt['cmeans'].set_linewidth(3)
        
            
        #        if not os.path.exists(compPath):
        #            os.makedirs(compPath)
        #        ax.set_title(m+ ' performance for method(s) on '+ds+' dataset')
        #        fig.savefig(compPath+'MeasureDS_'+str(measures.index(m))+'-'+str(datasets.index(ds))+'.svg', format='svg')
        #        #fig.savefig(picPath+'1'+names[field]+'.jpg', format='jpg', dpi=100)
        #        #plt.cla()
        #        #plt.clf()
        #        fig.clf()
        #        ax.cla()
            
        #        plt.close('all')
        #        fig = None
        #        ax = None
        file = open(compPath+'done.confirm','w')
        file.close()

        return md5Name