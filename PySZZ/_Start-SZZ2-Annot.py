import os
import os.path
import sys
from .Helpers import Helpers
from .DBHelper import DBHelper
from .HG import HG
from .AnnotGraph import AnnotHelpers
import queue
import multiprocessing as mp

#The graph type

##Log the stdout output to a file plus showing it in the command prompt window.
class Logger(object):
    def __init__(self,fid=0, BlameFol=""):
        self.terminal = sys.stdout
        self.log = open(BlameFol+"SZZAnnotOut"+str(fid)+".txt", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)  
        self.log.flush()    
    def flush(self):
        pass





def traceB(initNodes,Rev,atypes,bFile,revDates,bugReportDate,file,locid,b,revs,indb,fid,Name):

    ##For each starting line (removed or updated in Rev)
    for idid in initNodes:
        ##Extract the revision index and line number
        dpars = 0
        oid = idid.split('-')
        #Revision Index
        id1 = int(oid[0])
        #Line number
        id2 = int(oid[1])                    
        ##If there is a possibility of going back.                    
        if id1>=0:
            #Keep track of the cur Revision.
            curId = id1
            #The changed or removed line
            Node = Rev[id2]

            #Line text
            line = Node.line
            isRemoval = False
            #Line revision ID
            #lineRev = Node.cmId
            lineRev = str(revs[-2])+':'+str(revs[-1])
            #if lineRev.find(';')>0:
            #    isRemoval = True
            #    lineRev = lineRev[lineRev.find(';')+1:]
            #else:
            #    lineRev = 
            #Extract the set of nodes that have a link to the current node from the previous revision. The first level suspects.
            p={lnk for lnk in Node.Links if lnk.startswith(str(curId-1)+'-')}
                                
            curId-=1
                                
            parentFound = False
            RevCur=None
            pNodes = []
            pNodesIds = []
            ##Until parents are found or no more revision is available :
            ##We used parents since in some implemetations, a line could have multiple parents. This is true for the conservative implementation.
            while not parentFound and curId>=0:
                RevCur = None
                ##Load the revision to be inspected.
                RevCur = AnnotHelpers.loadRevision(fid,curId,type=Name,indb = indb)
                ##Parent Nodes and Parent Node IDS (INDEX-LINE_NO)
                pNodes.clear()
                pNodesIds.clear()
                for pi in p:
                    pi = pi.split('-')
                    id1 = int(pi[0])
                    id2 = int(pi[1])
                    
                    Node= RevCur[id2]
                    pNodes.append(Node)
                    pNodesIds.append("%d-%d"%(id1,id2))
                pNew = None
                pNew = set()
                ##Check for each parent node, 
                
                                    
                for nindex,Node in enumerate(pNodes):
                    typeFound = False   
                    typeDateMatchFound = False 
                    ##if the node type (addition or update) matches one of the input types passed through atypes list. A match is Found.
                    ##If we have match, check for the validity based on the dates. If a bug date is supplied, the filtering is perfomed. 
                    ## Otherwise, stop at the first match for the current parent.
                    for type in atypes:
                        
                        if Node.type.find(type)>=0:
                            typeFound = True
                            if Node.type.find('-')>=0:
                                raise Exception("Invalid Link. - Can not have link to next level")

                            if revDates[Node.ij[0]]<bugReportDate or bugReportDate == 0:
                                typeDateMatchFound = True
                                dpars+=1
                                ##Save the found match for later parsing.   
                                blamedRev = ''        
                                if Node.ij[0]>0:
                                    blamedRev  = str(revs[Node.ij[0]-1]) + ':' + str(Node.cmId)
                                else:
                                    blamedRev  = '@' + ':' + str(Node.cmId)
                                bFile.write(Helpers.bcSep.join([str(locid),b,str(fid)+':'+file,blamedRev+'-'+pNodesIds[nindex], str(lineRev)+'-'+idid,Node.line,line])+Helpers.bcSep+'\n\n\n')
                            
                            
                     ##If a match is not found (the node is not an update or an addition for updated or an addition for removed)
                     ##Or the parent date is greater than the supplioed bugdate, track the changes further by adding the links from this node to the previous revision.                      
                    if not typeFound or (typeFound and not typeDateMatchFound):
                        
                        for pn in [lnk for lnk in Node.Links if lnk.startswith(str(curId-1)+'-')]:
                            pNew.add(pn)

                ##If there are anymore parents: Repeat. Else the tracking is finished.
                if len(pNew)>0:
                    
                    p = pNew
                else:
                    break
                curId-=1

            if curId==-1:
                break
        elif id1 == 0:
            pass
            ##Do not do anything. No tracking is possible
        else:  
            ##Can not have negative IDS.                                
            raise Exception('Error:Neg ID-'+str(idid)+'-'+file+'-'+len(revs))



