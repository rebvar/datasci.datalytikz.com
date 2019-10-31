
from flask import Blueprint, render_template, redirect, url_for, request, abort
from os import environ as env
from app import bcr, db, session
from models import User, Experiment, Dataset, DatasetGroup, ExperimentPrediction
import sys
import config
from CPDP import BCC
from Lib import Common
import multiprocessing as mp
import json
import Shared
import pickle
import os


BPExperiments = Blueprint('BPExperiments', __name__)


def RunWithPars(pars, uid):
    """
    docstring here
        :param pars: 
        :param uid: 
    """

    startTime =  Common.getCurrentTimeMil()
    
    modelsFol = 'SavePath/models/'
    if not os.path.exists(config.basedir+'/'+modelsFol):
        os.makedirs(config.basedir+'/'+modelsFol)
    fname = modelsFol+Common.gen_rnd_filename()+'.pkl'
    #ADD Field

    pars['pid'] = os.getpid()
    e = Experiment()
    e.endDateTime = "--RUNNING--"
    e.startDateTime = str(startTime)
    e.pars = json.dumps(pars)
    e.results = ""
    e.type = pars['type']
    e.expModelsFileName = ''    
    e.userId = uid

    db.session.add(e)
    db.session.commit()
    
    ret, expModels = BCC.BCC.RunTests(uid,pars['type'],pars, config.basedir)
    pickle.dump(expModels,open(config.basedir+'/'+fname,'wb'))
    if ret is None:
        e.delete()
        db.session.commit()
    else:
        endTime = Common.getCurrentTimeMil()                        
        e.endDateTime = str(endTime)
        e.startDateTime = str(startTime)
        e.pars = json.dumps(pars)
        e.expModelsFileName = fname
        e.results = json.dumps(ret) 
        db.session.commit()    
    

    for method in ret.keys():
        for ds in ret[method].keys():
            perfs = ret[method][ds]
        
            ep = ExperimentPrediction()
        
            ep.data = None
            ep.datasetName = ds
            ep.predResult = json.dumps(perfs)
            ep.expId = e.id
            ep.predDateTime = e.endDateTime
            ep.predType = 0    ###Test with known labels

            db.session.add(ep)
            db.session.commit()

@BPExperiments.route('/newgis',methods=['GET', 'POST'])
def newgis():    
    error = None
    ret = None
    lrnrs = ['Naive Bayes','Logistic Regresson','Decision Tree','Bayesian Network','Support Vector Machine','Random Forest Classifier','AdaBoost Classifier', 'Linear Regression']
    vSetType = ['Multiple Random','Single Random','NN-Filter','Training Set','KS2']
    features = ['All','Iterative InfoGain Subsetting', 'PCA']
    fols = os.listdir(config.basedir+'/DataPacks')
    DataPacks = {fol:os.listdir(config.basedir+'/DataPacks/' + fol) for fol in  fols}
    
    #return render_template('expr/dp/GISExpr.html', error=error, result = ret, lrnrs=lrnrs, vSetType = vSetType, features = features, fols = fols,DataPacks = DataPacks)

    #Create Data Details

    print ('Hey')   
    if Shared.isLoggedIn():
        

        if request.method == 'POST':
                       

            try:
                dsList = None
                if len(request.form['hdselect2'])>0:
                    dsList = json.loads(request.form['hdselect2'])
                    if (not isinstance(dsList,list)) or len(dsList)<=0:
                        raise Exception('No Dataset is selected')
                else:
                    raise Exception('No Dataset is selected')

                pars = {
                    'lrnr': request.form['lrnr'],
                    'vSetType': request.form['vSetType'],
                    'features': request.form['features'],
                    'iters' :max(1,min(int(request.form['iters']),100)),
                
                    'popSize': max(2,min(int(request.form['popSize']),1000)),
                    'numGens': max(2,min(int(request.form['numGens']),1000)),
                
                    'trainType' :request.form['trainType'],
                    'numParts' :max(1,min(int(request.form['numParts']),10)),
                    'sizeTop' :max(0,min(int(request.form['sizeTop']),10)),

                    'chrmSize': max(10,min(1000, int (request.form['chrmSize']))),
                    'vSetMaxDSSize': max(10,min(100, int (request.form['vSetMaxDSSize']))), 

                    'vSetCount':max(1,min(10, int (request.form['vSetCount']))),
                
                    'tunelrnr':'tunelrnr' in request.form,
                
                    'tunecut':'tunecut' in request.form,
                    'isKS':'isKS' in request.form,
                    'isCount': request.form['lrnr'] == 'Linear Regression',
                    'type' :'GIS',
                    'datasets': dsList,
                }

                if pars['vSetType'] == 'Single Random':
                    pars['vSetCount'] = 1

                print (pars)
                

            except Exception as e:
                error = str(e)
                print (error)
                return render_template('expr/dp/GISExpr.html', error=error, result = ret, lrnrs= lrnrs, vSetType = vSetType, features = features, fols = fols,DataPacks = DataPacks)

            try:
                
                uid = int(session['u'])

                #RunWithPars(pars,uid)
                
                p = mp.Process(target=RunWithPars, args=(pars,uid))
                p.start()            
                ret  = 'Please Check your Dashboard to Check the status of your experiments'
                error = None
            except Exception as ex:
                error = str(ex)
                ret = None
       
        return render_template('expr/dp/GISExpr.html', error=error, result = ret, lrnrs=lrnrs, vSetType = vSetType, features = features, fols = fols,DataPacks = DataPacks)
    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))




