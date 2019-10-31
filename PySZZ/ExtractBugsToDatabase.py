from .DBHelper import DBHelper
from Helpers import Helpers
import os
import shutil

def ParseBugPages(filesq,procId,q):
    #
    #if not str(procId) in md.keys():
    #    md[str(procId)] = []
    print ('Started:',procId)
    i = 0
    while not filesq.empty():
         
        file = filesq.get()
        i+=1
        if file.startswith('-1--') or file.startswith ('-2--'):
            continue
        print ('Processing (in '+ str(procId) +') : ','Remaining',filesq.qsize())
        data,stat = Helpers.getBugData(file.replace('.html',''),Helpers.ExtractBugData)
        if stat < 0:
            shutil.move(Helpers.bpPath+file,Helpers.bpPath+str(stat)+'--'+file)
            continue
        
        q.put(data)
        #ret = dbh.InsertBug(data)
        #print ('In ',procId,' :', data['bug'],ret)
    print ('Finished:',procId)


if __name__ == '__main__':

    
    
    #ParseBugPages(bugfiles,dbh,0)

    import multiprocessing as mp
    manager = mp.Manager()
    md = manager.dict()
    q = manager.Queue()
    filesq = manager.Queue()
    bugfiles = os.listdir(Helpers.bpPath)
    for file in bugfiles: 
        filesq.put(file)
    numproc = 20
    
    processes = [mp.Process(target=ParseBugPages,args=(filesq,i,q)) for i in range(numproc)]
    for p in processes:
        p.start()

    for p in processes:
        p.join()


    dbh = DBHelper()
    
    i = 0
    datarows = []
    keys = None
    
    while not q.empty():
        i+=1
        if i%10000==0:
            print ('Processing ',i)
        data = q.get()
        
        if keys==None:
            keys = sorted(data.keys())
        datarows.append([data[key] for key in keys])
        
    ret = dbh.CleanInsertMany(datarows,keys,table = 'VALIDBUGS')
        