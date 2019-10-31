from flask import Blueprint, render_template, redirect, url_for, request, abort
from os import environ as env
#from app import app, db
#from flask_sqlalchemy import SQLAlchemy as sa
from app import bcr, db, session
from models import User, Experiment, Dataset, DatasetGroup, ExperimentPrediction, Repo, Log, RepoFile, BugPattern, BugFix, RevisionData, SZZBlame
import sys
import config
from Lib import Common
import multiprocessing as mp
import json
import Shared
import pickle
import os
from dulwich import porcelain
from PySZZ import GIT
from PySZZ.Helpers import Helpers
from PySZZ.AnnotGraph import GraphBuilder
from PySZZ.SZZBlame import Blame2

BPSZZ = Blueprint('BPSZZ', __name__)


def RunWithPars(pars, uid):
    startTime =  Common.getCurrentTimeMil()    
    reposFol = 'SavePath/Repos/'
    if not os.path.exists(config.basedir+'/'+reposFol):
        os.makedirs(config.basedir+'/'+reposFol)
    fname = reposFol+Common.gen_rnd_filename()
    os.makedirs(config.basedir+'/'+fname)
    ##ADD Field
    e = Repo()
    e.cloneFinishDate = "--RUNNING--"
    e.cloneStartDate = str(startTime)
    e.repoInfo = ''
    e.isPrivate = int(pars['isPrivate'])
    e.path = fname
    e.repoName = pars['repoName']
    e.url = pars['url']
    e.userId = uid
    db.session.add(e)
    db.session.commit()
    
    try:
        porcelain.clone(pars['url'], config.basedir+'/'+fname)
        endTime = Common.getCurrentTimeMil()                        
        e.cloneFinishDate = str(endTime)    
        db.session.commit()

    except Exception as ex:
        print(ex)
        e.delete()
        db.session.commit()



def ExtractLogs(repo):        
    
    id = repo.id

    g = GIT.G(repo.path)
    logs = g.getAllLogsMy(dolower = True,toText= True)
    rex = Helpers.reexclude
    reb = Helpers.rebugs
    logs , out = Helpers.GetBC(logs, rex, reb)
    i = 0
    
    bugPT = json.dumps([rex,reb])
    
    bp = BugPattern.query.filter_by(patternList = bugPT)
    if bp.count()<=0:    
        bp = BugPattern()
        bp.patternList = bugPT
        db.session.add(bp)
        db.session.commit()
    else:
        if len(bp.count)>1:
            raise Exception('Duplicate bug pattern')
        bp = bp.first()

    oldlogs = Log.query.filter(Log.repoId==id).delete()
    db.session.commit()        
    logfiles = {}
    logfilesauth = {}
    for log in logs:
        if isinstance(log, dict):
            dblog = Log()
            dblog.author = log['author']
            dblog.branches = log['branches']
            dblog.cid = log['cid']
            dblog.date = log['date']
            dblog.files = json.dumps(log['files'])
            dblog.m = log['m']
            dblog.parents = json.dumps(log['parents'])
            dblog.pushdateTimestamp = log['commit_time']
            dblog.repoId = repo.id
            dblog.tags = log['tags']
            dblog.revIndex = i
            dblog.timestamp = log['commit_time']
            dblog.bugs = log['bugs']

            

            for file in log['files']:
                if file not in logfiles.keys():
                    logfiles[file] = [log['cid']]
                    logfilesauth[file] = [log['author']]
                else:
                    logfiles[file].append(log['cid'])
                    logfilesauth[file].append(log['author'])
            db.session.add(dblog)
            db.session.commit()


            if len(dblog.bugs)>0:
                bfix = BugFix()
                bfix.bugPatternId = bp.id
                bfix.isBugFix = 1
                bfix.logId = dblog.id
                bfix.bugs = dblog.bugs
                db.session.add(bfix)
                db.session.commit()
            i+=1
                                
    for file in logfiles:
        repofile = RepoFile()
        repofile.file = file
        repofile.authors = json.dumps(logfilesauth[file])
        repofile.revs = json.dumps(logfiles[file])
        repofile.repoId = id
        db.session.add(repofile)
        db.session.commit()
        logfiles[file] = None
        logfilesauth[file] = None        
    message = 'Logs Generated'
    return logs
    

