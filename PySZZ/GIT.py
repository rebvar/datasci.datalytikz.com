import os
import codecs
import chardet
from subprocess import Popen, PIPE
from .Helpers import Helpers
import dulwich
from dulwich import porcelain as po, repo, diff_tree
from io import StringIO
from random import Random

class G:

    def __init__(self,repodir = Helpers.repodir):
        self.repodir = repodir
        self.cwd = os.getcwd()
        #self.repo = dulwich.repo.Repo(self.repodir)
        self.r = repo.Repo(self.repodir)


    
    def getLogLocIds (self,file = None,r1 = None,r2 = None,reverse=True, follow = False, returnLogs = False, ignoreMerges = False):

        """
            r2 inclusive
            r1 exclusive
            (r1,r2]
        """
        
        out = []
        auth = []
        
        p = file
        walker = None
        
        if file is not None and isinstance(file, str):
            file = file.encode()

        if r1 is not None and isinstance(r1, str):
            r1 = r1.encode()

        if r2 is not None and isinstance(r2, str):
            r2 = r2.encode()

        if file==None:
            
            if r2 is not None:
                walker = self.r.get_graph_walker(heads = [r2])
            else:
                walker = self.r.get_graph_walker()
        else:
            

            if r2 is not None:
                walker = iter(self.r.get_walker(paths=[file],follow = follow, include = [r2]))
            else:
                walker = iter(self.r.get_walker(paths=[file],follow = follow))


        prev = None
        
        if file is not None:
            cset = next(walker, None)
        else:
            cset = walker.next()
        while True:
            commit = None
            if cset!=None:            
                if file is not None:
                    commit = cset.commit
                else:
                    commit = self.r.get_object(cset)
            
            if prev is None:
                prev = commit                
                
                if file is not None:
                    cset = next(walker, None)
                else:
                    cset = walker.next()
                continue
            tr = None
            if commit is not None:
                tr = commit.tree
            delta = diff_tree.tree_changes(self.r, tr,  prev.tree)
            for x in delta:
                #if isinstance(x, Random):
                #    continue
                if file is not None:
                    if x.new.path == file or x.old.path == file:
                        if returnLogs:
                            out.append(x)
                            auth.append(prev.author)
                        else:
                            if prev.id not in out:                  
                                out.append(prev.id)
                                auth.append(prev.author)
                    
                        
                else:
                    if returnLogs:
                        out.append(x)
                        auth.append(prev.author)
                    else:
                        if prev.id not in out:
                            out.append(prev.id)
                            auth.append(prev.author)
            prev = commit
            if prev == None:
                break
            if (r1 is not None) and (prev.id == r1):
                break
            
            if file is not None:
                cset = next(walker, None)
            else:
                cset = walker.next()
        if reverse:
            if not returnLogs:
                out = [Helpers.ConvertToUTF8(o) for o in out]
            out.reverse()
            auth.reverse()
        return out, [Helpers.ConvertToUTF8(a) for a in auth]


    def getAllLogsMy(self, file = None, r1 = None, r2 = None ,reverse=True, follow = False, dolower=False, toText =False):
        """
            r2 inclusive
            r1 exclusive
            (r1,r2]
        """

        if file is not None and isinstance(file, str):
            file = file.encode()

        if r1 is not None and isinstance(r1, str):
            r1 = r1.encode()

        if r2 is not None and isinstance(r2, str):
            r2 = r2.encode()

        out = []        
        
        p = file
        walker = None
        prev = None



        if file==None:
            if r2 is not None:
                walker = self.r.get_graph_walker(heads = [r2])
            else:
                walker = self.r.get_graph_walker()
        else:
            
            if r2 is not None:
                walker = iter(self.r.get_walker(paths=[file],follow = follow, include = [r2]))
            else:
                walker = iter(self.r.get_walker(paths=[file],follow = follow))
        
        if file is not None:
            cset = next(walker, None)
        else:
            cset = walker.next()
        while True:
            commit = None
            if cset!=None:            
                if file is not None:
                    commit = cset.commit
                else:
                    commit = self.r.get_object(cset)

            if prev is None:
                prev = commit                
                
                if file is not None:
                    cset = next(walker, None)
                else:
                    cset = walker.next()
                continue
            if file is not None:
                files = [file]
            else:
                files = []
                tr = None
                if commit is not None:
                    tr = commit.tree
                delta = diff_tree.tree_changes(self.r, tr,  prev.tree)
            
                for x in delta:
                    
                    
                    if x.new.path is not None:
                        files.append(x.new.path)

                    else:
                        if x.old.path is not None:
                            files.append(x.old.path)                        
            msg = prev.message
            if toText:
                msg = Helpers.ConvertToUTF8(msg)

            if dolower:
                msg = msg.lower()

            cid = Helpers.ConvertToUTF8(prev.id)
            out.append({'m':msg, 'committer':Helpers.ConvertToUTF8(prev.committer), 'author': Helpers.ConvertToUTF8( prev.author)
                    , 'commit_time': prev.commit_time, 'commit_timezone': prev.commit_timezone, 'author_time': prev.author_time
                    , 'author_timezone': prev.author_timezone, 'parents':[Helpers.ConvertToUTF8(pr) for pr in prev.parents], 'cid':cid, 'locid': cid, 'cidshort':cid,
                    'tree': Helpers.ConvertToUTF8(prev.tree), 'files':[Helpers.ConvertToUTF8(f) for f in files], 'date' : prev.commit_time,'timestamp' : prev.commit_time, 'tags':'', 'branches':''})
            
            prev = commit
            if prev == None:
                break
            

            if (r1 is not None) and (commit.id == r1):
                break
            
            if file is not None:
                cset = next(walker, None)
            else:
                cset = walker.next()
        if reverse:
            out.reverse()
        return out


    def getLogFollow (self,file,reverse=True):
        return self.getLogLocIds(file,follow = True,reverse=reverse)

    def getChangedFiles(self,r1,r2):

        if file is not None and isinstance(file, str):
            file = file.encode()

        if r1 is not None and isinstance(r1, str):
            r1 = r1.encode()

        if r2 is not None and isinstance(r2, str):
            r2 = r2.encode()

        out = set()
        outmod = set()
        outdel = set()
        types = set()
        
        if r2 is not None:
            walker = self.r.get_graph_walker(heads=[r2])    
        else:
            walker = self.r.get_graph_walker()
        
        cset = walker.next()
        prev = None
        
        if cset == None:
            return None

        while True:
            commit = None
            if cset!=None:
                commit = self.r.get_object(cset)
            
            if prev is None:                
                prev = commit
                
                cset = walker.next()
                
                continue
            tr = None
            if commit is not None:
                tr = commit.tree
            delta = diff_tree.tree_changes(self.r, tr, prev.tree)
            for x in delta:
                if x.type == 'delete':
                    outdel.add(x.old.path)
                elif x.type == 'add':
                    out.add(x.new.path)
                else:
                    outmod.add(x.new.path)
                types.add(x.type)
                #try:
                #    out.add(x.new.path)                        
                #except Exception as ex:
                #    pass
            
            
            
            if commit is None:
                break

            prev = commit
            

            if (r1 is not None) and (prev.id == r1):
                break
            
            
            
            cset = walker.next()

        if None in out:
            out.remove(None)

        return sorted(list(out)), sorted(list(outdel)), sorted(list(outmod)), sorted(list(types))


    def getRevisionFiles(self, rev):
        
        
        if rev is not None and isinstance(rev, str):
            rev = rev.encode()

        
        commit = self.r.get_object(rev)
        
        delta = diff_tree.tree_changes(self.r, None, commit.tree)
        files = []
        
        for x in delta:
            if x.type == 'add' or x.type == 'modify':                
                files.append(x.new.path)
                
        
        return sorted(files)


    ##Extracts the source code for revision rev of file=file
    def getCatSource(self,file, rev):
                        
        if file is not None and isinstance(file, str):
            file = file.encode()

        if rev is not None and isinstance(rev, str):
            rev = rev.encode()

        
        commit = self.r.get_object(rev)
        prev = None
        tr = None
        if len(commit.parents)>0 and len(commit.parents)<2:
            prev = self.r.get_object(commit.parents[0])
            if prev is not None:
                tr = prev.tree
        delta = list(diff_tree.tree_changes(self.r, tr, commit.tree))
        for x in delta:
            if x.type == 'add' or x.type == 'modify':
                if x.new.path == file:
                    return Helpers.ConvertToUTF8(self.r.get_object(x.new.sha).data)
            else:
                if x.old.path == file and x.new.path == None:
                    return ""
        return None

    #def getAnnotatedSourceLines(self,file, rev, showUser=True,showRevs=True):
    #    cm = r'hg annotate "-u" "-n" "-r %d" "%s"' % (rev,file)
        
    #    os.chdir(self.repodir)
        
    #    with Popen(cm,
    #        stdout=PIPE, stderr=PIPE) as p:
    #        out, errors = p.communicate()
        
    #    out = Helpers.ConvertToUTF8(out).splitlines()
    #    lines = []
    #    users = []
    #    revs = []
    #    for line in out:
    #        if len(line)<1 or line.find(': ')<0:
    #            continue

    #        line = line.split(': ')
    #        line0 = line[0].rsplit(' ')

    #        users.append(''.join(line0[:-1]).strip())
    #        revs.append(line0[-1].strip())
    #        lines.append(''.join(line[1:]))
    #    os.chdir(self.cwd)
    #    return lines,users,revs
    

    #def getRawHunks (self,files,r1,r2,c):
    #    if files[0]==files[1]:
    #        cm = r'hg diff "-r %d" "-r %d" "%s" "-U %d"' % (r1,r2,files[0],c)        
    #    else:
    #        cm = r'hg diff "-r %d" "-r %d" "%s" "%s" "-U %d"' % (r1,r2,files[1],files[0],c)
    #    os.chdir(self.repodir)
        
    #    with Popen(cm,
    #        stdout=PIPE, stderr=PIPE) as p:
    #        out, errors = p.communicate()
        
    #    os.chdir(self.cwd)
    #    out = Helpers.ConvertToUTF8(out).splitlines()
    #    return out



    #def getRenamedFile(self,file,r1,r2):
    #    cm=r'hg diff "-r %d" "-r %d" "%s" "-g"'%(r1,r2,file)
    #    os.chdir(self.repodir)
    #    lines = []

    #    with Popen(cm,
    #        stdout=PIPE, stderr=PIPE) as p:
    #        out, errors = p.communicate()

    #    out = getLines(out)
    #    cpf,cpt = None,None
    #    for line in out:
    #        if line.startswith('copy from '):
    #            cpf = line[len('copy from '):]
    #        if line.startswith('copy to '):
    #            cpt = line[len('copy to '):]
    #    os.chdir(self.cwd)
    #    if cpf is None or cpt is None:
    #        return None
    #    return cpf,cpt

    
    