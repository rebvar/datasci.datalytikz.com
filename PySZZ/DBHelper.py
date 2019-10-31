import sqlite3
from .Helpers import Helpers

class DBHelper:

    
    def __init__(self, dbname="SZZData.db", setup = True):
        
        self.dbname = dbname
        
        self.conn = sqlite3.connect(Helpers.mcPath+dbname,timeout=60)
        self.cursor = self.conn.cursor()
        if setup:
            self.setup()

    def close(self):
        self.conn.close()
        self.cursor = None

    def setup(self):
        
        stmt = "CREATE TABLE IF NOT EXISTS LOGS (locid INTEGER primary key, cid text, parents text, m text, author text, date text, tags text, branches text, cidshort text, files text, timestamp REAL,pushdateTimestamp REAL)"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = "CREATE TABLE IF NOT EXISTS BC (locid INTEGER primary key, cid text, parents text, m text, author text, date text, tags text, branches text, cidshort text, files text, timestamp REAL,pushdateTimestamp REAL, bugs text)"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = "CREATE TABLE IF NOT EXISTS VALIDBUGSREST (bug INTEGER PRIMARY KEY,assignedTo text,modDateText text,modTimestamp REAL,reportDateText text,reportTimestamp REAL,reporter text,status text,product text, component text, version text, target text, keywords text)"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = "CREATE TABLE IF NOT EXISTS VALIDBUGS (bug INTEGER PRIMARY KEY,assignedTo text,modDateText text,modTimestamp REAL,reportDateText text,reportTimestamp REAL,reporter text,status text,product text, component text, version text, target text, keywords text)"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = "CREATE TABLE IF NOT EXISTS PATCHES (patchId INTEGER PRIMARY KEY,bug int,patchDateText text,patchTimestamp REAL,patchRowType text,author text,commentLink text,patchText text, patchSize text, patchFlagUsers text, patchFlagTypes text, patchFlagStatus text)"
        self.conn.execute(stmt)
        self.conn.commit()
        
        stmt = "CREATE TABLE IF NOT EXISTS FILES (file text primary key, revs text,authors text)"
        self.conn.execute(stmt)
        self.conn.commit()


    def setupTableForGraph(self):
        stmt = "CREATE TABLE IF NOT EXISTS [RevisionData] (revIndex integer primary key, revID integer,author text, gDump text)"
        self.conn.execute(stmt)
        self.conn.commit()

    def setupCleanTableForGraph(self):

        stmt = "DROP TABLE  IF EXISTS [RevisionData]"
        self.conn.execute(stmt)
        self.conn.commit()

        stmt = "CREATE TABLE  IF NOT EXISTS [RevisionData] (revIndex integer primary key, revID integer,author text, gDump text)"
        self.conn.execute(stmt)
        self.conn.commit()

        


    def EXEC_QUERY(self, QUERY_TEXT):
        stmt = QUERY_TEXT
        self.conn.execute(QUERY_TEXT)
        self.conn.commit()

    

    def InsertMany(self,datarows,keys,table = 'VALIDBUGS'):        
        
        fields = ','.join(keys)
        q = ','.join(['?' for _ in range(len(keys))])
        size =10000
        
        if len(datarows)%size == 0:
            parts = int(len(datarows)/size)
        else:
            parts = int(len(datarows)/size)+1        
        for i in range(parts):
            self.cursor.executemany("INSERT INTO ["+table+"]  ("+fields+") VALUES ("+q+")", datarows[i*size:min((i+1)*size,len(datarows))])
        self.conn.commit()
    
        

    
    
    def CleanInsertMany(self,datarows,keys,table = 'VALIDBUGS'):        
        self.cursor.execute("delete from [%s]"%table)
        self.conn.commit()
        fields = ','.join(keys)
        q = ','.join(['?' for _ in range(len(keys))])
        size =10000
        
        if len(datarows)%size == 0:
            parts = int(len(datarows)/size)
        else:
            parts = int(len(datarows)/size)+1        
        for i in range(parts):
            self.cursor.executemany("INSERT INTO ["+table+"]  ("+fields+") VALUES ("+q+")", datarows[i*size:min((i+1)*size,len(datarows))])
        self.conn.commit()


    def Clean(self, table = 'RevisionData'):
        self.cursor.execute("delete from [%s]"%table)
        self.conn.commit()


    def Insert(self,row,keys = None,table = 'RevisionData', keysStr = None):
        
        if keysStr==None:
            fields = ','.join(keys)
        else:
            fields = keysStr
        q = ','.join(['?' for _ in range(len(keys))])
        self.cursor.execute("INSERT INTO ["+table+"]  ("+fields+") VALUES ("+q+")", row)
        self.conn.commit()

    
    
    def GET_ALL(self,table = 'LOGS',fields = [],Where = ''):
        fieldsStr = '*'
        if len(fields)>0:
            fieldsStr = ','.join(fields)
        self.cursor.execute('SELECT %s from [%s] %s' % (fieldsStr,table,Where))
        names = [description[0] for description in self.cursor.description]
        return self.cursor.fetchall(),names

    