@BPSZZ.route('/repoinfo/<id>',methods=['GET'])
def repoinfo(id):
    if Shared.isLoggedIn():
        repo = Repo.query.filter_by(id=id).first()
        g = GIT.G(repo.path)
        return render_template('expr/szz/repoinfo.html', repo=repo, g=g)

    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))


def RunSZZForRepo(repo, exts = None):
    id = repo.id
    if exts is None:
        exts = Helpers.currentExts
    if isinstance(exts, list):
        exts = tuple(exts)
    
    bc = Log.query.filter_by(repoId = repo.id)

    if bc.count()<=0:
        ExtractLogs(repo)
        bc = Log.query.filter_by(repoId = repo.id)
    if bc.count()>0:
        bc = bc.filter(Log.bugs!='')
        if bc.count()<=0:
            raise Exception('No Bug Fixes based on the current Bug patterns and exclusions')
    else:
        raise Exception('No Extracted Logs')
    
    files = set()
    for b in bc:
        bf = json.loads(b.files)
        for f in bf:
            files.add(f)
    repoFiles = repo.repoFiles.filter(RepoFile.file.in_(files))

    #repoFileIds = set()
    #for rf in repoFiles:
    #    repoFileIds.add(rf.id)
    
    revIds = set()
    for repoFile in repoFiles:
        revs = json.loads(repoFile.revs)
        for rev in revs:
            revIds.add(rev)
    graphs = RevisionData.query.filter_by(repoId = repo.id)
    if graphs.count()<=0:
        GenGraphs(repo,exts)
        graphs = RevisionData.query.filter_by(repoId = repo.id)    

    if graphs.count()>0:
        graphs = graphs.filter(RevisionData.rev.in_(revIds))
    else:
        raise Exception('No Graphs')
    #repoFiles = set([g.RepoFile for g in graphs])
    
    fileIDs = {}
    for file in repoFiles:
        fileIDs[file.file] = file.id
    
    returnVals = []
    for b in Blame2(bc,0,None,None,['+','*'],['+','*'],True,fileIDs,Helpers.currentExts, graphs):
        returnVals.append(b)
    

    bl = SZZBlame()
    bl.repoId = repo.id
    bl.blames = json.dumps(returnVals)
    db.session.add(bl)
    db.session.commit()


@BPSZZ.route('/runszz/<id>',methods=['GET', 'POST'])
def runszz(id):
    message=None

    if Shared.isLoggedIn():
        repo = Repo.query.filter_by(id=id).first()

        p = mp.Process(target=RunSZZForRepo, args=(repo,))
        p.start()            
        

        #RunSZZForRepo(repo)
        message = 'SZZ Started.'
        return render_template('expr/szz/repoinfo.html', repo=repo, message = message)

    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))

@BPSZZ.route('/extlogs/<id>',methods=['GET', 'POST'])
def extlogs(id):
    if Shared.isLoggedIn():
        repo = Repo.query.filter_by(id=id).first()

        #ExtractLogs(repo)

        p = mp.Process(target=ExtractLogs, args=(repo,))
        p.start()            
        
        message = 'Logs Extraction Scheduled.'
        return render_template('expr/szz/repoinfo.html', repo=repo, message = message)

    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))
    

@BPSZZ.route('/repologs/<id>',methods=['GET'])
def repologs(id):
    if Shared.isLoggedIn():
        repo = Repo.query.filter_by(id=id).first()
        logs = Log.query.filter_by(repoId = id)
            
        return render_template('expr/szz/repologs.html', logs=logs, repo=repo)

    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))


@BPSZZ.route('/reposzzs/<id>',methods=['GET'])
def reposzzs(id):
    if Shared.isLoggedIn():
        repo = Repo.query.filter_by(id=id).first()
        szzs = SZZBlame.query.filter_by(repoId = id)
            
        return render_template('expr/szz/reposzzs.html', szzs=szzs, repo=repo)

    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))

