import os
from subprocess import Popen, PIPE
import json
import shutil
import random
import pickle
from .Helpers import Helpers

pth = 'RawSourcesCF\\'
pthOut = 'RawSourcesCFOUT\\'
pthTmp = 'RawSourcesCFTMP\\'


import sys


os.chdir(Helpers.mcPath)

##Logger. print to stdout and file 
class Logger(object):
    def __init__(self,fid=None):
        self.terminal = sys.stdout
        
        if fid == None:
            
            self.log = open("TMP/CLANG-FORMAT-CONVERT-LOG-0.txt", "w")
        else:
            self.log = open("TMP/CLANG-FORMAT-CONVERT-LOG-"+str(fid+1)+".txt", "w")
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
        self.log.flush()    
    def flush(self):
        pass

#pth = 'testfol/'
def cf(fq,pid):
    sys.stdout = Logger(pid)
    print ('Started Formatting in ', pid)
    maxsizepart = 100000
    while not fq.empty():
        file = fq.get()        
        
        fl = file.lower()

        if fl.endswith('.tmp') or fl.endswith('.tmpx') or fl.endswith('.hconverted.cpp') or fl.endswith('.cconverted.cpp') or fl.endswith('.ccconverted.cpp') or fl.endswith('.cppconverted.cpp') or fl.endswith('.hhconverted.cpp'):
            print ('Removed:', file, fq.qsize())
            os.remove(pth+file)
            continue
        if fl.startswith('rev-'):# and (fl.endswith('.cpp') or fl.endswith('.h') or fl.endswith('.cc') or fl.endswith('.hh') or fl.endswith('.c')):
            print ('Minified:', file, fq.qsize())
            st = os.stat(pth+file)
            
            if st.st_size>100000:
                i = 0
                curline = 0
                o = open(pth+file,encoding='utf8')
                lines = o.readlines()
                o.close()
                countLines = len(lines)
                cfailed = False
                while True:
                    sizesel = 0
                    
                    o = open(pthTmp+file+'--'+str(i)+'.tmpx','w',encoding='utf8')
                    for j in range(curline,min(curline+1000,countLines)):
                        sizesel+=len(lines[j])
                        o.write(lines[j])
                        if sizesel>=maxsizepart:
                            break
                    curline=j+1
                    cntns = 0
                    
                    while curline<countLines:
                        if sizesel>=maxsizepart:
                            break
                        line = lines[curline]
                        o.write(line)
                        curline+=1
                        sizesel+=len(line)
                        if line.replace('\n','').strip().endswith(';'):
                            break
                        cntns+=1
                        if cntns>=200:
                            break
                    o.close()
                    with Popen(r'clang-format.exe -style=file "%s" > "%s"'%(pthTmp+file+'--'+str(i)+'.tmpx', pthTmp+file+'--'+str(i)+'.tmpc'),shell=True, stdout=PIPE, stderr=PIPE) as p:
                        outc, errors = p.communicate()
                        if outc.decode('utf8').find('crash dump file')>0:
                            print ('Part Conversion Failed for ',file,i)
                            cfailed = True
                            break
                        if errors.decode('utf8').find('crash dump file')>0:
                            print ('Part Conversion Failed for ',file,i)
                            cfailed = True
                            break
                        outc = None
                        errors = None
                    p=None
                    
                    i+=1
                    if curline>=len(lines):
                        o = open(pthOut+file,'w',encoding='utf8')
                        for j in range(i):
                            oo = open(pthTmp+file+'--'+str(j)+'.tmpc')
                            o.write(oo.read())
                            oo.close()
                            os.remove(pthTmp+file+'--'+str(j)+'.tmpx')
                            os.remove(pthTmp+file+'--'+str(j)+'.tmpc')
                        o.close()
                        break
                
                if cfailed == True:
                    print ('Part Conversion Failed, Break and Copied:', file, fq.qsize())
                    shutil.copy(pth+file,pthOut+file)
            else:
                cfailed = False
                with Popen(r'clang-format.exe -style=file "%s" > "%s"'%(pth+file,pthOut+file), shell=True,stdout=PIPE, stderr=PIPE)  as p:
                    outc, errors = p.communicate()
                    if outc.decode('utf8').find('crash dump file')>0:
                        print ('Conversion Failed for ',file)
                        cfailed = True
                        
                    if errors.decode('utf8').find('crash dump file')>0:
                        print ('Conversion Failed for ',file)
                        cfailed = True
                    outc = None
                    errors = None
                p=None
                if cfailed == True:
                    print ('Conversion Failed, Copied:', file, fq.qsize())
                    shutil.copy(pth+file,pthOut+file)
                
        else:
            print ('Copied:', file, fq.qsize())
            shutil.copy(pth+file,pthOut+file)
    print (pid,'Finished Formatting...')

if __name__=='__main__':
        
    sys.stdout = Logger()
    
    print ('Started... Getting List of Files')
    import multiprocessing as mp
    manager = mp.Manager()
    
    fq = manager.Queue()

    if not os.path.exists(pth):
        raise Exception ('Path '+ pth+ ' Not Found')

    if not os.path.exists(pthOut):
        os.makedirs(pthOut)

    if not os.path.exists(pthTmp):
        os.makedirs(pthTmp)

    fileNameq = 'RawSourcesCFFileQ.PKL'
    #if os.path.exists(fileNameq):
    if False:
        with open(fileNameq,'rb') as pkl:
            fq = pickle.load(pkl)
            print ('Q Loaded')    
    else:
        
        jsonfileName = 'RawSourcesCFFileList.json'
        if os.path.exists(jsonfileName):
            with open(jsonfileName,encoding='utf8') as jsonfile:
                files = json.load(jsonfile)
        else:
            files = os.listdir(pth)
            with open(jsonfileName,'w',encoding='utf8') as jsonfile:
                json.dump(files, jsonfile)

    
        #print(files)
        random.shuffle(files)
        print ('Creating the file Queue')
        for file in files:
            fq.put(file)

        with open(fileNameq,'wb') as pkl:
            pickle.dump(fq, pkl)
            pkl.flush()
    
        
        files = None
        
    print ('Converted to Q', 'Press a key to start...')
    input ()
    
    numproc = 50
    
    i = 0
    
    
    processes = [mp.Process(target=cf,args=(fq,i)) for i in range(numproc)]
    for p in processes:
        p.start()

    for p in processes:
        p.join()
