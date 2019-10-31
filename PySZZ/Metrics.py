
from .Helpers import Helpers
from .AnnotGraph import *
import os
import os.path
import os
import random
import multiprocessing as mp
import datetime
from subprocess import Popen, PIPE



def GenerateMetricsFromSourceFolder(q,j,sourceFolder,indb = False,mfol = ""):
    i = 0

    print ('Started Process : ('+str(j)+')')
    tf = open (Helpers.mcPath+mfol+"MI-"+str(j),'w')
    while not q.empty():
         
        fid,file = q.get()
        revs = AnnotHelpers.loadPickle(fid,"Revs",sourceFolder)
        i+=1

        for rindex, rev in enumerate(revs):
            fn = 'Rev-%d===%d' % (rindex,fid)
            with Popen(r'qmcalc.exe "%s"'%(Helpers.mcPath+sourceFolder+fn),
                stdout=PIPE, stderr=PIPE) as p:
                out, errors = p.communicate()

            out = Helpers.ConvertToUTF8(out)
            
            #with open(Helpers.mcPath+mfol+fn,'w') as o:
            #    o.write(out)
            #    o.close()
            tf.write('%d;%d;%d;%s\n'%(fid,rindex,rev,out.replace('\n','').replace('\r','')))
        if i%5==0:
            print ('In ('+str(j)+') - Done:',i, 'Remaining', q.qsize())
        
        revs = None
        
    tf.close()
    print ('Pr('+str(j)+') Finished...')



if __name__ == '__main__':
    
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
    

    

    i = 0
        
    manager = mp.Manager()
    q = manager.Queue()
    prcount = manager.Value('i',0)
    for file in cfiles:
        q.put(file)
    
    prcount = None
    numproc = 100
    indb = True
    #CheckGraphsForSourceFolder(q,i,'RawSourcesCFOUT/',indb)


    sfolder = 'RawSourcesCFOUT/'
    mfol = sfolder[:-1]+'Metrics/'

    if not os.path.exists(Helpers.mcPath+mfol):
        os.makedirs(Helpers.mcPath+mfol)


    #GenerateMetricsFromSourceFolder(q,i,'RawSources/',indb,mfol)

    

    processes = [mp.Process(target=GenerateMetricsFromSourceFolder,args=(q,i,sfolder,indb,mfol)) for i in range(numproc)]
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



    SourceFolder =Helpers.mcPath+'RawSourcesMetrics/'

    for i in range(100):
        o = open(SourceFolder+'MI-'+str(i))

        lines = o.read().split('\n')

        o.close()
        for line in lines:
            if line.find(';')<0:
                continue
            line = line.split(';')
            fid = line[0]
            revIndex = line[1]
            revID = line[2]
            metrics = line[3]

            if not fid in MetricsChgData.keys():
                MetricsChgData[fid] = {}

            if not revID in MetricsChgData[fid].keys():
                MetricsChgData[fid][revID] = {}
            MetricsChgData[fid][revID]=[float(t.strip()) if len(t.strip())>0 else 0 for t in metrics.split('\t')]
        print (i)


    countMetrics = len(MetricsChgData[revID][0])
    print (len(MetricsChgData.keys()), countMetrics)
    input()

    


    o = open('MetricsProcessedCFOUT.txt','w')

    MetricsProcessed = {}

    cnt = 0
    for revID in MetricsChgData.keys():
        cnt+=1
        nmt = []
        for i in range(countMetrics):

        
            vals = [MetricsChgData[revID][t][i] for t in range(len(MetricsChgData[revID]))]

            nmt.append(max(vals))
            nmt.append(min(vals))
            nmt.append(np.mean(vals))
            nmt.append(np.median(vals))
            nmt.append(MAD(vals))

        MetricsProcessed[revID] = nmt
        o.write(revID+';'+','.join([str(n) for n in nmt])+'\n')
        if cnt%1000 == 0 :
            print(cnt)
    o.close()

    print ('Done')
    