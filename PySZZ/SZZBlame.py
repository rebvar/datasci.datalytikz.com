import os
import os.path
import sys
from .Helpers import Helpers
from .HG import HG
from .GIT import G
from .AnnotGraph import AnnotHelpers, Node as ANNOTNODE
import queue
import multiprocessing as mp
import json
import ujson

def traceB(initNodes,Rev,atypes,bFile,revDates,bugReportDate,file,locid,b,revs,indb,fid,Name):

    returnVals = []
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
            lineRev = str(revs[-2].rev)+':'+str(revs[-1].rev)
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
                RevCur = [ANNOTNODE(mdict = uj) for uj in ujson.loads(revs[curId].gDump)]
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
                                    blamedRev  = str(revs[Node.ij[0]-1].rev) + ':' + str(Node.cmId)
                                else:
                                    blamedRev  = '@' + ':' + str(Node.cmId)
                                returnVal = Helpers.bcSep.join([str(locid),b,str(fid)+':'+file,blamedRev+'-'+pNodesIds[nindex], str(lineRev)+'-'+idid,Node.line,line])+Helpers.bcSep+'\n\n\n'
                                yield returnVal
                                #returnVals.append(returnVal)
                            
                            
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
    #return returnVals



def Blame2(q,procIndex,bugDates,logDates,removeStopTypes = ['+'],updateStopTypes = ['+','*'],indb = True,fileIDs = {}, exts = None, graphs = None):
    
    if exts == None:
        exts= Helpers.currentExts
    #Counter for printing purposes
    i=0
    #The blames for the removed lines are stored in this file
    #while not q.empty():
    for item in q:
        #Get the next item from the queue. The items in the queue need to have few information. 
        #locid : Changeset ID for which we are trying to find the changesets to blame. The added, removed and updated lines are insepected for this changeset. 
        #BugId : The ID of the bug which is discovered from the changeset message and is linked and validated from the issue repository system.
        #Files : A list if the files that are added, removed or modified in changeset locid. 
         
        #item = q.get()
        
        i+=1
        #Extract locid
        locid = item.cid
        
        #progress printing
        #print ('In : '+cmpName+' ('+str(procIndex)+') :Iteration',i, '  For',locid, 'Remaining:', q.qsize())
        

        #BugID
        b = item.bugs        

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
            files=json.loads(item.files)
            
            ##For each file in changeset locid, load its revisions,saved before through the graph generator module.
            for file in files:
                                                
                if not Helpers.isExtValid(file, exts):                    
                    continue
                
                fo = file
                fid = fileIDs[file]
                ##The list of the revisions for the file. Ignore changesets after locid. They are not required as we track the changes backward.
                revs = [g for g in graphs if g.repoFileId == fid]


                ##Exception Happens when file is completely removed. If that is the case, we can track all of its line.
                ##I have not implemented this at the moment. To do that, the previsous revision should be loaded, and all its lines be added to removedLines 
                ## and updated and added Arrays should be empty.

                try:
                    index = -1
                    for revIndex,r in enumerate(revs):
                        if r.rev == locid:
                            index = revIndex
                    
                    if index<0:
                        raise Exception('Index -1')                     
                    
                    revs = revs[:index+1]
                except Exception as eeee:
                    print ('Ignored In : '+str(eeee)+' ('+str(procIndex)+') :Iteration',i, '  For file ',file,' and ',locid,' Rev Not Found in:',revs)
                    revs = None

                
                #file = Helpers.GetDashedFileName(file)
                if revs!=None:


                    ## For the filtering purposes, described before for bug date, the date of the chnages to file are extracted. If the dates for all changes are not available, 
                    ## Use integers as dates. Additionally set the bugreport date to zero as no filtering based on date is possible
                    print ('In :  ('+str(procIndex)+'): Processing ',file, len(revs))
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
                            RevL =  [ANNOTNODE(mdict = uj) for uj in ujson.loads(revs[irevl].gDump)]
                        if removeStopTypes!=None:
                            RevBL = [ANNOTNODE(mdict = uj) for uj in ujson.loads(revs[irevbl].gDump)]
                        

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
                            for tritem in traceB(removedNodes,RevBL,removeStopTypes,None,revDates,bugReportDate,file,locid,b,revs,indb = indb,fid=fid,Name = None):
                                yield tritem
                        RevBL = None
                        ##track the updated lines
                        if updateStopTypes!=None:
                            for tritem in traceB(changedNodes,RevL,updateStopTypes,None,revDates,bugReportDate,file,locid,b,revs,indb = indb,fid=fid,Name=None):
                                yield tritem
                        RevL = None

                        ##No tracking for added lines.

                        removedNodes = None
                        changedNodes = None
                        addedNodes = None

                    revDates = None
                
                revs = None

        
        #print ('-----------------------------------------')
    print ('PR ('+str(procIndex)+'): Finished.')
    