def Blame2(q,procIndex,bugDates,logDates,removeStopTypes = ['+'],updateStopTypes = ['+','*'],indb = True,fileIDs = {},BlameFol="",Name="",cmpName=""):
    
    sys.stdout = Logger(fid=procIndex+1,BlameFol = BlameFol)
    
    #Counter for printing purposes
    i=0
    #The blames for the removed lines are stored in this file
    rbFile = None
    ubFile = None
    if removeStopTypes!=None:
        rbFile = open(BlameFol+'RemovedBlames-'+str(procIndex)+'.txt','w',encoding='utf8')
    #The blames for the update lines are stored in this file
    if updateStopTypes!=None:
        ubFile = open(BlameFol+'UpdatedBlames-'+str(procIndex)+'.txt','w',encoding='utf8')
    #Both files are specific to Process procIndex. Two files are created for each process number passed to the function.
   
    
    #Read from the shared Queue for all processes. Until the queue is empty.    
    while not q.empty():

        #Get the next item from the queue. The items in the queue need to have few information. 
        #locid : Changeset ID for which we are trying to find the changesets to blame. The added, removed and updated lines are insepected for this changeset. 
        #BugId : The ID of the bug which is discovered from the changeset message and is linked and validated from the issue repository system.
        #Files : A list if the files that are added, removed or modified in changeset locid. 
         
        item = q.get()
        
        i+=1
        #Extract locid
        locid = item['locid']
        
        #progress printing
        print ('In : '+cmpName+' ('+str(procIndex)+') :Iteration',i, '  For',locid, 'Remaining:', q.qsize())
        

        #BugID
        b = str(item['bug'])
        

        if b!=None:
            ## The blaming algorithm, starts from changeset locid tracks the history of the changes until a modification (for updates) or 
            ## an addition (for removal and updates are found). Since not all changes are necessarily responsible for introducing the bug, certain changes are ignored.
            ## Specifically, changes made after the report date of the bug can not be responsible for causing the bug. Therefore, they are ignored based on
            ##  the dates for the changes and bugs. The utc timestamp is expected for both dates. If a date for a bug is not available, no filtering based on date is performed




            ##If bug date is available, extract the bug date, set to zero, otherwise.
            if bugDates!=None:
                bugReportDate = bugDates[b]
            else:
                bugReportDate = 0

            ## Scan the files that are present in the changeset.
            files=item['files'].split('---')[:-1]
            
            ##For each file in changeset locid, load its revisions,saved before through the graph generator module.
            for file in files:
                
                
                
                ##Only track chnages for valid extensions: C/C++/CC/HH/H at the moment. 
                ##Other files could be added to the list if their graphs are generated.
                if not Helpers.isExtValidCpp(file):
                    print ('In : '+cmpName+' ('+str(procIndex)+'): Ignoring ',file)
                    continue
                
                fo = file
                fid = fileIDs[file.replace('/','\\')]
                ##The list of the revisions for the file. Ignore changesets after locid. They are not required as we track the changes backward.
                revs = AnnotHelpers.loadRevsList(fid,type = Name,indb = indb)


                ##Exception Happens when file is completely removed. If that is the case, we can track all of its line.
                ##I have not implemented this at the moment. To do that, the previsous revision should be loaded, and all its lines be added to removedLines 
                ## and updated and added Arrays should be empty.

                try:
                    index = revs.index(int(locid))
                    revs = revs[:index+1]
                except Exception as eeee:
                    print ('Ignored In : '+cmpName+' ('+str(procIndex)+') :Iteration',i, '  For file ',file,' and ',locid,' Rev Not Found in:',revs)
                    revs = None

                
                #file = Helpers.GetDashedFileName(file)
                if revs!=None:


                    ## For the filtering purposes, described before for bug date, the date of the chnages to file are extracted. If the dates for all changes are not available, 
                    ## Use integers as dates. Additionally set the bugreport date to zero as no filtering based on date is possible
                    print ('In : '+cmpName+' ('+str(procIndex)+'): Processing ',file, len(revs))
                    if logDates!=None:
                        revDates = [logDates[str(revs[i])] for i in range(len(revs))]
                    else:
                        revDates = [i+1 for i in range(len(revs))]
                        bugReportDate = 0
                    
                    ## If this is the first instance which the file appears, no tracking of the changes are possible as only one version of the source code exists.
                    ## If All the changes are additions, the blaming does not work.
                    if len(revs)>1:   
                        
                        ##Index of last revision             
                        irevl = len(revs)-1
                        ##Index of revision before the last
                        irevbl = len(revs)-2
                        
                        ## Load the graph portion for the last two revisions. RevL, contains the graph structure for the last revision 
                        ## in revs (not neccessarily the last revision of the file as the revisions after locid are not of any use for the current blaming process.). 
                        ## The file takes three parameters. Name of the file, revision index amd type of the Graph.
                        RevL = None
                        RevBL = None
                        if updateStopTypes!=None:
                            RevL = AnnotHelpers.loadRevision(fid,irevl,type = Name,indb = indb)
                        if removeStopTypes!=None:
                            RevBL = AnnotHelpers.loadRevision(fid,irevbl,type = Name,indb = indb)
                        

                        ##Extract the added, removed and updates lines of code. Added and updatesd lines are located in RevL. Removed lines can be found in RevBL.
                        ##
                        removedNodes = []
                        changedNodes = []
                        addedNodes = []
                        ##Search RevBL for removed lines
                        if RevBL!=None:
                            for j in range(len(RevBL)):
                                if RevBL[j].type.find('-')>=0:
                                    if not Helpers.ignoreNode(RevBL[j]):
                                        removedNodes.append("%d-%d"%(irevbl,j))
                        
                        #Search RevL for updated lines
                        if RevL!=None:
                            for j in range(len(RevL)):
                                if RevL[j].type.find('*')>=0:
                                    if not Helpers.ignoreNode(RevL[j]):
                                        changedNodes.append("%d-%d"%(irevl,j))
                            #Search RevL for added lines
                            for j in range(len(RevL)):
                                if RevL[j].type.find('+')>=0:
                                    if not Helpers.ignoreNode(RevL[j]):
                                        addedNodes.append("%d-%d"%(irevl,j))
        
                        ##track the Removed lines
                        if removeStopTypes!=None:
                            traceB(removedNodes,RevBL,removeStopTypes,rbFile,revDates,bugReportDate,file,locid,b,revs,indb = indb,fid=fid,Name = Name)
                        RevBL = None
                        ##track the updated lines
                        if updateStopTypes!=None:
                            traceB(changedNodes,RevL,updateStopTypes,ubFile,revDates,bugReportDate,file,locid,b,revs,indb = indb,fid=fid,Name=Name)
                        RevL = None

                        ##No tracking for added lines.

                        removedNodes = None
                        changedNodes = None
                        addedNodes = None

                    revDates = None
                
                revs = None

        
        #print ('-----------------------------------------')
    print ('PR ('+str(procIndex)+'): Finished.')
    if rbFile!=None:
        rbFile.close()
    if ubFile!=None:
        ubFile.close()

