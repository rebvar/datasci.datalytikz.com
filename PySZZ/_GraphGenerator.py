
from .Helpers import Helpers
from .AnnotGraph import *
import os
import os.path
import os
import random
import multiprocessing as mp
import datetime
from .AnnotGraph import GraphBuilder

Name = 'KIM'

def GenerateGraphForList(q,j):
    i = 0
    g = GraphBuilder()    
    while not q.empty():
         
        fid,file = q.get()
        
        i+=1
        
        print ('In ('+str(j)+') : '+file, ' Remaining', q.qsize())

        g.buildGraph(file = file,type=Name,procId = j,IndexId = i,fid=fid)
    print ('Pr('+str(j)+') Finished...')

def GenerateGraphFromSourceFolder(q,j,sourceFolder,indb = True):
    i = 0

    print ('Started Process : ('+str(j)+')')

    g = GraphBuilder(indb=indb,dbName = 'Graphs'+Name)
    while not q.empty():
         
        fid,file = q.get()
        revs = AnnotHelpers.loadPickle(fid,"Revs",sourceFolder)
        authors = AnnotHelpers.loadPickle(fid,"Authors",sourceFolder)
        i+=1
        if i%5==0:
            print ('In ('+str(j)+') - Done:',i, 'Remaining', q.qsize())
        dfn = str(fid)
        g.buildGraph(file = file,type=Name,procId = j,IndexId = q.qsize(),SourceCodeFiles = ['Rev-'+str(k)+"==="+dfn for k in range(len(revs))],sourceCodeFilesPath=sourceFolder,revs = revs,authors = authors,fid = fid)
        revs = None
        authors = None

    print ('Pr('+str(j)+') Finished...')



def CheckGraphsForSourceFolder(q,j,sourceFolder,indb = True,prcount = None):
    i = 0

    print ('Started Process : ('+str(j)+')')

    g = GraphBuilder(indb=indb,dbName = 'Graphs'+Name)
    while not q.empty():
         
        fid,file = q.get()
        revs = AnnotHelpers.loadPickle(fid,"Revs",sourceFolder)
        dbh = DBHelper(dbname='Graphs'+Name+'/'+str(fid),setup=False)
        revs2,RcolNames = dbh.GET_ALL('RevisionData',fields=['revID'])
        dbh.close()
        revs2 = [r[0] for r in revs2]
        print ('In ('+str(j)+') - PRCDone:',file, fid, i, 'Remaining', q.qsize())

        i+=1
        #if i%300==0:
        #    print ('In ('+str(j)+') - Done:',i, 'Remaining', q.qsize())
        #if (prcount!=None and prcount.value>=90):
        #    print ('In ('+str(j)+') - PRCDone:',file, fid, i, 'Remaining', q.qsize())
        if len(revs)!=len(revs2):
            print ('Not Finished',file,fid,len(revs),len(revs2))
            input()
        for k in range(len(revs)):
            if revs[k]!=revs2[k]:
                print ('Not The same',file,fid,len(revs),len(revs2),revs,revs2)
                input()
        revs = None
        revs2 = None
        RcolNames = None

    if prcount!=None:
        prcount.value +=1
    print ('Pr('+str(j)+') Finished...')


def CopyToType(q,j,fromtype,totype):
    i = 0
    g = GraphBuilder()    
    while not q.empty():
         
        fid,file = q.get()
        
        i+=1
        
        print ('In ('+str(j)+') : '+file, ' Remaining', q.qsize())
        
        g.CopyToType(file = file,fromtype=fromtype,totype=totype,procId = j,IndexId = i,fid=fid)
    print ('Pr('+str(j)+') Finished...')


def ExtractSources(q,j):
    i = 0
    g = GraphBuilder()    
    while not q.empty():
         
        fid,file = q.get()
        
        i+=1
        
        #print ('In ('+str(j)+') : '+file, ' Remaining', q.qsize())
        
        g.ExtractAllSources(file = file,procId = j,qs=q.qsize(),fid = fid)
    print ('Pr('+str(j)+') Finished...')
    

def CopySources(q,j,s,t):
    i = 0
    g = GraphBuilder()    
    
    while not q.empty():
         
        fid,file = q.get()
        
        i+=1
        
        #print ('In ('+str(j)+') : '+file, ' Remaining', q.qsize())
        
        g.Minify2Extracted(file = file,procId = j,qs=q.qsize(),sourcePath=s,tgtPath=t,fid=fid)
    print ('Pr('+str(j)+') Finished...')
    
        
def GennAuthors(q,j):
    i = 0
    g = GraphBuilder()    
    while not q.empty():
         
        fid,file = q.get()
    
        i+=1
        if i%500==0:
            print ('In ('+str(j)+') :',i, ' Remaining', q.qsize())
        g.RebuildAuthors(file = file,type=Name,procId = j,IndexId = i,fid=fid)
    print ('Pr('+str(j)+') Finished...')

def GennRevsAuthors(q,j):
    i = 0
    g = GraphBuilder()    
    while not q.empty():
         
        fid,file = q.get()
        i+=1
        if i%500==0:
            print ('In ('+str(j)+') :',i, ' Remaining', q.qsize())
        g.RebuildRevsAuthors(file = file,type=Name,procId = j,IndexId = i,fid=fid)
        
    print ('Pr('+str(j)+') Finished...')


import sys
##Logger. print to stdout and file 
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("OtherModules/mystdoutMultiProc"+Name+".txt", "a+")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
        self.log.flush()    
    def flush(self):
        pass

sys.stdout = Logger()


def main():

    dbh = DBHelper()
    cfiles,fcols =dbh.GET_ALL(table='FILES',fields=['ROWID','file'])

    if len(cfiles) ==0:

        files = Helpers.GetAllFiles()
        dbh.CleanInsertMany(datarows = [(file,) for file in files],keys=['file'],table='FILES')
    
    cfiles,fcols =dbh.GET_ALL(table='FILES',fields=['ROWID','file'])
    
    dbh.close()
    cfiles = [file for file in cfiles if Helpers.isExtValidCpp(file[1])]

    print ('Count valid (c/c++/hh/h/cc) : #', len(cfiles))
    input()
    

    start = datetime.datetime.now()

    i = 0
        
    manager = mp.Manager()
    q = manager.Queue()
    prcount = manager.Value('i',0)
    for file in cfiles:
        q.put(file)
    
    prcount = None
    numproc = 150
    indb = True
    #CheckGraphsForSourceFolder(q,i,'RawSourcesCFOUT/',indb)
    processes = [mp.Process(target=GenerateGraphFromSourceFolder,args=(q,i,'RawSources/',indb)) for i in range(numproc)]
    for p in processes:
        p.start()

    for p in processes:
        p.join()
    #precount = 0
    #while prcount.value<len(processes):
    #    time.sleep(1)        
    #    if precount!=prcount.value:
    #        print ('Finished ', prcount.value, ' Processes')
    #        precount = prcount.value


    print ('Done')
    end = datetime.datetime.now()
    print (start)
    print (end)

if __name__ == '__main__':    
    main()