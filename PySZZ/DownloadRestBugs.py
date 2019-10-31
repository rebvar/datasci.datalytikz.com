from .DBHelper import DBHelper
from .Helpers import Helpers

if __name__ == '__main__':
    print ('Started')
    dbh = DBHelper()
    logs,logcolnames = dbh.GET_ALL(table='LOGS')
    print ('Getting Log IDS')
    logcids = [l[logcolnames.index('cid')] for l in logs]
    print ('Downloading')
    Helpers.Download(logcids,'LOGPAGES')
