from flask import Flask, render_template, session, request, abort
#import multiprocessing as mp
#import time
from flask_sqlalchemy import SQLAlchemy
#from os import environ as env
from config import Config
import os
import config
from flask_bcrypt import Bcrypt
#import sys
import uuid
import json
import urllib
import traceback
app = Flask(__name__)


@app.errorhandler(Exception)
def handle_error(e):
    trace = traceback.format_exc()
    o = open('error.txt','w')
    o.write(str(trace))
    o.close()
    return str(e)


"""
App Secret Key
A Secret key is generated for the app in it does not exist. The generated key is 
generated using uuid library. The key is loaded on later runs/restarts. 
"""
a_s_k_FileName = 'a_s_k'
app.secret_key = ''
if os.path.exists(a_s_k_FileName):
    with open(a_s_k_FileName,'r') as a_s_k:
        app.secret_key = a_s_k.read()
else:
    with open(a_s_k_FileName,'w') as a_s_k:
        sk = str(uuid.uuid4())
        a_s_k.write(sk)
        app.secret_key = sk
if app.secret_key == '':
    raise Exception ('Invalid Configuration')


app.config.from_object(Config)
db = SQLAlchemy(app)
bcr = Bcrypt(app)


"""
Handling CSRF:
a csrf token is inserted into the forms and in each Post Request, the validity of the token is
evaluated. Invalid csrf token, points to invalid behaviour and causes 403 abort. 

Added:
Beside checking the csft token and since this handles before_request, the validity of google recaptcha
is checked if included in the request. Invalid recaptcha causes an abort 403 call.
"""
@app.before_request
def csrf_protect():
    if request.method == "POST":
        #Check CSRF Token - If invalid, abort
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

        #Google Re-Captcha
        if 'g-recaptcha-response' in request.form.keys():

            response = request.form.get('g-recaptcha-response')
            showalert = True
            if not checkRecaptcha(response,config.Config.RECAPTCHA_PRIVATE_KEY):
                abort(403)
            

def generate_csrf_token():
    """
    Creates a uuid.uuid4 string to be used as CSRF token and session key
    """

    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid.uuid4())
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token   

import models

##Register CKEditor with the app for the Blog Section.
from flask_ckeditor import CKEditor
ckeditor = CKEditor(app)


##Register the blueprints

from Blueprints import BPUsers,BPBlog, BPExperiments, BPSZZ

app.register_blueprint(BPExperiments)
app.register_blueprint(BPUsers)
app.register_blueprint(BPBlog)
app.register_blueprint(BPSZZ)

import Shared

@app.route('/')
def index():
    """
    Start page
    """
    u = Shared.getLoggedInUser()               
    return render_template("index.html",  u = u)


def checkRecaptcha(resp, skey):
    """
    Validates google recaptcha
    :param resp       data received from the request
    :param skey      the private key for the recaptcha
    """
    url = 'https://www.google.com/recaptcha/api/siteverify?secret=%s&response=%s' % (skey,resp)
    try:
        result = json.loads(urllib.request.urlopen(url).read())
        if result['success']:
            return True
        else:
            return False
    except Exception as e:
        return False
