from .HG import HG
from .GIT import G
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import difflib
from .Helpers import Helpers
import clang.cindex
import pickle
import os
import shutil
from scipy.optimize import linear_sum_assignment
import numpy as np
import Levenshtein
import datetime
import dateutil
import dateutil.parser as parser
import time
import re
import pickle
from .DBHelper import DBHelper
import ujson

class AnnotHelpers():

    ##Create a list of Node class instances. One per line of code. 
    def createRevNodes(alines,file,r,i,revs,authors, minifyFunc=None):
        revNodes = []
        

        ##Do minification/formating based on the file extension.
        if minifyFunc!=None:
            alines = minifyFunc(alines.encode('utf8'),None,alines.split('\n'))
        ##Split the lines of code.
        alines = alines.split('\n')
        if alines==['']:
            alines = []
        
        countLines = len(alines)
         ##Assign each line to a Node object and append it to the list. if the revision index is 0, the node types are + since this is
         ##the earliest available revision. ij stores the revisionindex-lineno pair used by blaming algorithm   
        for j in range(countLines):
            node = Node()
            if i == 0:
                node.author=authors[0]
                node.cmId=str(revs[0])
                node.type='+'
            node.ij = [i,j]
            node.line = alines[j]
            revNodes.append(node)
        ##Return the minified/formated/unchanged source and the generated graphs.    
        return revNodes,alines
                
        

    ##Generate hunks from the output of the Unified diff - difflib from python is used in this case. However, this is compatible with any standard difflib output.
    ##The function expects only one large hunk with as much context as possible. It then splits the large hunk into smaller hunks and removes the context lines.
    ##We implemented this as the unidiff generated some unexpected outputs. For example the start point of the first hunk for both left and right should always be equal (not the case for some with HG diff).

    def getHunks(hunkLines,sources=None):
        j=0
        ##Hunk line starting with @@ representing the starting point in both versions of the source
        hunkLineFound = False
        while j <len(hunkLines):
            line = hunkLines[j]
            if line.startswith('@@'):
                hunkLineFound = True
                break
            j+=1
        if hunkLineFound:
            ##Split and parse the hunk line. Since we always include all the context, the lstart and rstart vars must always be 0 when initialized with the hunk line data.
            ##An error otherwise.
            hln = hunkLines[j]
            hln = hln[hln.find('@@')+2:hln.rfind('@@')].strip().split(' ')
                                        
            lstart = abs(int(hln[0].split(',')[0]))-1
            rstart = abs(int(hln[1].split(',')[0]))-1
            if lstart>0 or rstart>0:
                print ('Error in hunk start')
                raise Exception("Invalid Hunk starts")
                
            llen = 0
            rlen = 0
            cnC = 0
            acnC = 0

            ##Order of the addition or deletion for the lines in any hunk.
            order = ''
            ##List to store the identified smaller hunks.
            nhunks = []
            ##Data after the hunk line: Source lines, +,-, ' '(context)                    
            h = hunkLines[j+1:]
            ##List of sources for source ('-', ' ') and target ('+',' ')
            src = [t[1:].strip() for t in h if t.startswith(' ') or t.startswith('-')]
            tgt = [t[1:].strip() for t in h if t.startswith(' ') or t.startswith('+')]


            
            #Cunks are separated by context lines. If a context line is observed and either of llen (changes in source) or rlen (chnage in target) are not zero,
            #A hunk is found. if llen>0 and rlen>0: this is a potential update. if llen>0 this is removal. if rlen>0 this is addition. else ignore the context, but account for it in the line couting.
            #The case for the update is decided after further investigation is the revision linker in the graph builder functions.

            for indexi,hi in enumerate(h):
                        
                if hi.startswith(' ') and (rlen<=0 and llen<=0):
                    cnC+=1
                if hi.startswith('+'):
                    rlen+=1
                    order+='+'
                if hi.startswith('-'):
                    llen+=1
                    order+='-'
                ##For the last hunk, check for the end of file and context ' ' as the last line of the diff might not be a context.
                ##If OK, generate a dict of the values lstart, rstart, llen,rlen, srclines, rgtlines and the order and append it to the return lit.
                ##Continue search for additional hunks  
                if (hi.startswith(' ') or indexi==len(h)-1) and (rlen>0 or llen>0):
                    hni = {}
                    lstart+=cnC
                    rstart+=cnC
                    hni["lstart"] = lstart
                    hni["rstart"] = rstart
                    lstart+=llen
                    rstart+=rlen
                    hni["llen"] = llen
                    hni["rlen"] = rlen
                            
                    sourceCode = '\n'.join(src[cnC:cnC+llen])
                    targetCode = '\n'.join(tgt[cnC:cnC+rlen])
                    hni['slines'] = sourceCode
                    hni['tlines'] = targetCode
                    
                            
                    src = src[cnC+llen:]
                    tgt = tgt[cnC+rlen:]                                
                    hni['order'] = order

                    llen = 0
                    order = ''
                    rlen = 0
                    acnC+=cnC
                    cnC=1
                            
                    nhunks.append(hni)
            ##return identified hunks
            return nhunks

        ##No hunks identified
        return None
        
    
    
    #Generate one large hunk from two versions of the source code in the sources list                                        
    def getRawHunks(sources):
        if sources!=None:
            n = n=max(len(sources[0]),len(sources[1]))
            h = [pudiline for pudiline in difflib.unified_diff(sources[0],sources[1],n = n,lineterm="")]
            #return the diff output
            return h

        #return None. No diff.
        return []


    ###########Load Functions
    #Load Entire Annot Graph. Rarely used
    def LoadAnnotGraph(fid,type = 'AG', indb = True):
        #Expected form of file name:
        #The dahsed type of filename is used to show the filename as well as its path on disk. This way, all the graphs for all files could be stored in just one folder.         
        #Path= GraphsType/ for example GraphsKIM/
        
        if indb:
            dbh = DBHelper('Graphs'+type+'/'+str(fid),setup=False)
            data,datacols = dbh.GET_ALL(table = 'RevisionData')
            revs = []
            Nodes = []
            #Load individual revisions
            for i in range(len(revs)):                                
                Nodes.append([Node(ujsdict = uj) for uj in ujson.loads(data[i][datacols.index('gDump')])])
                revs.append(data[i][datacols.index('revIndex')])
            return Nodes,revs
            
        else:
    
            fname = Helpers.GetGraphFilePathForType(fid,type)
            if not os.path.exists(fname+'===Revs'):
                return None, None
        
            #Load the revision list for the file
            revs = pickle.load(open(fname+'===Revs','rb'))
            Nodes = []
            #Load individual revisions
            for i in range(len(revs)):
                Nodes.append(pickle.load(open(fname+'===Rev-'+str(i),'rb')))
            return Nodes,revs

   
    ##Load the graph for a single revision. It is a list of Node classes stored as binary.
    ## See the comments for LoadAnnotGraph function for the rest of the function
    def loadRevision(fid,i,type = 'AG',indb = True):
        pass        
        
        return [Node(mdict = uj) for uj in ujson.loads(data[0][datacols.index('gDump')])]
                                
        
    ##Load the revision list for a file
    ## See the comments for LoadAnnotGraph function for the rest of the function
    def loadRevsList(fid,type = 'AG',indb = True):
        
        if indb:
            dbh = DBHelper('Graphs'+type+'/'+str(fid),setup=False)
            data,datacols = dbh.GET_ALL(table = 'RevisionData', fields=['revID'])
            dbh.close()
            return [d[0] for d in data]

        fname = Helpers.GetGraphFilePathForType(fid,type)
        if not os.path.exists(fname+'===revs'):            
            return None
        revs = pickle.load(open(fname+'===revs','rb'))
        return revs

    def loadPickle(fid,type = 'Revs',sourceFolder='',indb = True):
                
        fname = Helpers.mcPath+sourceFolder+type+"==="+str(fid)
        if not os.path.exists(fname):            
            return None
        obj = pickle.load(open(fname,'rb'))
        return obj

     ##Load the author list for a file
    ## See the comments for LoadAnnotGraph function for the rest of the function
    def loadAuthors(fid,type = 'AG',indb = True):
        
        if indb:
            dbh = DBHelper('Graphs'+type+'/'+str(fid),setup=False)
            data,datacols = dbh.GET_ALL(table = 'RevisionData', fields=['author'])
            dbh.close()
            return [d[0] for d  in data]

        fname = Helpers.GetGraphFilePathForType(fid,type)
        if not os.path.exists(fname+'===Authors'):
            
            return None

        auth = pickle.load(open(fname+'===Authors','rb'))
        return auth



