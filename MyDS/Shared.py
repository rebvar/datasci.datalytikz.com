from app import app,db, session
from flask import redirect, url_for
import time

def isLoggedIn():
    if 'u' in session:
        return True
    return False


def getLoggedInUser():
    if isLoggedIn():
        from models import User
        u = User.query.filter_by(id = int(session['u'])).first()
        if u==None:
            session.pop('u',None)
            return redirect(url_for('index'))
        return u
    return None


def getCurrentTimeMil():
    return int(round(time.time() * 1000))

