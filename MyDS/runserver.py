"""
This script runs the MyDS application using a development server.
"""
import os
pardir = os.path.abspath(os.pardir).replace('\\','/')+'/'

#comps = ['PyCQ/','PyGIS/','PyLib/','PyLSH/','PySZZ/']

import sys

#for comp in comps:
#    if not (pardir+comp in sys.path):
#        sys.path.append(pardir+comp)
sys.path.append(pardir)

import config
from os import environ
from app import app
from io import StringIO


if __name__ == '__main__':
    
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
