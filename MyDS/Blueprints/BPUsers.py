from flask import Blueprint, render_template, redirect, url_for, request
import os
from os import environ as env
from app import bcr, db, session
from models import User, Experiment
import json
from DA.ExpDA import ExpDA
import config
from Lib import Security

BPUsers = Blueprint('BPUsers', __name__)

@BPUsers.route('/signup',methods=['GET', 'POST'])
def signup():    
    error = None
    if request.method == 'POST':
        #if not valie return error:
        #if request.form['email'] != 'admin@admin.com' or request.form['password'] != 'admin' or len(str(request.form['name']))==:
        #    error = 'Invalid Credentials. Please try again.'
        #else:
        #    return redirect(url_for('index'))

        email = request.form['email']
        name = request.form['name']
        password = bcr.generate_password_hash(request.form['password']).decode()
        
        exists = User.query.filter_by(username=email).first()
        
        if exists is not None:
            error = "User already exists."
        else:
            try:
                user = User()
                user.email = email
                user.password = password
                user.name = name
                user.username = email
                user.utype = 2
                user.registrationDate = str(Shared.getCurrentTimeMil())

                db.session.add(user)
                db.session.commit()
                return redirect(url_for('BPUsers.login'))
            except Exception as ex:
                error = 'Error in signup:'+str(ex)            

    return render_template('users/signup.html', error=error)



@BPUsers.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        email = request.form['email']
        
        u = User.query.filter_by(username=email).first()
        
        if u is not None:
            password = u.password.encode()
            
            passMatch = bcr.check_password_hash(password, request.form['password'])
            
            if not passMatch:
                error = 'Invalid Credentials. Please try again.'
            else:
                session['u'] = u.id
                return redirect(url_for('index'))
    
    return render_template('users/login.html', error=error)

import Shared

@BPUsers.route('/dashboard')
def dashboard():
    
    error = None
    completedExps = None
    u = None
    try:
        if Shared.isLoggedIn(): 
        
            import models
            u = Shared.getLoggedInUser()
            
            exps = models.Experiment.query.filter_by(userId = int(session['u']))
            completedExps = exps.filter(Experiment.endDateTime!='--RUNNING--')
            cDataSets = [json.loads(ce.pars)['datasets'] for ce in completedExps] 
        
            md5Names =[ExpDA.generateViolinPlots(cexp) for cexp in completedExps]    
            plotFiles = [['/static/plots/'+m+'/'+file for file in os.listdir(config.plotsPath+m) if file.endswith('.svg') and file.startswith('Method')] for m in md5Names]
            runningExps = exps.filter(Experiment.endDateTime=='--RUNNING--')
            runningValid = []
            for r in runningExps:
                pid = json.loads(r.pars)['pid']
                if not Security.check_pid(pid):
                    runningValid.append(False)
                else:
                    runningValid.append(True)
                    #r.delete()
                    #db.session.commit()
            return render_template('users/dashboard.html', error=error, completedExps = completedExps, u = u, runningExps = runningExps, cDataSets = cDataSets, plotFiles = plotFiles, runningValid = runningValid)
    except Exception as exep:
        file = open('error.txt','w')
        file.write(str(exep))
        file.close()

    return redirect(url_for('BPUsers.login'))


@BPUsers.route('/signout')
def signout():
    if 'u' in session:
        session.pop('u',None)
    return redirect(url_for('index'))


@BPUsers.route('/resetpassword')
def resetpassword():    
    pass

#AJAX CALL
@BPUsers.route('/generate_plots_per_dataset',methods=['GET'])
def submit_comment_reply():
    pass

    #message = None
    #data = json.loads(request.data)
    #ds = data['dataset']
    #expId=int(data['id'])
    #exp = None
    #if Shared.isLoggedIn():
    #    user = Shared.getLoggedInUser()
    #    exp = models.Experiment.query.filter_by(id = expId)
    #    if exp==None or len(exp)!=1 or exp.userId!=user.id:
    #        print ('Not authorised or not found')
    #        return redirect(url_for('BPUsers.login'))
    #else:
    #    return redirect(url_for('BPUsers.login'))
    
    #expHash = generatePlots(exp)

    #resp = make_response(render_template('blog/singleComment.html', comment = pc))
    #return json.dumps({'html':resp.data.decode("utf-8"), "id":str(inReplyTo)})
    