if __name__ == '__main__':

    f = open('q1.csv')
    comps = f.readlines()[1:]
    f.close()
    for i in range(len(comps)):
        comps[i] = comps[i].split(',')[0].strip()
    #comps.reverse()
    print (len(comps))
    input('Press a key to start.....')
    curPrcs = []
    comps = comps[102:]
    for cmpName in comps:
        
        #cmpName = 'graphics' #widget
        #cmpName = cmpName.lower()
        Name = 'KIM-No-Minify-DB'
        num = '---ND---'+cmpName.replace(': ','-').replace(' ','-').replace(':','-').replace('/','-')+'---Update+starDel+star'
        

        ##Dir Check.
        curDir = os.getcwd()
        BlameFol = curDir+'/Blames'+Name+num+'/'
        if not os.path.exists(BlameFol):
            os.makedirs(BlameFol)
    
        sys.stdout = Logger(fid=0,BlameFol=BlameFol)
        print ("Started Job For Component: " +cmpName)
        

        uc,ub = set(),set()
        bc = None


        ##Stores changeset and bug information
        dbh = DBHelper()
    
        ##For shared variables for the processes.
        manager = mp.Manager()
        ##Shared dictionaries for the bugs and logs dates
        logDates = manager.dict()
        bugDates = manager.dict()


        ##Read all the logs
        logs,logcolnames = dbh.GET_ALL()
        ##If no log, first generate the logs.
        if len(logs) == 0:
            logs = Helpers.getAllLogsMy(dolower=False,ToText = False)
            dbh.CleanInsertMany(datarows = logs,keys = logcolnames,table = 'LOGS')
            logs,logcolnames = dbh.GET_ALL(table='LOGS')
             
        print ('Count changesets:',len(logs))

        ##Extract the logdates. Store them in a dictionary for fast access.
        if len(logDates.keys())<=0:
            for bci in logs:
                logDates[str(bci[0])]=bci[logcolnames.index('timestamp')]
                #uc.add(str(bci[0]))

        ##Read the linked cchangeset and bugs information. If does not exist, generate it.
        forceRegenerateBC=False

        bc,bccolnames = dbh.GET_ALL('BC')
    
        if len(bc) == 0 or forceRegenerateBC:
            bc,out = Helpers.GetBC(logs)
            print(out['ccommits'],out['sbugs'],out['len3minCount'])
            print(out['filteredcounts'])
            dbh.CleanInsertMany(datarows = bc,keys = bccolnames,table='BC')
     
        if len(bc) == 0:
            bc,bccolnames = dbh.GET_ALL(table='BC')

        print ('BC Count:',len(bc))

        print(len(uc),len(ub))
        ub = set()
        uc = set()
    


        i = 0
    
        print ('LogDates',len(logDates))
    
    
        ##Filter the bugs based on product and component. This in turn filters the changesets. USE 'like' and '='
        ##Example for Audio/Video
        ##select bug,reportTimestamp,status,product,component from VALIDBUGS where lower(status) like '%fixed%' and (lower(product)='core') and (lower(component) like '%video%' or lower(component) like '%audio%')
   


    
        #quer = "select "+','.join(keys)+" from VALIDBUGS where status like '%fixed%' and (product = 'Core' or product='core')"
        keys = ['bug','reportTimestamp','status','product','component']
        vbugs,vbugscolnames = dbh.GET_ALL(table='VALIDBUGS',fields=keys,Where="  where lower(status) like '%fixed%' and (lower(product)='core') and (lower(component) like '"+cmpName+"')")
        ##Generate the bugdates store them in a dict for fast access.
        for line in vbugs:
            
            b = str(line[0])
            
            bugDates[b] = line[1]
            ub.add(b)
            
        print (len(ub),len(vbugs))
    
        ##Create a shared queue containing the commit bug file information.  
        q = manager.Queue()
        ##The changesets might be linked to multiple bugs. Separate them and only keep the valid bugs. 
        bcnew = []
        locidindex = bccolnames.index('locid')
        filesindex = bccolnames.index('files')
        bugsindex = bccolnames.index('bugs')


        for bci in bc:
            bugids = bci[bccolnames.index('bugs')].split(',')
            for bug in bugids:
                if bug in ub:
                    bcnew.append({'locid':bci[locidindex] , 'files':bci[filesindex], 'bug':bug})
        bc = bcnew[:]
        print ('BCNEW: ',len(bcnew))

        bcnew = []
    
        ##Filter the bug fixes based on their files extensions. 

        #for bci in bc:
        #    files = bci[Helpers.logFilesIndex].split('---')[:-1]
        #    allvalidcpp = True
        #    for file in files:
        #        if not Helpers.isExtValidCpp(file):
        #            allvalidcpp = False
        #            break
        #    if allvalidcpp:
        #        bcnew.append(bci)
        #bc = bcnew
        #print ('BCNEW After Files: ',len(bcnew))


        ##print some statistics
        ub =set()
        uc = set()
        for bci in bc:
            q.put(bci)
            ub.add(bci['bug'])
            uc.add(bci['locid'])
        bcnew = None
        bc = None

        files,fcols =dbh.GET_ALL(table='FILES',fields=['ROWID','file'])

        if len(files) ==0:

            files = Helpers.GetAllFiles()
            dbh.CleanInsertMany(datarows = files,keys=['file'],table='FILES')
    
        files,fcols =dbh.GET_ALL(table='FILES',fields=['ROWID','file'])
        fileIDs = manager.dict()
        for row in files:
            fileIDs[row[1]] = row[0]
    
        print ('UNIQUE BUGS', len(ub))
        print ('UNIQUE Commits', len(uc))
        print ('QSIZE',q.qsize())
    
        #input('Press  a key to start...')
        logs = None
        ub = None
        uc= None
        dbh.close()
        ##Start blaming with numproc Processes.
        numproc = 14
        indb = True
        
    
        print (cmpName, cmpName.replace(' ','').replace(':','-'))

        #Blame2(q,i,bugDates,logDates,['+','*'],['+','*'],indb,fileIDs)

        processes = [mp.Process(target=Blame2,args=(q,i,bugDates,logDates,['+','*'],['+','*'],indb,fileIDs,BlameFol,Name,cmpName)) for i in range(numproc)]
        
        for p in processes:
            p.start()
            curPrcs.append(p)

        if len(curPrcs)>=0:
            for p in curPrcs:
                p.join()
            curPrcs = []
    
        print ("Finished Job For Component: " +cmpName)

    if len(curPrcs)>=0:
        for p in curPrcs:
            p.join()
        curPrcs = []
    