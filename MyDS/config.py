"""
App configurations
"""
import os
basedir = os.path.abspath(os.path.dirname(__file__)).replace('\\','/')
dbname = 'maindb.db'
dbpath = basedir+'/'+dbname
uploadsPath = basedir+'/static/upload'
reposPath = basedir+'/SavePath/Repos/'
plotsPath = basedir+'/static/plots/'

if not os.path.exists(uploadsPath):
    os.makedirs(uploadsPath)

if not os.path.exists(reposPath):
    os.makedirs(reposPath)


"""
Google Recaptcha Data. Need to create the file before starting the program.
"""

recKeyFile = 'google_recaptcha_file'
R_PUB_KEY = ''
R_PRIV_KEY = ''
try:
    file = open(basedir+'/'+recKeyFile)
    R_PUB_KEY = file.readline().replace('\n','')
    R_PRIV_KEY = file.readline().replace('\n','')
except Exception as ex:
    raise Exception("Google Recaptcha file not found.")

class Config(object):
    DEBUG = False
    PROPAGATE_EXCEPTIONS = True
    # ...
    SQLALCHEMY_DATABASE_URI =  'sqlite:///'+dbpath
    SQLALCHEMY_TRACK_MODIFICATIONS = False    
    CKEDITOR_SERVE_LOCAL = True
    CKEDITOR_HEIGHT = 500
    CKEDITOR_WIDTH = 1024
    CKEDITOR_FILE_UPLOADER = 'BPBlog.upload'    
    UPLOADED_PATH = uploadsPath
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = R_PUB_KEY
    RECAPTCHA_PRIVATE_KEY = R_PRIV_KEY