@BPExperiments.route('/newlsh',methods=['GET', 'POST'])
def newlsh():    
    error = None
    ret = None
    lrnrs = ['Naive Bayes','Logistic Regresson','Decision Tree','Bayesian Network','Support Vector Machine', 'Linear Regression']
    vSetType = ['Multiple Random','Single Random','NN-Filter','Training Set']
    features = ['All','Iterative InfoGain Subsetting', 'PCA']
    fols = os.listdir(config.basedir+'/DataPacks')
    DataPacks = {fol:os.listdir(config.basedir+'/DataPacks/' + fol) for fol in  fols}
    if Shared.isLoggedIn():
        

        if request.method == 'POST':

            try:

                dsList = None
                if len(request.form['hdselect2'])>0:
                    dsList = json.loads(request.form['hdselect2'])
                    if (not isinstance(dsList,list)) or len(dsList)<=0:
                        raise Exception('No Dataset is selected')
                else:
                    raise Exception('No Dataset is selected')

                pars = {
                    'lrnr': request.form['lrnr'],
                    'vSetType': request.form['vSetType'],
                    'features': request.form['features'],
                    'iters' :max(1,min(int(request.form['iters']),100)),         
                    'numOptions' :max(1,min(int(request.form['numOptions']),10)),
                    'maxBuckets': max(2,min(int(request.form['maxBuckets']),99)),
                    'minBuckets': max(2,min(int(request.form['minBuckets']),99)),
                    'maxStages': max(2,min(int(request.form['maxStages']),10)),
                    'minStages': max(2,min(int(request.form['minStages']),10)),
                    'vSetMaxDSSize': max(10,min(100, int (request.form['vSetMaxDSSize']))), 
                    'vSetCount':max(1,min(10, int (request.form['vSetCount']))),                
                    'tunelrnr':'tunelrnr' in request.form,                
                    'tunecut':'tunecut' in request.form,
                    'isCount': request.form['lrnr'] == 'Linear Regression',
                    'type': 'LSH',
                    'lshType': request.form['lshType'],
                    'datasets': dsList,
                }

                if pars['vSetType'] == 'Single Random':
                    pars['vSetCount'] = 1

                print (pars)
                

            except Exception as e:
                error = str(e)
                print (error)
                return render_template('expr/dp/LSHExpr.html', error=error, result = ret, lrnrs= lrnrs, vSetType = vSetType, features = features, fols=fols,DataPacks = DataPacks)

            try:
                
                uid = int(session['u'])

                #RunWithPars(pars,uid)


                p = mp.Process(target=RunWithPars, args=(pars,uid))
                p.start()            
                ret  = 'Please Check your Dashboard to Check the status of your experiments'
                error = None
            except Exception as ex:
                error = str(ex)
                ret = None
            
        return render_template('expr/dp/LSHExpr.html', error=error, result = ret, lrnrs=lrnrs, vSetType = vSetType, features = features, fols = fols ,DataPacks = DataPacks)
    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))


@BPExperiments.route('/init_dp_data',methods=['GET'])
def init_db_data():
    user = Shared.getLoggedInUser()
    if user is not None:
        if user.utype == 1:
            pass
        
    return abort(403)
