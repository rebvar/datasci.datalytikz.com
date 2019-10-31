import os
from unidiff import PatchSet,PatchedFile
import codecs
import chardet
from subprocess import Popen, PIPE
from .Helpers import Helpers


class HG: 


    def __init__(self,repodir = Helpers.repodir):
        self.repodir = repodir
        self.cwd = os.getcwd()

    def getLogLocIds (self,file,r1 = None,r2 = None,reverse=True):
        cm = 'hg log "%s"' % file
        if r1!=None:
            cm+= ' -r '+str(r1)
        if r2!=None:
            cm+= ' -r '+str(r2)
                
        os.chdir(self.repodir)
        
        out = os.popen(cm).read().split('\n\n')
        ret = []
        authors = []
        
        for item in out:
            
            if item.count('\n')<2:               
                continue

            item = item.split('\n')
            
            cf = False
            uf = False
            
            for elem in item: 
                
                if elem.startswith ('changeset'):
                    locid = int(elem.split(':')[1].strip())
                    
                    ret.append(locid)
                    cf = True
                elif elem.startswith('user'):
                    uid = elem.split(':')[1].strip()
                    authors.append(uid)
                    uf = True


            if len(authors)!=len(ret):
                print ('Error Author Extraction',len(ret),len(authors),file)
                input()


            if (cf==False or uf==False):
                print ('Error in Log')
                print (item)
                input()                    
        
        os.chdir(self.cwd)
        
        if reverse:
            ret.reverse()
            authors.reverse()
        return ret,authors


    def getLogFollow (self,file,reverse=True):
        cm = 'hg log "%s" --follow' % file
        os.chdir(self.repodir)        
        out = os.popen(cm).read()
        path = self.repodir
        path = Helpers.mcPath+'Logs/'
        if not os.path.exists(path):
            os.makedirs(path)
        path = path+Helpers.GetDashedFileName(file)
        o = open(path,'w')
        o.write(out)
        o.close()
        os.chdir(self.cwd)


    def getChangedFiles(self,r1,r2):
        cm = 'hg diff -r %d -r %d --stat' % (r1,r2)
        
        os.chdir(self.repodir)
        
        out = os.popen(cm).read().split('\n')
        os.chdir(self.cwd)
        return out

    ##Extracts the source code for revision rev of file=file
    def getCatSource(self,file, rev):
                
        os.chdir(self.repodir)
        lines = []

        with Popen(r'hg cat "-r %d" "%s"'%(rev,file),
            stdout=PIPE, stderr=PIPE) as p:
            out, errors = p.communicate()

        out = Helpers.ConvertToUTF8(out)
        os.chdir(self.cwd)
        return out
    

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



    def getRenamedFile(self,file,r1,r2):
        cm=r'hg diff "-r %d" "-r %d" "%s" "-g"'%(r1,r2,file)
        os.chdir(self.repodir)
        lines = []

        with Popen(cm,
            stdout=PIPE, stderr=PIPE) as p:
            out, errors = p.communicate()

        out = getLines(out)
        cpf,cpt = None,None
        for line in out:
            if line.startswith('copy from '):
                cpf = line[len('copy from '):]
            if line.startswith('copy to '):
                cpt = line[len('copy to '):]
        os.chdir(self.cwd)
        if cpf is None or cpt is None:
            return None
        return cpf,cpt

    
    