##Source code parsing and minification class
class SourceCodeHelpers:
    def Minify1 (s,idx,sc):
        ##Clang cindex instance
        if idx == None:
            idx = clang.cindex.Index.create()
        ##Perform the tokenization in a temp file.
        tu = idx.parse('tmp.cpp', unsaved_files=[('tmp.cpp', s)],  options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
        ##All Tokens
        toks = [t for t in tu.get_tokens(extent=tu.cursor.extent)]
        ns = ''
        pdstarted = False
        pdline = -1
        pre = ''

        ##Do for each token t
        for i,t in enumerate(toks):
            ##Ignore comments.
            if t.kind == clang.cindex.TokenKind.COMMENT:
                continue
            else:
                ##If not comment
                ##If we are in a preprocessor directive (such as defines)
                if pdstarted:
                    if True:
                        ##process multiline defines and other preprocessor directives. The lines end with \\ for multiline instances.
                        if t.location.line!=pdline:
                            if sc[pdline].endswith('\\'):
                                pdline = t.location.line
                            else:
                                pdstarted = False
                                pdline = -1
                                ns+='\n'
                        ##If # is identified right after a previous # command. Such as #endif after #define
                        if t.kind == clang.cindex.TokenKind.PUNCTUATION and t.spelling == '#':
                            pdstarted = True
                            pdline = t.location.line
                            ns+='\n'
                            ns+=t.spelling
                            continue
                        #Format the tokens inside preprocessor directives such as defines. If punctuation or literal, ...

                        #The last two conditions could change pdstarted. It means that the preprocessor directive could have ended in the first
                        #But the second could start it again. So check for its value again and process the current token accordingly.
                        if pdstarted:
                            if t.kind == clang.cindex.TokenKind.PUNCTUATION and t.spelling == ';':
                                ns+=';\\\n'
                            elif t.kind == clang.cindex.TokenKind.PUNCTUATION and t.spelling == '{':
                                ns+='\\\n{\\\n'
                            elif t.kind == clang.cindex.TokenKind.PUNCTUATION and t.spelling == '}':
                                ns+='\\\n}\\\n'
                            else:
                                if t.kind == clang.cindex.TokenKind.PUNCTUATION:
                                    ns+=t.spelling
                                else:
                                    if i>0 and toks[i-1].kind!= clang.cindex.TokenKind.PUNCTUATION:
                                        ns+=' '+t.spelling
                                    else:
                                        ns+=t.spelling
                        else:                                                                                   
                            if t.kind == clang.cindex.TokenKind.PUNCTUATION:
                                ns+=t.spelling
                            else:
                                if i>0 and toks[i-1].kind!= clang.cindex.TokenKind.PUNCTUATION:
                                    ns+=' '+t.spelling
                                else:
                                    ns+=t.spelling
                else:
                    ##If not a preprocessor environment is not observed or it has finished.
                    if t.kind == clang.cindex.TokenKind.PUNCTUATION and t.spelling == ';':
                        ns+=';\n'
                    elif t.kind == clang.cindex.TokenKind.PUNCTUATION and t.spelling == '{':
                        ns+='\n{\n'
                    elif t.kind == clang.cindex.TokenKind.PUNCTUATION and t.spelling == '}':
                        ns+='\n}\n'
            
                    elif t.kind == clang.cindex.TokenKind.PUNCTUATION and t.spelling == '#':
                        ##Check if a new preprocessor directive is starting
                        ns+='\n#'
                        if pdstarted:
                            print ('Error pdstart')
                            raise Exception('No two preprocessors in a single line')

                        pdstarted = True
                        pdline = t.location.line
                    else:
                        ##Process literals and keywords and punctuations whcih are not a part of the special cases considered above and not is a preprocessor environment.

                        if t.kind == clang.cindex.TokenKind.PUNCTUATION:
                            ns+=t.spelling
                        else:
                            if i>0 and toks[i-1].kind!= clang.cindex.TokenKind.PUNCTUATION:
                                ns+=' '+t.spelling
                            else:
                                ns+=t.spelling

        ##Delete empty lines and return the source
        return '\n'.join([line for line in ns.split('\n') if len(line)>0])

    def Minify2 (s,idx,sc = None):
        
        s=s.replace('\\\n',' CONTINNEWLINEX\n')

        if idx == None:
            idx = clang.cindex.Index.create()
        
        ##Perform the tokenization in a temp file.
        tu = idx.parse('tmp.cpp', unsaved_files=[('tmp.cpp', s)],  options=clang.cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD)
        ##All Tokens
        toks = [t for t in tu.get_tokens(extent=tu.cursor.extent)]
        ns = ''
        curLine = 1
        lines = s.split('\n')
        ##Do for each token t
        for i,t in enumerate(toks):
            ##Ignore comments.
            if t.kind == clang.cindex.TokenKind.COMMENT:
                continue
            else:               
                while curLine<t.location.line:
                    #if lines[curLine].replace('\n','').endswith('\\'):
                    #    ns+='\\\n'
                    #else:
                    #    ns+='\n' 
                    ns+='\n'
                    curLine+=1
                if i>0 and toks[i-1].kind!= clang.cindex.TokenKind.PUNCTUATION:
                    ns+=' '
                
                if t.spelling == 'CONTINNEWLINEX':
                    ns+='\\'
                else:
                    ns+=t.spelling

        ##Delete empty lines and return the source
        return ns



#Text Similarity Measurement Class

class SOper:
    ##Similarity Score based on the SequenceMatcher from difflib
    def simialrityScore(a,b,ignorecase=True):
        if ignorecase:
            a = a.lower()
            b = b.lower()
        seq=difflib.SequenceMatcher(a=a, b=b)
        return seq.ratio()
    ##Similarity Score based on the Levenshtein.ratio from Levenshtein
    def similarityScoreLev(a,b,ignorecase=True):
        if ignorecase:
            a = a.lower()
            b = b.lower()
        seq=Levenshtein.ratio(a, b)
        return seq



##Node Class. One for each line in each revision of each file
class Node:
    def __init__(self,mdict= None,ujsdict = None):
        if mdict!=None:
            self.__dict__=mdict
        elif ujsdict!=None:
            self.__dict__ = ujson.loads(ujsdict)
        else:
            self.Links = []
            self.author = ''
            self.type = ''
            self.cmId = ''
            self.line = ''
            self.ij = None
        
class GraphBuilder:

    def __init__(self,repodir = None,indb = True,dbName = 'GraphsKIM', repoType = 'GIT',useclang = False):
        
        ##Threshold used for SequenceMatcher
        self.scoreThreshold = 0.80
        #Cindex for the class
        if useclang:
            self.idx = clang.cindex.Index.create()
        else:
            self.idx = None
        self.indb = indb
        if self.indb:
            
            self.keysrdLst = ['revIndex','revID','author','gDump']
            
            self.keysrd = ','.join(self.keysrdLst)
            
        #Mercurial
        self.repodir = repodir
        self.repoType = repoType
        self.hg = None
        
    
        
    def createEdge2 (self, NRev1,NRev2, revL, revR, posL, posR):
        NRev1[posL].Links.append('%d-%d' % (revR,posR))
        NRev2[posR].Links.append('%d-%d' % (revL,posL))
    
    ##Generate the authors for each file from Mercurial
    def RebuildAuthors(self,file,type = 'AG',procId = 0,IndexId = 0, FromAG=False,fid=0):
        
        if self.hg==None:
            if self.repoType == 'GIT':
                if self.repodir!=None:
                    self.hg = G(self.repodir)
                else:
                    self.hg = G()
            else:
                if self.repodir!=None:
                    self.hg = HG(self.repodir)
                else:
                    self.hg = HG()
        revs,authors = self.hg.getLogLocIds(file)
        if len(authors)!=len(revs):
            print ('Error (in '+ str(procId) +') :  for ',IndexId,fid)
        fname = Helpers.GetGraphFilePathForType(fid,type)
        fn = fname+'===Authors'
        f = open(fn,'wb')
        pickle.dump(authors,f)
        f.flush()
        f.close()            
        
    ##Generate the authors and revision list for each file from Mercurial    
    def RebuildRevsAuthors(self,file,type = 'AG',procId = 0,IndexId = 0, FromAG=False,fid=0):
        
        if self.hg==None:
            if self.repoType == 'GIT':
                if self.repodir!=None:
                    self.hg = G(self.repodir)
                else:
                    self.hg = G()
            else:
                if self.repodir!=None:
                    self.hg = HG(self.repodir)
                else:
                    self.hg = HG()
        revs,authors = self.hg.getLogLocIds(file)
        if len(authors)!=len(revs):
            print ('Error (in '+ str(procId) +') :  for ',IndexId,file)
        fname = Helpers.GetGraphFilePathForType(fid,type)

        fn = fname+'===Revs'
        f = open(fn,'wb')
        pickle.dump(revs,f)
        f.flush()
        f.close()            
        fn = fname+'===Authors'
        f = open(fn,'wb')
        pickle.dump(authors,f)
        f.flush()
        f.close()            
        

    def ExtractAllSources(self, file, procId = 0,qs=0,fid = 0):
        
        if self.hg==None:
            if self.repoType == 'GIT':
                if self.repodir!=None:
                    self.hg = G(self.repodir)
                else:
                    self.hg = G()
            else:
                if self.repodir!=None:
                    self.hg = HG(self.repodir)
                else:
                    self.hg = HG()
            
        revs,authors = self.hg.getLogLocIds(file)
        
        
        ##print progress
        print ('Processing (in '+ str(procId) +') : ',fid,file,'Revs:', len(revs),'QSIZE:',qs)

        ##Authorrs and revisions must match. Each revision should have an author
        if len(authors)!=len(revs):
            raise Exception('Error in Authors for -- ' + file)
        ##Irrelevant of the sources, sourceCodeFiles or mercurial, a list of the revisions is required.
        if revs==None:
            print ('None or Load Error')
            print (file)
            raise Exception('None or Load Error')

        if len(revs)==0:
            print ('No Revs----0')
            print (file)
            raise Exception('No Revs:'+file)


        ##Output file name and destination for revision list, author list and individual revisions.
                
        fname = Helpers.mcPath+'RawSources/'
        if not os.path.exists(fname):
            os.makedirs(fname)

        #fname+=Helpers.GetDashedFileName(file)
        
        dfn =str(fid)
        fnamecf= Helpers.mcPath+'RawSourcesCF/'
        if not os.path.exists(fnamecf):
            os.makedirs(fnamecf)

        #fnamecf+=Helpers.GetDashedFileName(file)
        
        
        for i,r in enumerate(revs):
        
        
            alines = self.hg.getCatSource(file,r)

            fn = fname+'Rev-'+str(i)+'==='+dfn
            f = open(fn,'w',encoding='utf-8')
            f.write(alines)
            f.flush()
            f.close()

            if Helpers.isExtValidCpp(file):
                alines = SourceCodeHelpers.Minify2(alines,self.idx)
            
            fn = fnamecf+'Rev-'+str(i)+'==='+dfn
            f = open(fn,'w',encoding='utf-8')
            f.write(alines)
            f.flush()
            f.close()
            alines = None
            ns = None
              
        fn = fname+'Revs==='+dfn
        f = open(fn,'wb')
        pickle.dump(revs,f)
        f.flush()
        f.close()


        ##Save the list of authors for this file.

        fn = fname+'Authors==='+dfn
        f = open(fn,'wb')
        pickle.dump(authors,f)
        f.flush()
        f.close()

        shutil.copy(fname+'Revs==='+dfn,fnamecf+'Revs==='+dfn)
        shutil.copy(fname+'Authors==='+dfn,fnamecf+'Authors==='+dfn)
        revs = None
        authors = None

    def Minify2Extracted(self, file, procId = 0,qs=0, sourcePath='', tgtPath='',fid=0):
        revs = AnnotHelpers.loadPickle(fid,'Revs',sourcePath)
        ##print progress
        print ('Processing (in '+ str(procId) +') : ',fid,file,'Revs:', len(revs),'QSIZE:',qs)

        ##Authorrs and revisions must match. Each revision should have an author
                
        fname = Helpers.mcPath+sourcePath
        if not os.path.exists(fname):
            raise Exception('Source Folder not found')

        #fname+=Helpers.GetDashedFileName(file)
        
        dfn =str(fid)
        fnamecf= Helpers.mcPath+tgtPath
        if not os.path.exists(fnamecf):
            os.makedirs(fnamecf)

        
        for i,r in enumerate(revs):
        
            fn = fname+'Rev-'+str(i)+'==='+dfn
            f = open(fn,encoding='utf-8')
            alines = f.read()            
            f.close()

            if Helpers.isExtValidCpp(file):
                alines = SourceCodeHelpers.Minify2(alines,self.idx)
            
            fn = fnamecf+'Rev-'+str(i)+'==='+dfn
            f = open(fn,'w',encoding='utf-8')
            f.write(alines)
            f.flush()
            f.close()
            alines = None
            ns = None
        
        
        shutil.copy(fname+'Revs==='+dfn,fnamecf+'Revs==='+dfn)
        shutil.copy(fname+'Authors==='+dfn,fnamecf+'Authors==='+dfn)
        revs = None
        authors = None


    ##Generate a Graph for a file
    def buildGraph(self,file,type = 'AG',procId = 0,IndexId = 0,SourceCodeFiles=None,revs = None,authors = None, NoRevs = False, sourceCodeFilesPath=None,fid=0):
        #logs = self.client.log(files = [file])
        Nodes = []
        i = 0            

        ##Build from Souce codes
        if SourceCodeFiles != None:
            if NoRevs:
                revs = [i for i in range(len(SourceCodeFiles))]
                authors = ['' for i in range(len(SourceCodeFiles))]

        
        ##Build from Mercurial
        if SourceCodeFiles==None:
            if self.hg==None:
                if self.repoType == 'GIT':
                    if self.repodir!=None:
                        self.hg = G(self.repodir)
                    else:
                        self.hg = G()
                else:
                    if self.repodir!=None:
                        self.hg = HG(self.repodir)
                    else:
                        self.hg = HG()
            
            revs,authors = self.hg.getLogLocIds(file)
        
        
        ##print progress
        #print ('Processing (in '+ str(procId) +') : ',file,'Revs:', len(revs),' Remaining:', IndexId)
        ##Authorrs and revisions must match. Each revision should have an author
        if len(authors)!=len(revs):
            raise Exception('Error in Authors for -- ' + file)
        ##Irrelevant of the sources, sourceCodeFiles or mercurial, a list of the revisions is required.
        if revs==None:
            print ('None or Load Error')
            print (file)
            raise Exception('None or Load Error')

        if len(revs)==0:
            print ('No Revs----0')
            print (file)
            raise Exception('No Revs:'+file)


        ##Output file name and destination for revision list, author list and individual revisions.
        

        ##Revisions to compare. Two at a time until all revisions are compared and the graph is completed.
        NRev1 = None
        NRev2 = None
        #Index for the revision 1 (left -- RevL) and revision 2 (right -- LevR)
        revL = 0
        revR = 0
        ##Source code for revision 1 and revision 2
        S1 = []
        S2 = []

        dfn = str(fid)
        fname = Helpers.GetGraphFilePathForType(fid,type)
        
        ###Transfer the save/load part to elsewhere.

        #if not os.path.exists(Helpers.mcPath+'Graphs'+type):
        #    os.makedirs(Helpers.mcPath+'Graphs'+type)
        
        #if self.indb:
        #    dbh = DBHelper(dbname='Graphs'+type+'/'+dfn,setup=False)
        #    dbh.setupCleanTableForGraph()
            

        for i,r in enumerate(revs):
            ##Retrieve the source code. From mercurial or the SourceCodeFiles input iterator
            if SourceCodeFiles == None:
                alines = self.hg.getCatSource(file,r)
            else:

                fp = open(Helpers.mcPath+sourceCodeFilesPath+SourceCodeFiles[i],encoding='utf8')
                alines = fp.read()
                fp.close()

            
            ##Get the list of Nodes. Process and minify the code if possible. If the first revision, continue and load the second revision.
            ## Else, swap the current second with first (in later lines) and create the second revision. 
            if i == 0:
                NRev1,S1 = AnnotHelpers.createRevNodes(alines,file,r,i,revs,authors,minifyFunc=None)
                continue
            else:
                NRev2,S2 = AnnotHelpers.createRevNodes(alines,file,r,i,revs,authors,minifyFunc=None)

            
            

            ##Compare i-1 and i
            revL = i-1
            revR = i
            rl = revs[revL]
            rr = revs[revR]
            
            ##Get the large hunk with difflib with all context.
            hunkLines = AnnotHelpers.getRawHunks([S1,S2])
            posL = 0
            posR = 0
            dm = 0
            ##Do for all the identified hunks.
            if len(hunkLines)>0:
                ##Extract the smaller hunks from the large diff output.
                nhunks = AnnotHelpers.getHunks(hunkLines)#,[sources[revL],sources[revR]])
                if nhunks!=None:
                    ##Process each hunk. Make the connections with the next and previsous revisions.
                    for index, h in enumerate(nhunks):
                    
                        lstart = h['lstart']
                        rstart = h['rstart']
                        llen = h['llen']
                        rlen = h['rlen']                    


                        ##A hunk with no modification (add delete update) is mnnor valid.
                        if llen<=0 and rlen<=0:
                            print ('error in hunk index')
                            raise Exception('Hunk index Error')

                        #Unchanged Lines. Connect the unchanged lines to the previous revision and the lines from previsou revision to the current by making a link. (directed backward and forward links)
                        while posL < lstart and posR < rstart:
                            ##Create the link. Author and changeset Id which changed the current line is as for the line in the previous revision.
                            self.createEdge2(NRev1,NRev2 ,revL, revR, posL, posR);
                            NRev2[posR].author = NRev1[posL].author
                            NRev2[posR].cmId = str(NRev1[posL].cmId)
                            ##Increase both left and right links.
                            posL+=1
                            posR+=1         

                        
                        
                        score = 0
                        updateValid = True
                        if llen>0 and rlen>0:
                            ##A potential update
                            ##Act based on the Graph Type

                            ##Based on the SequenceMatcher similarity score.
                            if type == 'AG':
                                sourceCode = h['slines']
                                targetCode = h['tlines']
                                score = SOper.simialrityScore(sourceCode,targetCode,ignorecase=False)

                                ##If the source and target are similar enough, link all the lines starting from lstart until lstart+llen to all the lines starting
                                ## from rstart to rstart+rlen. This is a conservative approach. Similar to the original implementation by KIM.
                                if score>=self.scoreThreshold:
                                    ##For all lines in left hunk, for all lines in the right hunk.
                                    for i1 in range(llen):
                                        for j1 in range(rlen):
                                            self.createEdge2(NRev1,NRev2,revL,revR,lstart+i1,rstart+j1)
                                            ##Type * is an update. Modify the authoos and chnaging revision accordingly.
                                            NRev2[rstart+j1].type = '*'
                                            NRev2[rstart+j1].author = authors[revR]
                                            NRev2[rstart+j1].cmId = str(revs[revR])
                                    posL+=llen
                                    posR+=rlen
                                else:
                                    updateValid = False

                            ##Based on the SequenceMatcher, line mapping. No restriction on the scores. 
                            elif type == 'RAG':

                                revs1_inds,revs2_inds = [],[]
                                ##Ignore very large updates. Treat them as removal and addditions.
                                if llen<1000 and rlen<1000:
                                    ##If a reasonable size, compute the Similarity score for all pairs of Left and Right lines. Calculate the min assign mappings. 
                                    costs = np.array([[1-SOper.simialrityScore(NRev1[lstart+i1].line,NRev2[rstart+j1].line,ignorecase=False) for j1 in range(rlen)] for i1 in range(llen)])
                                    revs1_inds,revs2_inds = linear_sum_assignment(costs)
                                
                                    ##Connect Matching Lines. matching lines. 
                                    for i1 in range(len(revs1_inds)):
                                        self.createEdge2(NRev1,NRev2,revL,revR,lstart+revs1_inds[i1],rstart+revs2_inds[i1])
                                        NRev2[rstart+revs2_inds[i1]].type = '*'
                                        NRev2[rstart+revs2_inds[i1]].cmId = str(revs[revR])
                                        NRev2[rstart+revs2_inds[i1]].author = authors[revR]
                                    
                                     ## if rlen!=llen, one size would have some lines without a match. the first case llen>rlen, some lines are removed.    
                                    if llen>rlen:
                                        for i1 in range(llen):
                                            if not i1 in revs1_inds:
                                                NRev1[lstart+i1].type+=';-'
                                                NRev1[lstart+i1].author+=';'+authors[revR]
                                                NRev1[lstart+i1].cmId+=';'+str(revs[revR])
                               
                                     ##Some lines are added. They do not have a match in the min assignments       
                                    elif llen<rlen:
                                        for i1 in range(rlen):
                                            if not i1 in revs2_inds:

                                                NRev2[rstart+i1].type = '+'
                                                NRev2[rstart+i1].author = authors[revR]
                                                NRev2[rstart+i1].cmId = str(revs[revR])

                                    posL+=llen
                                    posR+=rlen
                                else:
                                    ##Treat very large changes as additions and deletions.
                                    updateValid = False

                            ##The sized based approach proposed originally by KIM (2006)
                            elif type == 'KIM':
                                alpha = 0.10
                                beta = 4
                                gamma = 4
                                ##If certain size limitations, listed below are satisfied, connect conservatively. Else, treat as additions and deletions.

                                if llen>max(alpha*len(NRev1),beta) or rlen>max(alpha*len(NRev2),beta):
                                    updateValid = False
                                elif (float(llen)/float(rlen))>gamma or (float(llen)/float(rlen))<(1.0/gamma):
                                    updateValid = False
                                else:
                                    for i1 in range(llen):
                                        for j1 in range(rlen):
                                            self.createEdge2(NRev1,NRev2,revL,revR,lstart+i1,rstart+j1)
                                            NRev2[rstart+j1].type = '*'
                                            NRev2[rstart+j1].author = authors[revR]
                                            NRev2[rstart+j1].cmId = str(revs[revR])
                                    posL+=llen
                                    posR+=rlen                                
                            
                            ##Line mapping approach based on the levensten distance proposed by SZZ Revisited: Verifying When Changes Induce Fixes (2008)
                            elif type == 'LEV':
                                revs1_inds,revs2_inds = [],[]
                                ##Ignore very large updates. Not in the original implementation. Added for convinience. It would take ages for such cases, and the results are often terrible.

                                if llen<1000 and rlen<1000:
                                    costs = np.array([[1-SOper.similarityScoreLev(NRev1[lstart+i1].line,NRev2[rstart+j1].line,ignorecase=False) for j1 in range(rlen)] for i1 in range(llen)])
                                    revs1_inds,revs2_inds = linear_sum_assignment(costs)
                                    

                                    revs1_indsv,revs2_indsv = [],[]
                                    for i1 in range(len(revs1_inds)):
                                        if costs[revs1_inds[i1],revs2_inds[i1]]<=0.4:
                                            revs1_indsv.append(revs1_inds[i1])
                                            revs2_indsv.append(revs2_inds[i1])
                                    for i1 in range(len(revs1_inds)):
                                        if costs[revs1_inds[i1],revs2_inds[i1]]>0.4:
                                            ##Three cases of link, probable and possible. Connections according to SZZ Revisited: Verifying When Changes Induce Fixes (2008)
                                            topOK = False
                                            downOK = False
                                            t = i1-1
                                            while t>=0:
                                                cinds = [ind for ind in range(len(revs1_inds)) if costs[revs1_inds[ind],revs2_inds[ind]]<=0.4 and ((revs1_inds[ind]>revs1_inds[t] and revs2_inds[ind]<revs2_inds[t]) or (revs1_inds[ind]<revs1_inds[t] and revs2_inds[ind]>revs2_inds[t]))]
                                                if len(cinds)>0:
                                                    break
                                                if costs[revs1_inds[t],revs2_inds[t]]<=0.4:
                                                    topOK = True
                                                    break
                                                t-=1

                                            t = i1+1
                                            while t<len(revs1_inds):
                                                cinds = [ind for ind in range(len(revs1_inds)) if costs[revs1_inds[ind],revs2_inds[ind]]<=0.4 and ((revs1_inds[ind]>revs1_inds[t] and revs2_inds[ind]<revs2_inds[t]) or (revs1_inds[ind]<revs1_inds[t] and revs2_inds[ind]>revs2_inds[t]))]
                                                if len(cinds)>0:
                                                    break
                                                if costs[revs1_inds[t],revs2_inds[t]]<=0.4:
                                                    downOK = True
                                                    break
                                                t+=1


                                            if topOK and downOK:
                                                revs1_indsv.append(revs1_inds[i1])
                                                revs2_indsv.append(revs2_inds[i1])

                                                
                                    revs1_inds = revs1_indsv
                                    revs2_inds = revs2_indsv
                                    
                                    #Connect Based on the mappings.
                                    for i1 in range(len(revs1_inds)):
                                        
                                        
                                        self.createEdge2(NRev1,NRev2,revL,revR,lstart+revs1_inds[i1],rstart+revs2_inds[i1])
                                        NRev2[rstart+revs2_inds[i1]].type = '*'
                                        NRev2[rstart+revs2_inds[i1]].cmId = str(revs[revR])
                                        NRev2[rstart+revs2_inds[i1]].author = authors[revR]
                                    

                                    ##Both sides here can have missing links. For Nodes without links in Left, put deletion in the type.
                                    for i1 in range(llen):
                                        if not i1 in revs1_inds:
                                            NRev1[lstart+i1].type+=';-'
                                            NRev1[lstart+i1].author+=';'+authors[revR]
                                            NRev1[lstart+i1].cmId+=';'+str(revs[revR])
                               
                                            
                                    ##Both sides here can have missing links. For Nodes without links in Right, set addition as the type.
                                    for i1 in range(rlen):
                                        if not i1 in revs2_inds:

                                            NRev2[rstart+i1].type = '+'
                                            NRev2[rstart+i1].author = authors[revR]
                                            NRev2[rstart+i1].cmId = str(revs[revR])

                                    posL+=llen
                                    posR+=rlen
                                else:
                                    ##Treart very large changes as additions and deletions
                                    updateValid = False
                        if rlen == 0 or llen == 0 or (not updateValid):

                            ##For additions, deletions, or invalid updates (size, similarity, etc.). 
                            for hi in h['order']:
                    
                                if hi == '+':                                                                    
                                    NRev2[posR].type = '+'
                                    NRev2[posR].author = authors[revR]
                                    NRev2[posR].cmId = str(revs[revR])
                                    posR+=1
                                

                                elif hi=='-':
                                    NRev1[posL].type+=';-'
                                    NRev1[posL].author+=';'+authors[revR]
                                    NRev1[posL].cmId+=';'+str(revs[revR])
                                    posL+=1
                                else:
                                    print ('Error in order')
                                    raise Exception('Index Order Error')

            else:
                #print ('No hunks')
                pass
            ##Link all the remaining lines of code one link per line. They are unchanged. For meta changes, no hunks are generated. 
            ##Therefore, this part will link each line form Left to a line in right. 

            while posL<len(NRev1) and posR<len(NRev2):
                self.createEdge2(NRev1,NRev2,revL,revR,posL,posR)
                NRev2[posR].author = NRev1[posL].author
                NRev2[posR].cmId = str(NRev1[posL].cmId)
                posL+=1
                posR+=1
            

            ##Save Left Revision. It now has both its next, and its previous links. 
            
            if self.indb:
                
                yield [revL,rl,authors[revL],ujson.dumps([nd.__dict__ for nd in NRev1])]
                #dbh.Insert(row=row,keys=self.keysrdLst,table='RevisionData')
                
            else:            
                fn = fname+'===Rev-'+str(revL)
                f = open(fn,'wb')
                pickle.dump(NRev1,f)
                f.flush()
                f.close()            


            ##Copy second revision to NRev1. The links to the previous revision for NRev2 are computed. In the next iteration, the links to 
            ##The next revision are also genertated and then it is saved.
            NRev1 = NRev2
            S1=S2

        ##Save the last revision. It is stored in Both NRev1 and NRev2 now. But since it is the last iteration it is not yet saved to the disk.
        
        if self.indb:
            
            yield [revR,revs[-1],authors[-1],ujson.dumps([nd.__dict__ for nd in NRev1])]
            #dbh.Insert(row=row,keys=self.keysrdLst,table='RevisionData')

            #dbh.close()

        else:
            fn = fname+'===Rev-'+str(revR)
            f = open(fn,'wb')
            pickle.dump(NRev1,f)
            f.flush()
            f.close()            

            ##Save the list of the revisions for this file.

            fn = fname+'===Revs'
            f = open(fn,'wb')
            pickle.dump(revs,f)
            f.flush()
            f.close()


            ##Save the list of authors for this file.

            fn = fname+'===Authors'
            f = open(fn,'wb')
            pickle.dump(authors,f)
            f.flush()
            f.close()

        #return revs

    ##Very similar to BuildGraph. It copies the structure from there to another type but this is much faster. The differences are only for the updates (AG,RAG,KIM,LEV)
    def CopyToType(self,file,fromtype = 'AG', totype='KIM',procId = 0,IndexId = 0,indb = True,fid = 0):
        #logs = self.client.log(files = [file])
        i = 0
        
        S1 = None
        S2 = None
                        
        revs = AnnotHelpers.loadRevsList(fid,type=fromtype,indb = indb)
        authors = AnnotHelpers.loadAuthors(fid,type=fromtype,indb = indb)
        if len(authors)!=len(revs):
            if self.hg==None:
                if self.repoType == 'GIT':
                    if self.repodir!=None:
                        self.hg = G(self.repodir)
                    else:
                        self.hg = G()
                else:
                    if self.repodir!=None:
                        self.hg = HG(self.repodir)
                    else:
                        self.hg = HG()
            revs,authors = self.hg.getLogLocIds(file)
        if len(authors)!=len(revs):            
            raise Exception('Error in Authors for -- ' + file)
        if revs==None:
            print ('None or Load Error')
            print (file)
            raise Exception('None or Load Error')


        if len(revs)==0:
            print ('No Revs----0')
            print (file)
            raise Exception('No Revs:'+file)

        #print ('Processing (in '+ str(procId) +') : ',IndexId,file,'Revs:', len(revs))
        #if IndexId%100==0:
        #print ('Processed (in '+ str(procId) +') : ',IndexId)

        fname = Helpers.GetGraphFilePathForType(fid,type=totype)
        if indb:
            dbh = DBHelper(dbname='Graphs'+totype+'/'+str(fid),setup = False)
            dbh.setupCleanTableForGraph()

        NRev1 = AnnotHelpers.loadRevision(fid,0,type=fromtype,indb=indb)        
        NRev2 = None
        revL = 0
        revR = 0
        S1 = []
        for j in range(len(NRev1)):
            NRev1[j].Links.clear()
            S1.append(NRev1[j].line)
            NRev1[j].cmId=str(revs[0])
            NRev1[j].type='+'
            NRev1[j].author = authors[0]
        if len(revs)>1:

            
            for i in range(1,len(revs)):

                revL = i-1
                revR = i
                rl = revs[revL]
                rr = revs[revR]
                
                
                NRev2 = AnnotHelpers.loadRevision(fid,revR,type=fromtype,indb = indb)
                S2 = []
                
                for j in range(len(NRev2)):
                    NRev2[j].Links.clear()
                    NRev2[j].cmId=''
                    NRev2[j].type=''
                    NRev2[j].author = ''
                    S2.append(NRev2[j].line)
                
                
                hunkLines = AnnotHelpers.getRawHunks([S1,S2])
                
                
                posL = 0
                posR = 0
                dm = 0
            
                if len(hunkLines)>0:
                    nhunks = AnnotHelpers.getHunks(hunkLines)
                    
                    
                    if nhunks!=None:
                        for index, h in enumerate(nhunks):
                    
                            lstart = h['lstart']
                            rstart = h['rstart']
                            llen = h['llen']
                            rlen = h['rlen']                    

                            

                            if llen<=0 and rlen<=0:
                                print ('error in hunk index')
                                raise Exception('Hunk index Error')

                            #Unchanged Lines

                            while posL < lstart and posR < rstart:
                                self.createEdge2(NRev1,NRev2 ,revL, revR, posL, posR);
                                NRev2[posR].author = NRev1[posL].author
                                NRev2[posR].cmId = str(NRev1[posL].cmId)
                                posL+=1
                                posR+=1
                                            

                        
                            #No change hunk type. Hunks are divided into lines. Lines are either added or deleted. 
                            updateValid = True
                            score = 0
                            if llen>0 and rlen>0:
                                if type == 'AG':
                                    sourceCode = h['slines']
                                    targetCode = h['tlines']
                                    score = SOper.simialrityScore(sourceCode,targetCode,ignorecase=False)

                                    if score>=self.scoreThreshold:
                                        for i1 in range(llen):
                                            for j1 in range(rlen):
                                                self.createEdge2(NRev1,NRev2,revL,revR,lstart+i1,rstart+j1)
                                                NRev2[rstart+j1].type = '*'
                                                NRev2[rstart+j1].author = authors[revR]
                                                NRev2[rstart+j1].cmId = str(revs[revR])
                                        posL+=llen
                                        posR+=rlen
                                    else:
                                        updateValid = False


                                elif type == 'RAG':
                                    revs1_inds,revs2_inds = [],[]
                                    
                                    if llen<1000 and rlen<1000:

                                        costs = np.array([[1-SOper.simialrityScore(NRev1[lstart+i1].line,NRev2[rstart+j1].line,ignorecase=False) for j1 in range(rlen)] for i1 in range(llen)])
                                        revs1_inds,revs2_inds = linear_sum_assignment(costs)
                                
                                
                                        for i1 in range(len(revs1_inds)):
                                            self.createEdge2(NRev1,NRev2,revL,revR,lstart+revs1_inds[i1],rstart+revs2_inds[i1])
                                            NRev2[rstart+revs2_inds[i1]].type = '*'
                                            NRev2[rstart+revs2_inds[i1]].cmId = str(revs[revR])
                                            NRev2[rstart+revs2_inds[i1]].author = authors[revR]
                                        

                                        if llen>rlen:
                                            for i1 in range(llen):
                                                if not i1 in revs1_inds:
                                                    NRev1[lstart+i1].type+=';-'
                                                    NRev1[lstart+i1].author+=';'+authors[revR]
                                                    NRev1[lstart+i1].cmId+=';'+str(revs[revR])
                               
                                            
                                        elif llen<rlen:
                                            for i1 in range(rlen):
                                                if not i1 in revs2_inds:

                                                    NRev2[rstart+i1].type = '+'
                                                    NRev2[rstart+i1].author = authors[revR]
                                                    NRev2[rstart+i1].cmId = str(revs[revR])

                                        posL+=llen
                                        posR+=rlen
                                    else:
                                        updateValid = False
                                elif type == 'KIM':
                                    alpha = 0.10
                                    beta = 4
                                    gamma = 4

                                    if llen>max(alpha*len(NRev1),beta) or rlen>max(alpha*len(NRev2),beta):
                                        updateValid = False
                                    elif (llen/rlen)>gamma or (llen/rlen)<(1/gamma):
                                        updateValid = False
                                    else:
                                        for i1 in range(llen):
                                            for j1 in range(rlen):
                                                self.createEdge2(NRev1,NRev2,revL,revR,lstart+i1,rstart+j1)
                                                NRev2[rstart+j1].type = '*'
                                                NRev2[rstart+j1].author = authors[revR]
                                                NRev2[rstart+j1].cmId = str(revs[revR])
                                        posL+=llen
                                        posR+=rlen                                

                                elif type == 'LEV':
                                    revs1_inds,revs2_inds = [],[]
                                    if llen<1000 and rlen<1000:
                                        costs = np.array([[1-SOper.similarityScoreLev(NRev1[lstart+i1].line,NRev2[rstart+j1].line,ignorecase=False) for j1 in range(rlen)] for i1 in range(llen)])
                                        revs1_inds,revs2_inds = linear_sum_assignment(costs)
                                    

                                        revs1_indsv,revs2_indsv = [],[]
                                        for i1 in range(len(revs1_inds)):
                                            if costs[revs1_inds[i1],revs2_inds[i1]]<=0.4:
                                                revs1_indsv.append(revs1_inds[i1])
                                                revs2_indsv.append(revs2_inds[i1])
                                        for i1 in range(len(revs1_inds)):
                                            if costs[revs1_inds[i1],revs2_inds[i1]]>0.4:
                                            
                                                topOK = False
                                                downOK = False
                                                t = i1-1
                                                while t>=0:
                                                    cinds = [ind for ind in range(len(revs1_inds)) if costs[revs1_inds[ind],revs2_inds[ind]]<=0.4 and ((revs1_inds[ind]>revs1_inds[t] and revs2_inds[ind]<revs2_inds[t]) or (revs1_inds[ind]<revs1_inds[t] and revs2_inds[ind]>revs2_inds[t]))]
                                                    if len(cinds)>0:
                                                        break
                                                    if costs[revs1_inds[t],revs2_inds[t]]<=0.4:
                                                        topOK = True
                                                        break
                                                    t-=1

                                                t = i1+1
                                                while t<len(revs1_inds):
                                                    cinds = [ind for ind in range(len(revs1_inds)) if costs[revs1_inds[ind],revs2_inds[ind]]<=0.4 and ((revs1_inds[ind]>revs1_inds[t] and revs2_inds[ind]<revs2_inds[t]) or (revs1_inds[ind]<revs1_inds[t] and revs2_inds[ind]>revs2_inds[t]))]
                                                    if len(cinds)>0:
                                                        break
                                                    if costs[revs1_inds[t],revs2_inds[t]]<=0.4:
                                                        downOK = True
                                                        break
                                                    t+=1

                                                if topOK and downOK:
                                                    revs1_indsv.append(revs1_inds[i1])
                                                    revs2_indsv.append(revs2_inds[i1])

                                                
                                        revs1_inds = revs1_indsv
                                        revs2_inds = revs2_indsv
                                        for i1 in range(len(revs1_inds)):
                                        
                                        
                                            self.createEdge2(NRev1,NRev2,revL,revR,lstart+revs1_inds[i1],rstart+revs2_inds[i1])
                                            NRev2[rstart+revs2_inds[i1]].type = '*'
                                            NRev2[rstart+revs2_inds[i1]].cmId = str(revs[revR])
                                            NRev2[rstart+revs2_inds[i1]].author = authors[revR]
                                    
                                        for i1 in range(llen):
                                            if not i1 in revs1_inds:
                                                NRev1[lstart+i1].type+=';-'
                                                NRev1[lstart+i1].author+=';'+authors[revR]
                                                NRev1[lstart+i1].cmId+=';'+str(revs[revR])
                               
                                            
                                    
                                        for i1 in range(rlen):
                                            if not i1 in revs2_inds:

                                                NRev2[rstart+i1].type = '+'
                                                NRev2[rstart+i1].author = authors[revR]
                                                NRev2[rstart+i1].cmId = str(revs[revR])

                                        posL+=llen
                                        posR+=rlen
                                    else:
                                        updateValid = False
                            if rlen == 0 or llen == 0 or (not updateValid):
                                for hi in h['order']:
                    
                                    if hi == '+':                                                                    
                                        NRev2[posR].type = '+'
                                        NRev2[posR].author = authors[revR]
                                        NRev2[posR].cmId = str(revs[revR])
                                        posR+=1
                                

                                    elif hi=='-':
                                        NRev1[posL].type+=';-'
                                        NRev1[posL].author+=';'+authors[revR]
                                        NRev1[posL].cmId+=';'+str(revs[revR])
                                        posL+=1
                                    else:
                                        print ('Error in order')
                                        raise Exception('Index Order Error')

                else:
                    #print ('No hunks')
                    pass
                while posL<len(NRev1) and posR<len(NRev2):
                    self.createEdge2(NRev1,NRev2,revL,revR,posL,posR)
                    NRev2[posR].author = NRev1[posL].author
                    NRev2[posR].cmId = str(NRev1[posL].cmId)
                    posL+=1
                    posR+=1
            


                if indb:
                    row = [revL,rl,authors[revL],ujson.dumps([nd.__dict__ for nd in NRev1])]
                    dbh.Insert(row=row,keys=self.keysrdLst,table='RevisionData')
                else:
                    fn = fname+'===Rev-'+str(revL)
                    f = open(fn,'wb')
                    pickle.dump(NRev1,f)
                    f.flush()
                    f.close()            


                NRev1 = NRev2
                S1=S2
                
                

        if  indb:
            row = [revR,revs[-1],authors[-1],ujson.dumps([nd.__dict__ for nd in NRev1])]
            dbh.Insert(row=row,keys=self.keysrdLst,table='RevisionData')
            dbh.close()
        else:
            fn = fname+'===Rev-'+str(revR)
            f = open(fn,'wb')
            pickle.dump(NRev1,f)
            f.flush()
            f.close()            

            fn = fname+'===Revs'
            f = open(fn,'wb')
            pickle.dump(revs,f)
            f.flush()
            f.close()

            fn = fname+'===Authors'
            f = open(fn,'wb')
            pickle.dump(authors,f)
            f.flush()
            f.close()

        return revs

    
    
    
    ##Drawing the graphs. For demonstration purposes only. Not required. 
    def drawGraph(self, file):
        
        matplotlib.rcParams.update({'font.size': 4})
        Nodes,revs = self.buildGraph(file)
        maxN = max([len(n) for n in Nodes])
        plt.figure(figsize=(50,100))
        #plt.tight_layout()
        plt.ylim([0,maxN+1])
        plt.xlim([0,len(revs)+1])


        for i in range(len(revs)):
            y = [j+1 for j in range(len(Nodes[i]))]
            x = [i+1 for j in range(len(Nodes[i]))]
            s = [3 for j in range(len(Nodes[i]))]
            plt.scatter(x,y, marker='o', c='r',s=12,edgecolors='none')
            for j in range(len(Nodes[i])):                
                plt.annotate(Nodes[i][j].type,xy=(i+1+0.01,j+1)) #, xytext=(i+1,j+0.2)

        for i in range(len(revs)-1):
            print (i)
            x1 = i+1
            for j in range(len(Nodes[i])):
                y1= j+1
                for t in range(len(Nodes[i][j].Links)):
                    lnk = Nodes[i][j].Links[t].split('-')                    
                    x2 = int(lnk[0])+1
                    y2 = int(lnk[1])+1
                    plt.plot([x1,x2],[y1,y2],'b-',markersize=2)

                
        
        nm = 'PIC/%s.jpg' % Helpers.GetDashedFileName(file)
        nm=Helpers.mcPath+nm
        plt.savefig(nm ,format='jpg', dpi=200)
        
    def drawGraphWithData(self, file,Nodes,revs,minX=0,minY=0):
        
        matplotlib.rcParams.update({'font.size': 4})
        
        maxN = max([len(n) for n in Nodes])
        plt.figure(figsize=(50,100))
        #plt.tight_layout()
        plt.ylim([0,maxN+1])
        plt.xlim([0,len(revs)+1])


        for i in range(len(revs)):
            y = [j+1 for j in range(len(Nodes[i]))]
            x = [i+1 for j in range(len(Nodes[i]))]
            s = [3 for j in range(len(Nodes[i]))]
            plt.scatter(x,y, marker='o', c='r',s=12,edgecolors='none')
            for j in range(len(Nodes[i])):                
                plt.annotate(Nodes[i][j].type,xy=(i+1+0.01,j+1)) #, xytext=(i+1,j+0.2)

        for i in range(len(revs)-1):
            print (i)
            x1 = i+1
            for j in range(len(Nodes[i])):
                y1= j+1
                for t in range(len(Nodes[i][j].Links)):
                    lnk = Nodes[i][j].Links[t].split('-')                    
                    x2 = int(lnk[0])+1-minX
                    y2 = int(lnk[1])+1-minY
                    plt.plot([x1,x2],[y1,y2],'b-',markersize=2)

                
        
        nm = 'PIC/%s-%d,%d.jpg' % (Helpers.GetDashedFileName(file),minX,minY)
        nm=Helpers.mcPath+nm
        plt.savefig(nm ,format='jpg', dpi=200)
        

    def drawGraphWithDataPath(self, file,Nodes,revs,pathdel=[],pathed=[],locid=0):

        
        
        matplotlib.rcParams.update({'font.size': 22})
        
        maxN = max([len(n) for n in Nodes])
        plt.figure(figsize=(70,80))
        #plt.tight_layout()
        plt.ylim([0,maxN+1])
        plt.xlim([0,len(revs)+1])
        plt.tight_layout()

        for i in range(len(revs)):
            y = [j+1 for j in range(len(Nodes[i]))]
            x = [i+1 for j in range(len(Nodes[i]))]
            s = [3 for j in range(len(Nodes[i]))]
            plt.scatter(x,y, marker='o',s=500, c='r',edgecolors='none')
            for j in range(len(Nodes[i])):                
                plt.annotate(Nodes[i][j].type,xy=(i+1+0.03,j+1)) #, xytext=(i+1,j+0.2)

        for i in range(len(revs)-1):
            print ('Rev' , i)
            x1 = i+1
            for j in range(len(Nodes[i])):
                y1= j+1
                for t in range(len(Nodes[i][j].Links)):
                    lnk = Nodes[i][j].Links[t].split('-')                    
                    x2 = int(lnk[0])+1
                    y2 = int(lnk[1])+1
                    plt.plot([x1,x2],[y1,y2],'b-',markersize=2)

        
        if len(pathdel)>0:
            for k in range(len(pathdel)):            
                print ('Del',k)
                pathk = pathdel[k]
                for i in range(len(pathk)):
                    
                    for j in range(len(pathk[i])):
                        x1 = pathk[i][j].ij[0]+1
                        y1 = pathk[i][j].ij[1]+1
                        for t in range(len(pathk[i][j].Links)):
                            lnk = pathk[i][j].Links[t].split('-')                    
                            x2 = int(lnk[0])+1
                            y2 = int(lnk[1])+1
                            if x2<=len(revs) and x1<=len(revs) and x2>=1 and x1>=1:
                                plt.plot([x1,x2],[y1,y2],'r-',linewidth=10)
        if len(pathed)>0:
            
            for k in range(len(pathed)):            
                print ('Ed',k)
                pathk = pathed[k]
                for i in range(len(pathk)):
                    
                    for j in range(len(pathk[i])):
                        x1 = pathk[i][j].ij[0]+1
                        y1 = pathk[i][j].ij[1]+1
                        for t in range(len(pathk[i][j].Links)):
                            lnk = pathk[i][j].Links[t].split('-')                    
                            x2 = int(lnk[0])+1
                            y2 = int(lnk[1])+1
                            if x2<=len(revs) and x1<=len(revs) and x2>=1 and x1>=1:
                                plt.plot([x1,x2],[y1,y2],'y-',linewidth=10)
        nm = 'PIC/%s-ForPath-%d.png' % (Helpers.GetDashedFileName(file),locid)
        nm=Helpers.mcPath+nm
        plt.savefig(nm ,format='png', dpi=150)
        
        plt.close('all')