@BPSZZ.route('/minifycode/<id>',methods=['GET', 'POST'])
def minifycode(id):
    pass


def ParseBlames():
    pass

@BPSZZ.route('/szzparse/<id>',methods=['GET', 'POST'])
def szzparse(id):
    message=None

    if Shared.isLoggedIn():
        repo = Repo.query.filter_by(id=id).first()    
        
                    
        ParseBlames()
        message = 'Parse Blames Started.'
        return render_template('expr/szz/repoinfo.html', repo=repo, message = message)
    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))

@BPSZZ.route('/gendata/<id>',methods=['GET', 'POST'])
def gendata(id):
    pass

def GenGraphs(repo, exts=None):
    if exts is None:
        exts = Helpers.currentExts
    if isinstance(exts, list):
        exts = tuple(exts)
    repofiles = RepoFile.query.filter_by(repoId = repo.id)
    
    for rf in repofiles:
        if rf.file.endswith(exts):
            revs = rf.revs
            auth = rf.authors
            g = GraphBuilder(config.basedir+'/'+repo.path)
            for row in g.buildGraph(rf.file,revs = revs,authors=auth):
                rd = RevisionData()
                rd.revIndex = row[0]
                rd.rev = row[1]
                rd.author = row[2]
                rd.gDump = row[3]
                rd.repoFileId = rf.id
                rd.repoId = repo.id
                db.session.add(rd)
                db.session.commit()
            print (rf.file)



@BPSZZ.route('/genannot/<id>',methods=['GET', 'POST'])
def genannot(id):

    if Shared.isLoggedIn():
        repo = Repo.query.filter_by(id=id).first()

        #GenGraphs(repo)

        p = mp.Process(target=GenGraphs, args=(repo,))
        p.start()            
        
        message = 'Graph Generation Scheduled.'
        return render_template('expr/szz/repoinfo.html', repo=repo, message = message)

    else:
        error = ' You are not logged in'
        return redirect(url_for('BPUsers.login'))

    

@BPSZZ.route('/stats/<id>',methods=['GET', 'POST'])
def stats(id):
    pass


@BPSZZ.route('/myrepos',methods=['GET', 'POST'])
def myrepos():
    
    error = None
    completedClones = None
    u = None
    if Shared.isLoggedIn(): 
                   
        
        u = Shared.getLoggedInUser()
        repos = Repo.query.filter_by(userId = int(session['u']))
        completedClones = repos.filter(Repo.cloneFinishDate!='--RUNNING--')
        runningClones = repos.filter(Repo.cloneFinishDate=='--RUNNING--')

        return render_template('expr/szz/myrepos.html', error=error, completedClones = completedClones, u = u, runningClones = runningClones)
    return redirect(url_for('BPUsers.login'))       

@BPSZZ.route('/clonerepo',methods=['GET', 'POST'])
def clonerepo():    
    error = None
    ret = None
    
        
    if Shared.isLoggedIn():        
        if request.method == 'POST':
            url = None                   
            repoName = None
            isPrivate = False
            uid = Shared.getLoggedInUser().id
            try:
                pars = {
                    'url': request.form['url'],
                    'repoName': request.form['repoName'],
                    'isPrivate': 'isPrivate' in request.form,
                    'uid' : uid
                    }
                            
            except Exception as e:
                error = str(e)
                print (error)
                return render_template('expr/szz/clonerepo.html', error=error)
            try:
                                

                #RunWithPars(pars,uid)


                p = mp.Process(target=RunWithPars, args=(pars,uid))
                p.start()            
                ret  = 'Scheduled. Check the cloning status in your repository page.'
                error = None
            except Exception as ex:
                error = str(ex)
                ret = None
            
        return render_template('expr/szz/clonerepo.html', error=error, result = ret)
    else:
        error = 'You are not logged in'
        return redirect(url_for('BPUsers.login'))
    return render_template('expr/szz/clonerepo.html')
