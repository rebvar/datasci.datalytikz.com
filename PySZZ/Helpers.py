import urllib
import urllib.request
from lxml.html import fromstring
import codecs
import os
import datetime
import dateutil
import dateutil.parser as parser
import time
import re
import pickle
import chardet
from PySZZ import GIT
import config


class Helpers:



    basePath = config.basedir+'/'
    repodir = basePath+'mozilla-central'
    mcPath = basePath+'MC/'    
    bpPath = mcPath+'BugPages/'
    bpPathRest = mcPath+'BugPagesRest/'
    LOGPagesPath = mcPath+'LOGPages/'
    ##Regexes for bugs
    rebugs = [r'bug[# \t=-]*[0-9]+', r'issue[# \t=-]*[0-9]+', r'fix(e[d|s]|ing|)?[# \t=-]*[0-9]+', r'b[# \t=-]+[0-9]+',r'pr[# \t=-]*[0-9]+',r'show\_bug\.cgi\?id=[0-9]+',r'\[[0-9]+\]']
    reexclude = [[r'back(ed|ing)?( )?out'],[r'merge'],[r'no bug'],[r'bump(ing)? gaia.json'],[r'bump(ing)? manifest(s)?'],[r'javascript test(s)?'],[r'add crashtest'],[r'regress([(ion)|(ed)]])?']]
    

    ##Fields in the dumped file from Mozilla central repository. The dump is generated using the command in the mytemplsCode variable below. 
    LogFieldsMy = ['locid','cid','parents','m','author','date','tags','branches','cidshort','files','timestamp']
    mytemplsCode = """hg log --template "changeset:{node|short};=;;-\nchangeshort:{node|short};=;;-\nrevision:{rev};=;;-\nauthor:{author};=;;-\ndate:{date|isodate};=;;-\nsummary:{desc};=;;-\nbranches:{branches};=;;-\ntags:{tags};=;;-\nparents:{parents};=;;-\nfiles:{files%'{file}---'};=;;-\n============================\n" --debug >../mc/mytempl.txt"""
    bcSep = ';;=;-;;'
    
    ##File Extensions
    cppExts = ['.c','.cpp','.h','.cc','.hh']
    currentExts = ['.c','.cpp','.h','.cc','.py','.hh','.java','.perl','.pl','.rb']
    
    ##Index of files field in the mozilla central repo dump file
    logFilesIndex = LogFieldsMy.index('files')
    

    ##Parse The logs from the hg log command according to the template provided in mytemplsCode variable in Helpers.py file.
    ##if dolower = True then the values in all fields would be lowered if they are strings. This however is dangerous as for example for the files field.
    ##hg is case sensitive when querying for the file information. Therefore, it is better to keep the case. But in case of need, one can set the option to True.
    ##The to text option if True, will convert all the  fields into strings. The timestamp and locid fields however, will be numbers if ToText = False
    def getAllLogsMy(dolower = False, ToText = False, LoadPushDates = True, file = None):
        if file is None:
            file = Helpers.mcPath+'mytempl.txt'
        o = open(file,'r')
        data = o.read().split(';=;;-\n============================\n')
        o.close()
        logs = []
        fields = set()
        for item in data:
            if len(item)<30:
                continue
            isValid=True
            parents = ''
            author = ''
            m = ''
            date = ''
            dateTimeStamp = ''
            locid = ''
            cid = ''
            cidshort = ''
            tags = ''
            files = ''
            branches = ''
            for line in item.split(';=;;-\n'):
                if dolower:
                    line = line.lower()
                p1 = line[:line.find(':')].strip()
                p2 = line[line.find(':')+1:].strip()
                if p1 == 'revision':
                    locid=p2
                    if locid=='':
                        isValid = False

                elif p1 == 'changeshort':
                    cidshort=p2
                elif p1 == 'files':
                    files=p2
                elif p1 == 'changeset':
                                      
                    cid = p2
                    if len(cid)<5:
                        isValid = False

                elif p1 == 'parents':
                    parents=','.join([t for t in p2.split(' ') if not t.startswith('-1')])
                elif p1 == 'summary':
                    m=p2
                elif p1 == 'date':
                    date = p2
                    dateTimeStamp = str(Helpers.getTimeStamp(date))
                elif p1 == 'author':
                    author=p2
                elif p1 == 'tags':
                    tags = p2
                elif p1 == 'branches':
                    branches == p2
            if isValid:
                if not ToText:
                    locid = int(locid)
                    dateTimeStamp = float(dateTimeStamp)

                if LoadPushDates:

                    logs.append([locid,cid,parents,m,author,date,tags,branches,cidshort,files,dateTimeStamp])
                else:
                    logs.append([locid,cid,parents,m,author,date,tags,branches,cidshort,files,dateTimeStamp,0])
            else:
                print ('Invalid ChgSet')
                input()
        #print (fields)
        return logs


    def getAllLogsGIT(repodir, dolower = False, ToText = False, LoadPushDates = False,g = None):
        g = GIT.G(repodir = repodir)
        return g.getAllLogsMy(dolower = dolower,toText = ToText)
        
        


    
    ##Download a list of bugs. The list should contain the potential bug ids in string format for example ['1','11224','2234', ...]
    ##The process will run in numproc Processes. Set the number according to your needs.
    def Download(lst,type = 'REST'):
        import multiprocessing as mp
        manager = mp.Manager() 
        ##A Shared queue for the processes.        
        q  = manager.Queue()
        for b in lst:
            q.put(b)

        numproc = 1
        
        i = 0
        #if not  os.path.exists(Helpers.bpPathRest):
        #    os.makedirs(Helpers.bpPathRest)
        #if not  os.path.exists(Helpers.bpPath):
        #    os.makedirs(Helpers.bpPath)
        #if not  os.path.exists(Helpers.LOGPagesPath):
        #    os.makedirs(Helpers.LOGPagesPath)
        if numproc>1:

            pass

            #Chck the parallel Code.
            #processes = [mp.Process(target=Helpers.ProcessDownloadQueue,args=(q,i,Helpers.DownloadPage,type)) for i in range(numproc)]
            #for p in processes:
            #    p.start()

            #for p in processes:
            #    p.join()
        else:
            yield Helpers.ProcessDownloadQueue(q,0,Helpers.DownloadPage,type)
    
    def ProcessDownloadQueue(q,pi,func,type = 'REST', bidUrl = False):
        
        while not q.empty():
            print ('In ',pi, ' QSIZE:', q.qsize())
            bid = q.get()
            if bidUrl:
                url = bid
            yield func(bid,pi,type = type, url = url)
        print ('Finished Process...', pi)
    
    ###Type could be PAGE or REST or LOGPAGES
    def DownloadPage(bugid,pi,type = 'REST', dolower = False, url = None):
        tries = 0
        path = ''
        
        if type == 'PAGE':
            path = Helpers.bpPath
            if url == None:
                url = 'https://bugzilla.mozilla.org/show_bug.cgi?id=%s' % bugid

        elif type =='REST':
            path = Helpers.bpPathRest
            if url == None:
                url = 'https://bugzilla.mozilla.org/rest/bug/%s' % bugid 

        elif type == 'LOGPAGES':
            path = Helpers.LOGPagesPath
            if url == None:
                url = 'https://hg.mozilla.org/mozilla-central/rev/%s' % bugid 
        while True:
            try:
                #if not os.path.exists(path+bugid+'.html'):
                    
                f = urllib.request.urlopen(url)
                cont = f.headers.get('content-type')
                cont = cont[cont.rfind('=')+1:]
                data = f.read()
                data = Helpers.ConvertToUTF8(data).encode()
                if dolower:
                    data=data.lower()
                f.close()
                return data
                #f = open (path+bugid+'.html','wb')
                #f.write(data)
                #f.close()
                #return
            except Exception as ex:
                print ('Exception For ', bugid,ex)
                tries+=1
                if tries>100:
                    return None
                time.sleep(1)
                continue

    
    ###Loads the bug file and executes the func function on the data on the generated lxml queryable tree 
    ### the func is intended to be any type of extraction function that works on the lxml tree
    def getLogData(b,func):
        
        try:
            f = open (Helpers.LOGPagesPath+str(b)+'.html','rb')
            data=f.read()
            f.close()
        except Exception as www:
            print (b, 'Load Failed')
            return None
        if len(data)<100:
            raise Exception()

        data = fromstring(data)
        return func(data,b)


    def getPushDate(b):
        
        try:
            f = open (Helpers.LOGPagesPath+str(b)+'.html',encoding='utf8')
            data=f.read(50000)
            f.close()
        except Exception as www:
            print (b, 'Load Failed')
            return 
        try:
            data = data[data.find('<td>push date</td>')+len('<td>push date</td>'):]
            return Helpers.getTimeStamp(data[data.find('<td>')+4:data.find('</td>')])        
        except Exception as ex:
            print (b,data)
            raise ex

    def getBugData(b,func):
        
        try:
            f = open (Helpers.bpPath+str(b)+'.html',encoding='utf8')
            data=f.read()
            f.close()    
        except Exception as www:
            print (b, 'Load Failed')
            
        if len(data)<100:
            raise Exception()

        data = fromstring(data)
        return func(data,b)





    ###Link the bugs with the changesets. This process first reads the commits one by one, then it parses the commit messages. 
    ###If a bug ID is found for a commit, it then creates a row containing the log row information and appends the identified bugs to it, as a comma separated string.

    def GetBC(logs, reexclude, rebugs):
        i = 0
        bc = []

        ##The out variable stores some statistics for the proessed changesets. 
        ##files100 contains a list of the changesets that modify more than a 100 files. 
        ##We assume that such changes could not be bug fixes. Therefore, they are not linked with any bugs.
        ##We assume the bug ids to start from 100. Any number below this is not considered as bug ids

        out = {}
        out['files100'] = []
        out['len3minCount'] = 0
        out['ccommits'] = 0
        out['sbugs'] = 0
        filteredcounts = {} 
        
        for log in logs:
            i+=1

            if isinstance(logs[0], dict):
                locid = log['locid']
                commid = log['cid']
                m = log['m'].lower()
                files = log['files']
                log['files'] = files
            else:
                locid = log[0]
                commid = log[1]        
                m = log[3].lower()
                files = log[Helpers.logFilesIndex].split('---')[:-1]
            mc = m
            
            ##Extract the list of the bugs in the commit message
            bugid,rei,stCode = Helpers.getBugIds(m, reexclude = reexclude, rebugs = rebugs)
            
            ##Collect status code information..

            if stCode==-1:
                if not rei in filteredcounts.keys():
                    filteredcounts[rei]=0
                filteredcounts[rei]+=1
            
            ###The list of the files that are changed. if it is more than a 100, ignore the change.
            
            if len (files)>100:
                out['files100'].append(log)
                
            ###If no bugs are found ignore the change
            #if len(bugid) == 0:
            #    continue
            
            ##Process the list of the extracted bugs for the changeset. Remove numbers less than 100
            cbc = 0        
            bugs = []
            for bug in bugid:
                bug = ''.join([c for c in bug if c>='0' and c<='9'])
                #if len(bug)<3:
                #    out['len3minCount'] += 1
                #    continue
            
                bugs.append(bug)
            #if len(bugs) == 0:
            #    continue

            ##Link the found bugs to the changeset 
            
            if isinstance(log, dict):
                log['bugs'] = ','.join(bugs)
            else:
                log = list(log)
                log.append(','.join(bugs))

            bc.append(log)

            cnt = len(bugs)
            ###Collect the information for changesets containing multiple bugs.
            if cnt>1:
                out['ccommits']+=1
                out['sbugs']+=cnt
            
            if i%10000 == 0:
                print ('BC',i)
        out['filteredcounts'] = filteredcounts
        return bc,out



    def getBugFileData(file):
        
        try:
            f = open (Helpers.bpPath+file,encoding='utf8')
            data=f.read().lower()
            f.close()    
        except Exception as www:
            print (b, 'Load Failed')
            
        if len(data)<100:
            raise Exception()

        data = fromstring(data)
        return Helpers.ExtractBugData(data,b)

    def getTimeStamp(dateStr):
         return parser.parse(dateStr).replace(tzinfo=datetime.timezone.utc).timestamp()

    ###Extract bug data from bug pages. 
    ###Inputs are: data: lxml tree for the page source of the bug
    ###b: the bug id string
    ### Return a dictionary containing various information for the bug b
    def ExtractBugData(data,b):
        
        isvalid = 1

        if len(data.xpath('//*[contains(text(),"you are not authorized to access bug")]'))>0:
            return None,-1
            

        if len(data.xpath('//*[contains(text(),"you must enter a valid bug number!")]'))>0:            
            return None, -2

        bugdata = {}
        if isvalid>0:
            reportDateText = None
            modDateText = None
            try:
                reportDateText = data.xpath("//span[@id='field-value-creation_ts']/span/@title")[0].upper()            
                bugdata['reportDateText'] = reportDateText.replace('\n','').strip()
                
            except Exception as ex: 
                reportDateText = ''
                bugdata['reportDateText'] = reportDateText
                
           
            try:
                bugdata['reportTimestamp'] = Helpers.getTimeStamp(reportDateText)
            except Exception as ex: 
                bugdata['reportTimestamp'] = 99999999999999999999999.0
            
            try:
                modDateText = data.xpath("//span[@id='field-value-delta_ts']/span/@title")[0].upper()
                bugdata['modDateText'] = modDateText.replace('\n','').strip()
            except Exception as ex:
                modDateText = ''
                bugdata['modDateText'] = ''
                

            try:
                bugdata['modTimestamp'] = Helpers.getTimeStamp(modDateText)
            except Exception as ex: 
                bugdata['modTimestamp'] = 99999999999999999999999.0

            bugdata['status'] = data.xpath("//*[@id='field-value-status-view']/text()")[0].replace('\n','').strip()
            bugdata['assignedTo'] = data.xpath("//*[@id='field-value-assigned_to']")[0].text_content().replace('\n','').strip()

            bugdata['reporter'] = data.xpath("//*[@id='field-value-reporter']")[0].text_content().replace('\n','').strip()
            bugdata['bug'] = b

            try:
                bugdata['product'] = data.xpath("//*[@id='product-name']")[0].text_content().replace('\n','').strip()
            except Exception as ex:
                bugdata['product'] = ''


            try:
                bugdata['component'] = data.xpath("//*[@id='component-name']")[0].text_content().replace('\n','').strip()
            except Exception as ex:
                bugdata['component'] = ''


            try:
                bugdata['version'] = data.xpath("//*[@id='field-value-version']")[0].text_content().replace('\n','').strip()
            except Exception as ex:
                bugdata['version'] = ''
            try:
                bugdata['target'] = data.xpath("//*[@id='field-value-target_milestone']")[0].text_content().replace('\n','').strip()
            except Exception as ex:
                bugdata['target'] = ''

            try:
                bugdata['keywords'] = data.xpath("//*[@id='field-value-keywords']")[0].text_content().replace('\n','').strip()
            except Exception as ex:
                bugdata['keywords'] = ''
        

            

        data=None
        return bugdata, 1



    ###Extract patch data from bug pages. 
    ###Inputs are: data: lxml tree for the page source of the bug
    ###b: the bug id string
    ### Return a list of dictionaries containing various information for each path in bug b
    def ExtractBugPatches(data,b):
        
        isvalid = 1

        if len(data.xpath('//*[contains(text(),"you are not authorized to access bug")]'))>0:
            return None,-1
            

        if len(data.xpath('//*[contains(text(),"you must enter a valid bug number!")]'))>0:            
            return None, -2

        patches = []
        if isvalid>0:

            
            attachments= data.xpath("//*[@id='attachments']//tr")  
            if attachments!=None and len(attachments)>0:
                for i,tr in enumerate(attachments):
                    pdata = {}
                    patchRowType = tr.attrib['class'].replace('\n','').strip()

                    patchId = tr.xpath("td[1]/div[1]/a/@href")[0]
                    if len(patchId)>0:
                        patchId = patchId[patchId.rfind('=')+1:].strip()
                    else:
                        print ('PatchID not fount for row ',i,'Bug', b)
                        continue
                    pdata['patchId'] = int(patchId)
                    pdata['bug']=int (b)

                    pdata['patchRowType'] = patchRowType
                    patchText = tr.xpath("td[1]/div[1]/a")[0].text_content().replace('\n','').strip()
                    pdata['patchText'] = patchText
                    try:
                        patchDateText = tr.xpath("td[1]/div[2]/a/span/@title")[0].upper().strip()                        
                    except Exception as ex:
                        patchDateText = ''
                        

                    try:                        
                        patchTimeStamp = Helpers.getTimeStamp(patchDateText)
                    except Exception as ex:                        
                        patchTimeStamp = 99999999999999999999.0


                    pdata['patchDateText'] = patchDateText
                    pdata['patchTimeStamp'] = patchTimeStamp
                    
                    try:
                        commentLink = tr.xpath("td[1]/div[2]/a/@href")[0]
                    except Exception as ex:
                        commentLink = ''
                    pdata['commentLink'] = commentLink
                    
                    patchSize = tr.xpath("td[1]/div[3]")[0].text_content().replace('\n','').strip()
                    pdata['patchSize'] = patchSize

                    author = tr.xpath('td[1]/div[2]/span/div/a')[0].text_content().replace('\n','').strip()
                    pdata['author'] = author
                    patchFlagUsers = [a.text_content().strip() for a in tr.xpath('td[2]/div/div[1]/span')]
                    pdata['patchFlagUsers']=','.join(patchFlagUsers)
                    patchFlagTypes = [a.text_content().strip() for a in tr.xpath('td[2]/div/a')]

                    pdata['patchFlagTypes']=','.join(patchFlagTypes)

                    patchFlagStatus = [a[-1] for a in patchFlagTypes]
                    
                    pdata['patchFlagStatus'] = ','.join(patchFlagStatus)
                    patches.append(pdata)


        return patches, 1
    
    

    def ExtractLogData(data,b):
        
        isvalid = 1

        

        logdata = {}
        if isvalid>0:
            pushdate = None
            adate = None

            try:
                pushdate = data.xpath("//td[text()='push date']/following-sibling::td[1]/text()")[0].upper()
                logdata['pushdate'] = pushdate.replace('\n','').strip()
                
            except Exception as ex: 
                pushdate = ''
                logdata['pushdate'] = pushdate
                
           
            try:
                logdata['pushdateTimestamp'] = Helpers.getTimeStamp(pushdate)
            except Exception as ex: 
                logdata['pushdateTimestamp'] = 99999999999999999999999.0
            

            try:
                adate = data.xpath("//td[@class='date age']/text()")[0].upper()
                logdata['adate'] = adate.replace('\n','').strip()
                
            except Exception as ex: 
                adate = ''
                logdata['adate'] = adate
                
           
            try:
                logdata['adateTimestamp'] = Helpers.getTimeStamp(adate)
            except Exception as ex: 
                logdata['adateTimestamp'] = 99999999999999999999999.0
            

            
        data=None
        return logdata, 1

    
    
    ##Removes the path / and \ characters and replaces them with ---. This way, all the files in all paths could be represented in a single folder.  
    ##Used in Graph generation and Blaming.
    def GetDashedFileName(name):
        return name.replace('/','---').replace('\\','---')

    
    
    def GetGraphFolderPathForType(type='AG'):
        
        return Helpers.mcPath+'Graphs'+type+'/'

    def GetGraphFilePathForType(fid,type='AG'):        
        return Helpers.GetGraphFolderPathForType(type)+str(fid)
    

    
           
    ##do not blame for these nodes
    def ignoreNode(Node):
        if Node.line.strip() in ['','{','}',';']:
            return True
        return False
    
    
    
    
    ##Extract the list of the bugIDS included in the commit message. The search is done by considerig multiple regex strings.
    ## the list however could be filtered by another list of strings that filter non bug fix changesets. Examples are the changesets that contain the merge keywork or no bug pattern.
    #The list of regexes are stored in two variable in Helper functions. 
    ##The filter list is a list of lists. Each list in the list contain one or more filter keywords. if the list contains more than one patterm, the commit is excluded if only all of them are contained. For example
    ##[['no bug','merge'],['crashtest']] This list causes a bug to be excluded if the message contains 'crashtest' or it contains both of 'no bugs' and 'merge'
    ## the lists could be customized based on needs.
    ##checkExclude=False: the messages would not be filtered based on excludekeywords.
    ##Return a list of bug IDS, a reason for exclusion or None if not excluded and a status: -1 if excluded and 0 if not.

    def getBugIds(m,checkExclude=True, reexclude = None, rebugs = None):
        bugid=[]
        if rebugs is None:
            rebugs = Helpers.rebugs
        if reexclude is None:
            reexclude = Helpers.reexclude
        while True:            
            if checkExclude:
                for reitem in reexclude:
                    isOK = False
                    for reelement in reitem:
                        if re.search(reelement,m)==None:
                            isOK = True
                            break
                    if not isOK:
                        return [],str(reitem),-1
            if m.find('issue')>=0:
                print (m)
            indexes = [(re.search(bmarker,m),bmarker) for bmarker in rebugs]
            indexes = [item for item in indexes if item[0]!=None]
            if len(indexes)>0:
                minitem = indexes[0]
            else:
                break

            for item in indexes:
                
                if item[0].start()<minitem[0].start():
                    minitem = item
            if minitem[0].start()<0:
                break
            bugid.append(m[minitem[0].start():minitem[0].end()])
            m = m[minitem[0].end():]
        if len(bugid)>=2:
            #Perform additional checks
            #check for back outs with no mention of back out keyword.
            pass
        return bugid,None,0

    
        
    def isExtValid(file, exts = None):
        if exts is None:
            exts = Helpers.currentExts
        fc = file.lower()
        for c in exts:
            if fc.endswith(c):
                return True
        return False


    def isExtValidCpp(file):
        fc = file.lower()
        for c in Helpers.cppExts:
            if fc.endswith(c):
                return True
        return False

    def GetAllFiles():
        rf = set ()
        if os.path.exists(Helpers.mcPath+'files.txt'):
            f = open (Helpers.mcPath+'files.txt')
            lines = [file.replace('\n','').replace('/','\\') for file in f.readlines()]
            f.close()
            return lines
        logs = Helpers.getAllLogsMy(dolower = False)

        for log in logs:
            files = log[Helpers.logFilesIndex].split('---')
            for file in files:
                rf.add(file)
        files = sorted(list(rf))
        f = open (Helpers.mcPath+'files.txt','w')
        for file in files:
            f.write(file+'\n')
        f.close()
        return files

    


    def ConvertToUTF8(data,file=None):
        
        try:
            data = data.decode('utf8')
        except Exception as eee:
            try:
                enc = chardet.detect(data)
                data = data.decode(enc['encoding']).encode('utf8').decode('utf8')
                print ('decoded in', enc['encoding'], enc['confidence'])
            except Exception as eed:
                data = data.decode('utf8','ignore').encode('utf8').decode('utf8')
                print ('decoded in utf8, ignore Error', file)
                

        return data