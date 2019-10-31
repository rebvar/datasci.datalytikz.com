from .Helpers import Helpers
from .DBHelper import DBHelper
import datetime
import networkx as nx
import matplotlib.pyplot as plt
from Lib import DPLIB
import os
import matplotlib
import numpy as np
import os.path
import json

Name = 'KIM'

Name = 'KIM-Minify2-CLF-DB'

#GraphsFol = 'BlamesKIM-No-Minify-DB'

logDates = {}
dbh = DBHelper()
logAuthors={}
authorMails = set()





#keys = ['bug','reportTimestamp','status','product','component']
#quer = "select "+','.join(keys)+" from VALIDBUGS where status like '%fixed%' and (product = 'Core' or product='core')"

#vbugs,vbugscolnames = dbh.GET_ALL(table='VALIDBUGS',fields = keys)    

logs,logcolnames = dbh.GET_ALL(table='LOGS')

filerows,fidCols =  dbh.GET_ALL(table='FILES',fields=['rowid','file'])

fileIDS = {}

for row in filerows:
    fileIDS[row[1]] = row[0]

filerows = None


logsd = {}

fidcmpBlamed = {}

fidcmpBlamer = {}


fidcmp = {}

import os

if os.path.exists('MetricsChgData.txt'):
    
    o = open('MetricsChgData.txt')
    lines = o.readlines()
    o.close()
    MetricsChgData = {}
    for line in lines:
        line = line.replace('\n','').split(';')
        if not line[0] in MetricsChgData.keys():
            MetricsChgData[line[0]] = {}
        if not line[1] in MetricsChgData[line[0]].keys():
            MetricsChgData[line[0]][line[1]] = line[2]
    print (len(MetricsChgData.keys()))
    print('Metrics loaded')


else:


    SourceFolder =Helpers.mcPath+'RawSourcesCFOUTMetrics/'
    MetricsChgData = {}
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
                #MetricsChgData[fid][revID] = {}
                MetricsChgData[fid][revID]=','.join([str(float(t.strip())) if len(t.strip())>0 else '0' for t in metrics.split('\t')])
        print (i)


    #countMetrics = len(MetricsChgData[revID][0])
    print (len(MetricsChgData.keys()))
    print('Metrics loaded')

    o = open('MetricsChgData.txt','w')
    for fid in MetricsChgData.keys():
        for revID in MetricsChgData[fid].keys():
            o.write('%s;%s;%s\n'%(fid,revID,MetricsChgData[fid][revID]))
    o.close()


for log in logs:
    key = log[logcolnames.index('locid')]
    logsd[key]=log
    logDates[key]=log[logcolnames.index('timestamp')]    
    email = log[logcolnames.index('author')]
    logAuthors[key] = email
    authorMails.add(email)
logs = None
#input('Converted To Dict')

for key in logsd.keys():
    lg =logsd[key]
    logDates[key]=lg[logcolnames.index('timestamp')]


bugDates = {}
        
keys = ['bug','reportTimestamp','status','product','component']
vbugs,vbugscolnames = dbh.GET_ALL(table='VALIDBUGS',fields=keys,Where="  where lower(status) like '%fixed%' and (lower(product)='core')")

for line in vbugs:
            
    b = str(line[0])
            
    bugDates[b] = line[1]



f = open('q1.csv')
comps = f.readlines()[1:]
f.close()
for i in range(len(comps)):
    comps[i] = comps[i].split(',')[0].strip()




#MetricsProcessed = {}

#o = open (Name+'.txt')
#while True:
#    line = o.readline()
#    if line == '':
#        break
#    if line.find(';')<0:
#        continue
#    line = line.replace('\n','').split(';')

#    MetricsProcessed[line[0]]  = line[1]

#o.close()

ChgCompBlamed = {}
ChgCompBlamer = {}


generateHeatMaps = True

assignedComps = {}
allfidsStrAssignedComps = {}
if generateHeatMaps:
    import seaborn as sns


    saveFolMt = 'MT'
    data = []
    names = []


    if os.path.exists('htfidcmp.json'):
        fidcmp = json.load(open('htfidcmp.json'))
        data.append(fidcmp)
        names.append('fidcmp')

    if  os.path.exists('htfidcmpBlamed.json'):
        fidcmpBlamed = json.load(open('htfidcmpBlamed.json'))
        data.append(fidcmpBlamed)
        names.append('fidcmpBlamed')


    if os.path.exists('htfidcmpBlamer.json'):
        fidcmpBlamer = json.load(open('htfidcmpBlamer.json'))
        data.append(fidcmpBlamer)
        names.append('fidcmpBlamer')
    

    
    
    for index, dic in enumerate(data):
        less70 = {}
        cmpFiles = {}
        for cmpName in comps:
            cmpFiles[cmpName] = []
        assignedComps[names[index]] = None
        allfids = sorted([int(fid) for fid in dic.keys()])
        allfids = [str(fid) for fid in allfids]
        fid65Comps = [None for _ in range(len(allfids))]
        lfids = len(allfids)
        mt = np.array([[float(dic[fid][cmpName]) if cmpName in dic[fid].keys() else 0.0 for cmpName in comps] for fid in allfids])

        for i in range(len(allfids)):
            mx = np.sum(mt[i,:])
            for j in range(len(mt[i,:])):
                mt[i,j] = float(mt[i,j])/float(mx)

            ind  = np.argmax(mt[i,:])
            mx = mt[i,ind]
            if mx>1.0/3.0:
                comp = comps[ind]
                cmpFiles[comp].append(allfids[i])
                fid65Comps[i] = comp

            else:
                less70[allfids[i]] = str(mx)+'--'+comps[ind]

        for index , item in enumerate(fid65Comps):
            if index<3:
                continue
            if item == None:
                pre3=fid65Comps[index-3:index]
                indexNext = index+1
                
                while indexNext<lfids and fid65Comps[indexNext]==None:
                    indexNext+=1
                if indexNext<lfids and indexNext-index<4:
                    pre3.append(fid65Comps[indexNext])
                else:
                    print (indexNext)
                item = max(pre3,key=pre3.count)
                fid65Comps[index] = item
        assignedComps[names[index]] = fid65Comps
        print (len(less70.keys()))
        #input()


        #count = int(len(allfids)/len(comps))+1
        #for i in range(len(comps)):
            
        #    sns.set(font_scale=0.15)
        #    fig, ax = plt.subplots(figsize=(15,10))
        #    fig.tight_layout(rect=[0.03, 0.03, 1, 0.99])
        #    mti = mt[i*count:min((i+1)*count, len(allfids)):,]
        #    yticks = allfids[i*count:min((i+1)*count, len(allfids))]
        #    sns.heatmap(mti,annot=True, fmt=".2g", linewidths=0.05, linecolor='yellow', yticklabels = yticks, xticklabels = comps,ax = ax)
        #    ax.set_yticklabels(ax.get_yticklabels(), rotation = 0)
        #    ax.set_xticklabels(ax.get_xticklabels(), rotation = 90)
        #    ax.figure.savefig('PLT/'+saveFolMt+'/'+Name+'--'+names[index]+'--'+str(i)+'--.png',dpi = 500)
        #    #ax.figure.savefig('PLT/'+saveFolMt+'/'+Name+'--'+names[index]+'--'+str(i)+'--.eps',dpi = 500)


        #    plt.close('all')
        #    plt.cla()
        #    plt.clf() 
        #    ax = None
        #    mti = None
        #    fig = None

        #    print (index, names[index], i)
        
        #sns.set(font_scale=0.15)
        #ax = sns.heatmap(mt,annot=True, fmt="d", linewidths=2, linecolor='yellow')
        #ax.figure.savefig('PLT/'+saveFolMt+'/'+Name+'--'+names[index]+'--Full.png',dpi = 500)
        ##ax.figure.savefig('PLT/'+saveFolMt+'/'+Name+'--'+names[index]+'--Full.eps',dpi = 500)


        #plt.close('all')
        #plt.cla()
        #plt.clf()    
        #ax = None
    
    print ('HeatMaps generated. Press a key to continue.')
    input('')




#comps = comps[90:]
for cmpName in comps:
    allfiles = set()        
    #cmpName = 'graphics' #widget
    #cmpName = cmpName.lower()
    
    num = '---ND---'+cmpName.replace(': ','-').replace(' ','-').replace(':','-').replace('/','-')+'---Update+starDel+star'
    BlameFol = 'Blames'+Name+num+'/'

    print (BlameFol)
    


        
    
    blamedMultiParents=[]
    blamedHasMergeKeyword=[]
    
    blamedAuthors = {}
    blamerAuthors = {}
    def ExtractBlames(lines,ruBlamer,ruBlamed,Blamer,Blamed,ruFileBlamer, ruFileBlamed, FileBlamer, FileBlamed):
        for i,line in enumerate(lines):
        
            line = line.split(Helpers.bcSep)
            file = line[2].split(':')
            fid, file = int(file[0]),file[1]
            if not  Helpers.isExtValidCpp(file):
                continue

            allfiles.add(file)

            #fid = fileIDS[file]
            if fid<0:
                print ('File ', file,  ' Not Found')
                input()

            commitId = line[0]
            bugId = line[1]
            blamerAuth = logAuthors[int(commitId)]
            cmb = commitId+'--'+bugId
            fb = str(fid)+'--'+bugId

            if cmb.find(';')>0:
                print ('Error in CMB',line)
                input()
            parentNode = line[3].split('-')
            subjNode = line[4].split('-')
            blamedRev = parentNode[0].split(':')[1]
            BlameLines = parentNode[1]+'-'+parentNode[2]+','+subjNode[1]+'-'+subjNode[2]
            blamedAuth = logAuthors[int(blamedRev)]
            if blamedRev.find(';')>=0:
                print (line)
                input()
                pass
            ##RUBlamer
            if not blamerAuth in blamerAuthors.keys():
                blamerAuthors[blamerAuth] = set()
            blamerAuthors[blamerAuth].add(cmb+";"+blamedRev)

            if not blamedAuth in blamedAuthors.keys():
                blamedAuthors[blamedAuth] = set()
            blamedAuthors[blamedAuth].add(cmb+";"+blamedRev)

            parentsForBlamedRev = logsd[int(blamedRev)][logcolnames.index('parents')]
            if parentsForBlamedRev.count(',')>0:
                blamedMultiParents.append(blamedRev)
            
        
            msg = logsd[int(blamedRev)][logcolnames.index('m')]
            if msg.lower().find('merge')>=0:
                blamedHasMergeKeyword.append(blamedRev)
            
        
            #RUBlamer
            if not cmb in ruBlamer.keys():
                ruBlamer[cmb] = {}

            if blamedRev not in ruBlamer[cmb].keys():
                ruBlamer[cmb][blamedRev] = []
            ruBlamer[cmb][blamedRev].append(BlameLines)

            ##Blamer
            if not cmb in Blamer.keys():
                Blamer[cmb] = {}

            if blamedRev not in Blamer[cmb].keys():
                Blamer[cmb][blamedRev] = []
            Blamer[cmb][blamedRev].append(BlameLines)


            #RUFileBlamer
            if not fid in ruFileBlamer.keys():
                ruFileBlamer[fid] = {}


            if not commitId in ruFileBlamer[fid].keys():
                ruFileBlamer[fid][commitId] = {}

            if not bugId in ruFileBlamer[fid][commitId].keys():
                ruFileBlamer[fid][commitId][bugId] = {}

            if blamedRev not in ruFileBlamer[fid][commitId][bugId].keys():
                ruFileBlamer[fid][commitId][bugId][blamedRev] = []
            ruFileBlamer[fid][commitId][bugId][blamedRev].append(BlameLines)

            #if not cmb in ruFileBlamer[fid].keys():
            #    ruFileBlamer[fid][cmb] = {}

            #if blamedRev not in ruFileBlamer[fid][cmb].keys():
            #    ruFileBlamer[fid][cmb][blamedRev] = []
            #ruFileBlamer[fid][cmb][blamedRev].append(BlameLines)

            ##FileBlamer

            if not fid in FileBlamer.keys():
                FileBlamer[fid] = {}


            if not commitId in FileBlamer[fid].keys():
                FileBlamer[fid][commitId] = {}

            if not bugId in FileBlamer[fid][commitId].keys():
                FileBlamer[fid][commitId][bugId] = {}

            if blamedRev not in FileBlamer[fid][commitId][bugId].keys():
                FileBlamer[fid][commitId][bugId][blamedRev] = []
            FileBlamer[fid][commitId][bugId][blamedRev].append(BlameLines)


            
            #if not cmb in FileBlamer[fid].keys():
            #    FileBlamer[fid][cmb] = {}

            #if blamedRev not in FileBlamer[fid][cmb].keys():
            #    FileBlamer[fid][cmb][blamedRev] = []
            #FileBlamer[fid][cmb][blamedRev].append(BlameLines)


            ##RUBlamed
            if not blamedRev in ruBlamed.keys():
                ruBlamed[blamedRev]=set()

            if not cmb in ruBlamed[blamedRev]:
                ruBlamed[blamedRev].add(cmb)

            ##Blamed
            if not blamedRev in Blamed.keys():
                Blamed[blamedRev]=set()

            if not cmb in Blamed[blamedRev]:
                Blamed[blamedRev].add(cmb)


            #RUFileBlamed
            if not fid in ruFileBlamed.keys():
                ruFileBlamed[fid] = {}

            if not blamedRev in ruFileBlamed[fid].keys():
                ruFileBlamed[fid][blamedRev] = set()

            if not cmb in ruFileBlamed[fid][blamedRev]:
                ruFileBlamed[fid][blamedRev].add(cmb)

            ##FileBlamed

            if not fid in FileBlamed.keys():
                FileBlamed[fid] = {}

            if not blamedRev in FileBlamed[fid].keys():
                FileBlamed[fid][blamedRev] = set()

            if not cmb in FileBlamed[fid][blamedRev]:
                FileBlamed[fid][blamedRev].add(cmb)




    rBlamed = {}
    rBlamer = {}
    uBlamed = {}
    uBlamer = {}
    rFileBlamed = {}
    rFileBlamer = {}
    uFileBlamed = {}
    uFileBlamer = {}


    Blamed = {}
    Blamer = {}
    FileBlamed = {}
    FileBlamer = {}

    FutureBugs = {}
    BlamedForBug = {}
    for file in os.listdir(BlameFol):
        if file.startswith('RemovedBlames-'):
            f= open(BlameFol+file,encoding='utf8')
            lines = [line for line in f.read().split(Helpers.bcSep+'\n\n\n') if len(line)>3]
            f.close()   
            print ('Removed: For file',file,'Count Lines:',len(lines))
            ExtractBlames(lines,rBlamer,rBlamed,Blamer,Blamed,rFileBlamer, rFileBlamed, FileBlamer, FileBlamed)
        elif file.startswith ('UpdatedBlames-'):
            f= open(BlameFol+file,encoding='utf8')
            lines =[line for line in  f.read().split(Helpers.bcSep+'\n\n\n') if len(line)>3]
            f.close()
            print ('Updated: For file',file,'Count Lines:',len(lines))
            ExtractBlames(lines,uBlamer,uBlamed,Blamer,Blamed,uFileBlamer, uFileBlamed, FileBlamer, FileBlamed)

        


    print ('RBlamer:',len(rBlamer.keys()),'RBlamed:',len(rBlamed.keys()))
    print ('UBlamer:',len(uBlamer.keys()),'UBlamed:',len(uBlamed.keys()))
    print ('Blamer:',len(Blamer.keys()),'Blamed:',len(Blamed.keys()))


    #input('Data for Comp, loaded....')
    


    uniqC = set ()
    uniqB = set()
    for idid in Blamer.keys():
        idid = idid.split('--')
        uniqC.add(idid[0])
        uniqB.add(idid[1])
    print ('Unique Blamer Changes',len(uniqC),'Unique Blamer Bugs',len(uniqB))

    print ('Blamed MultiParents (all,unique): ',len(blamedMultiParents),len(set(blamedMultiParents)))
    print ('Blamed HasMergeKeyword (all,unique): ',len(blamedHasMergeKeyword),len(set(blamedHasMergeKeyword)))
    print ('Count Unique Authors: ',len(authorMails))
    print ('Blamed and Blamer Authors Counts:',len(blamedAuthors.keys()), len(blamerAuthors.keys()),len(set.intersection(set(blamerAuthors.keys()),set(blamedAuthors.keys()))))

    allchanges = set()

    for cmb in Blamer.keys():
        chg = cmb.split('--')[0]
        vals = set(Blamer[cmb].keys())
        vals.add(chg)
        for chg in vals:
            if not chg in allchanges:
                allchanges.add(chg)

    
    G=nx.DiGraph()
    for nd in allchanges:
        G.add_node(nd)

    for cmb in Blamer.keys():
        fromNode = cmb.split('--')[0]
        vals = set(Blamer[cmb].keys())
        for toNode in vals:
            G.add_edge(fromNode,toNode)

    #nx.draw_random(G)
    #plt.show()

    pr = nx.pagerank(G,alpha=0.1)
    prlst = [(pr[key],key) for key in pr.keys()]
    prlst = sorted(prlst,key=lambda tup: tup[0],reverse=True)



    #for i in range(len(prlst)-1):
    #    for j in range(i+1,len(prlst)):
    #        if prlst[i][0]<prlst[j][0]:
    #            prlst[i],prlst[j]=prlst[j],prlst[i]

    print ('\n\n\nTop 20 PageRanks:',prlst[:20],'\n\n\n\n')
    
    prTop = {p[1] for p in prlst[:int(len(prlst)/10)]}
    print ([p+(logsd[int(p[1])][logcolnames.index('cid')],) for p in prlst[:20]],'\n\n\n\n')

    print ('Count PageRank Links:',len(prlst),'\n\n\n')

    #input('Press a key')

    print ('Graph Size:',len(G.nodes()))

    BlamedCounts = []
    for key in Blamed.keys():
        BlamedCounts.append(len(Blamed[key]))   
    print (len(Blamed.keys()),' changes are blamed by Sum,Mean,STD',np.sum(BlamedCounts),np.mean(BlamedCounts),np.std(BlamedCounts))

    BlamerCounts = []
    for key in Blamer.keys():
        BlamerCounts.append(len(Blamer[key]))
    
    print (len(Blamer.keys()),' changes are blaming Sum,Mean,STD',np.sum(BlamerCounts),np.mean(BlamerCounts),np.std(BlamerCounts))

    print ('\n\n\n')

    BlamedList = [(len(Blamed[key]),key) for key in Blamed.keys()]
    BlamedList = sorted(BlamedList,key=lambda tup: tup[0],reverse=True)

    FileBlamedList = {fid:[(len(FileBlamed[fid][key]),key) for key in FileBlamed[fid].keys()] for fid in FileBlamed.keys()}

    #for i in range(len(BlamedList)-1):
    #    for j in range(i+1,len(BlamedList)):
    #        if BlamedList[i][0]<BlamedList[j][0]:
    #            BlamedList[i],BlamedList[j]=BlamedList[j],BlamedList[i]
    print ('Top 20 Blamed', BlamedList[:20])
    print ('\n\n\n')




    bl25 = {p[1] for p in BlamedList[:int(len(BlamedList)/4)]}
    cnt = 0
    for b in bl25:
        if b in prTop:
            cnt+=1
    print ('Blamed:',cnt, len(bl25),len(prTop),len(prlst),'\n\n\n')



    BlamerList = [(len(Blamer[key].keys()),key) for key in Blamer.keys()]
    BlamerList = sorted(BlamerList,key=lambda tup: tup[0],reverse=True)


    FileBlamerList = {fid:[(np.sum([len(FileBlamer[fid][key][b].keys()) for  b in FileBlamer[fid][key]]),key) for key in FileBlamer[fid].keys()] for fid in FileBlamer.keys()}

    
    print ('\n\n\n\nTop 20 Blamers', BlamerList[:20])

    bl25 = {p[1].split('--')[0] for p in BlamerList[:int(len(BlamerList)/4)]}
    cnt = 0
    for b in bl25:
        if b in prTop:
            cnt+=1
    print ('Blamer:',cnt, len(bl25),len(prTop),len(prlst),'\n\n\n')



    BLIST = [x[0] for x in BlamerList]
    if len(BLIST)>0:
        try:
            pass
            #plt.figure(figsize=(10,10))
            #plt.subplots_adjust(wspace=0, hspace=0)
            #plt.xlim((0,2))
            #plt.ylim((0,max(BLIST)+5))
            #plt.tight_layout()
            #prt=plt.violinplot(BLIST,showmeans=True,showmedians=True)
            #prt['cmeans'].set_facecolor('black')
            #prt['cmeans'].set_edgecolor('black')
            #prt['cmeans'].set_linestyle('--')
            #prt['cmeans'].set_linewidth(3)

            #plt.text(0.7,np.mean(BLIST),'Mean:%.2f'%(np.mean(BLIST)))
            #plt.text(1.1,np.median(BLIST),'Median:%.2f'%(np.median(BLIST)))
            #plt.savefig('PLT/'+BlameFol[:-1]+'0Blamers.png',dpi = 500)
            #plt.savefig('PLT/'+BlameFol[:-1]+'0Blamers.eps',dpi = 500)
            #plt.close('all')
            #plt.cla()
            #plt.clf()
        except Exception as ex:
            print('Not suitable for ViolinPlots', ex)
        print ('\n\n\n')



    CntFtBugs = [(len(set([cmb.split('--')[1] for cmb in Blamed[key]])),key) for key in Blamed.keys()]
    CntFtBugs = sorted(CntFtBugs,key=lambda tup: tup[0],reverse=True)
    
    print ('Top 20 CountFutureBugs', CntFtBugs[:20])
    print ('\n\n\n')

    bl25 = {p[1] for p in CntFtBugs[:int(len(CntFtBugs)/4)]}
    cnt = 0
    for b in bl25:
        if b in prTop:
            cnt+=1
    print ('BlamedCountFuture:',cnt, len(bl25),len(prTop),len(prlst),'\n\n\n')



    BLIST = [x[0] for x in CntFtBugs]

    if len(BLIST)>0:
        try:
            pass
            #print (len(BLIST),np.mean(BLIST))
            #plt.figure(figsize=(10,10))
            #plt.subplots_adjust(wspace=0, hspace=0)

            #plt.xlim((0,2))
            #plt.ylim((0,max(BLIST)+5))
            #plt.tight_layout()
            #prt=plt.violinplot(BLIST,showmeans=True,showmedians=True)
            #prt['cmeans'].set_facecolor('black')
            #prt['cmeans'].set_edgecolor('black')
            #prt['cmeans'].set_linestyle('--')
            #prt['cmeans'].set_linewidth(3)

            #plt.text(0.7,np.mean(BLIST),'Mean:%.2f'%(np.mean(BLIST)))
            #plt.text(1.1,np.median(BLIST),'Median:%.2f'%(np.median(BLIST)))
            #plt.savefig('PLT/'+BlameFol[:-1]+'0Blamed.png',dpi = 500)
            #plt.savefig('PLT/'+BlameFol[:-1]+'0Blamed.eps',dpi = 500)
            #plt.close('all')
            #plt.cla()
            #plt.clf()
        except Exception as ex:
            print('Not suitable for ViolinPlots',ex)
    print ('Count Future Bugs: Sum,Mean,STD ',np.sum([b[0] for b in CntFtBugs]),np.mean([b[0] for b in CntFtBugs]),np.std([b[0] for b in CntFtBugs]),'\n\n\n')

    for key in Blamed.keys():
        FutureBugs[key] = list({cmb.split('--')[1] for cmb in Blamed[key]})

        for cmb in  Blamed[key]:
            b = cmb.split('--')[1]
            if not b in BlamedForBug.keys():
                BlamedForBug[b] = set()
            BlamedForBug[b].add(cmb.split('--')[0])


    timespans = []
    timespansNoz = []
    ids = []

    for key in FutureBugs.keys():
        bds = sorted([bugDates[b] for b in FutureBugs[key]])

        if len(bds)>1:
            timespans.append((datetime.datetime.fromtimestamp(bds[-1])-datetime.datetime.fromtimestamp(bds[0])).total_seconds()/86400)
            timespansNoz.append(timespans[-1])
            ids.append(key)
        else:
            timespans.append(0)

    print ('2 Timespan of Bugs: Mean,STD,Median ',np.mean(timespans),np.std(timespans),np.median(timespans))
    print ('2 Timespan of Bugs (for multibugs only): Mean,STD ,Median',np.mean(timespansNoz),np.std(timespansNoz),np.median(timespansNoz))
    print ('2 Count Multi Bug:', len(timespansNoz))
    print ('2 Count One or Multi Bug:', len(timespans))
    mad = DPLIB.MAD(timespansNoz)
    umad = mad+np.median(timespansNoz)
    lmad = np.median(timespansNoz)-mad
    if len(timespansNoz)>0:
        print ('2 MAD, Median , UMAD , Percent>UMAD, Median Filtered:', 
            mad,np.median(timespansNoz),umad,'%.2f' %(100*len([t for t in timespansNoz if t>umad])/len(timespansNoz)), np.median([t for t in timespansNoz if t>umad]))
    else:
        print ('2 MAD, Median , UMAD , Percent>UMAD, Median Filtered:', 
            mad,np.median(timespansNoz),umad,'PERCENT UNDEF', np.median([t for t in timespansNoz if t>umad]))
    #numfiles= [(key,len(logsd[int(key)][logcolnames.index('files')].split('---')[:-1])) for index,key in enumerate(ids) if timespansNoz[index]>umad]
    #print (numfiles)
    if len(timespansNoz)>0:
        try:

            pass
            #plt.figure(figsize=(10,10))
            #plt.subplots_adjust(wspace=0, hspace=0)
            #plt.xlim((0,2))
            #plt.ylim((0,max(timespansNoz)+5))
            #plt.tight_layout()
            #prt=plt.violinplot(timespansNoz,showmeans=True,showmedians=True)
            #prt['cmeans'].set_facecolor('black')
            #prt['cmeans'].set_edgecolor('black')
            #prt['cmeans'].set_linestyle('--')
            #prt['cmeans'].set_linewidth(3)

            #plt.plot([0.7,1.3],[umad,umad])
            #plt.plot([0.7,1.3],[lmad,lmad])
            #plt.text(1.5,umad,'UMAD:%.2f'%(umad))
            #plt.text(0.4,lmad,'LMAD:%.2f'%(lmad))
            #plt.text(0.7,np.mean(timespansNoz),'Mean:%.2f'%(np.mean(timespansNoz)))
            #plt.text(1.1,np.median(timespansNoz),'Median:%.2f'%(np.median(timespansNoz)))
            #plt.savefig('PLT/'+BlameFol[:-1]+'2tsbugs.png',dpi = 500)
            #plt.savefig('PLT/'+BlameFol[:-1]+'2tsbugs.eps',dpi = 500)
            #plt.close('all')
            #plt.cla()
            #plt.clf()
        except Exception as ex:

            print ('Not Suitable for ViolinPlots',ex)
    print ('\n\n\n')

    timespans = []
    timespansNoz = []
    for key in BlamedForBug.keys():
        bds = sorted([logDates[int(l)] for l in BlamedForBug[key]])

        if len(bds)>1:
            timespans.append((datetime.datetime.fromtimestamp(bds[-1])-datetime.datetime.fromtimestamp(bds[0])).total_seconds()/86400)
            timespansNoz.append(timespans[-1])
        else:
            timespans.append(0)


    print ('3 Timespan of Changes: Mean,STD,Median ',np.mean(timespans),np.std(timespans),np.median(timespans))
    print ('3 Timespan of Changes (for multibugs only): Mean,STD ,Median',np.mean(timespansNoz),np.std(timespansNoz),np.median(timespansNoz))
    print ('3 Count Multi Change:', len(timespansNoz))
    print ('3 Count One or Multi Change:', len(timespans))
    mad = DPLIB.MAD(timespansNoz)
    umad = mad+np.median(timespansNoz)
    lmad = np.median(timespansNoz)-mad

    if len(timespansNoz)>0:
        print ('3 MAD, Median , UMAD , Percent>UMAD, Median Filtered:',
            mad,np.median(timespansNoz),umad,'%.2f' %(100*len([t for t in timespansNoz if t>umad])/len(timespansNoz)), np.median([t for t in timespansNoz if t>umad]))
    else:
        print ('3 MAD, Median , UMAD , Percent>UMAD, Median Filtered:',
            mad,np.median(timespansNoz),umad,'PERCENT UNDEF', np.median([t for t in timespansNoz if t>umad]))
    print ('\n\n\n')


    if len(timespansNoz)>0:
        try:

            pass
            #plt.figure(figsize=(10,10))
            #plt.subplots_adjust(wspace=0, hspace=0)
            #plt.xlim((0,2))
            #plt.ylim((0.1,max(timespansNoz)+5))
            #plt.tight_layout()
        
            #prt=plt.violinplot(timespansNoz,showmeans=True,showmedians=True)
        

            #prt['cmeans'].set_facecolor('black')
            #prt['cmeans'].set_edgecolor('black')
            #prt['cmeans'].set_linestyle('--')
            #prt['cmeans'].set_linewidth(3)

            #plt.plot([0.7,1.3],[umad,umad])
            #plt.plot([0.7,1.3],[lmad,lmad])
            #plt.text(1.5,umad,'UMAD:%.2f'%(umad))
            #plt.text(0.4,lmad,'LMAD:%.2f'%(lmad))
            #plt.text(0.7,np.mean(timespansNoz),'Mean:%.2f'%(np.mean(timespansNoz)))
            #plt.text(1.1,np.median(timespansNoz),'Median:%.2f'%(np.median(timespansNoz)))
            #plt.savefig('PLT/'+BlameFol[:-1]+'3tschg.png',dpi = 500)
            #plt.savefig('PLT/'+BlameFol[:-1]+'3tschg.eps',dpi = 500)
            #plt.close('all')
            #plt.cla()
            #plt.clf()

        except Exception as ex: 
            print ('Data can not be represented in ViolinPlots', ex)


    ###################Blamed File DS

    if not 'FileJustBlamed' in ChgCompBlamed.keys():
        ChgCompBlamed['FileJustBlamed'] = {}


    
    allChangesets = set()

    fids = set()
    for fid in FileBlamedList.keys():
        fids.add(fid)

    for fid in FileBlamerList.keys():
        fids.add(fid)

    for fid in fids:
        allChgSet = set()
        
        #BlamedChgLIST = FileBlamed[fid]

        
        #BlamerChgLIST = FileBlamerList[fid]

        if not fid in fidcmpBlamer.keys():
            fidcmpBlamer[fid] = {}
        

        if not fid in fidcmpBlamed.keys():
            fidcmpBlamed[fid] = {}

        if not fid in fidcmp.keys():
            fidcmp[fid] = {}


        for chg in FileBlamed[fid].keys():
            allChgSet.add(chg)

        for chg in FileBlamer[fid].keys():
            allChgSet.add(chg)

        
        i=0 
        for rev in allChgSet:
            blamedCount = 0
            blamerCount = 0

            if rev in FileBlamed[fid].keys():
                blamedCount = len(FileBlamed[fid][rev])
                if cmpName not in fidcmpBlamed[fid].keys():
                    fidcmpBlamed[fid][cmpName]=1
                else:
                    fidcmpBlamed[fid][cmpName]+=1

                if cmpName not in fidcmp[fid].keys():
                    fidcmp[fid][cmpName]=1
                else:
                    fidcmp[fid][cmpName]+=1


            if rev in FileBlamer[fid].keys():
                for b in FileBlamer[fid][rev].keys():
                    blamerCount+=len(FileBlamer[fid][rev][b].keys())
                if cmpName not in fidcmpBlamer[fid].keys():
                    fidcmpBlamer[fid][cmpName]=1
                else:
                    fidcmpBlamer[fid][cmpName]+=1

                if cmpName not in fidcmp[fid].keys():
                    fidcmp[fid][cmpName]=1
                else:
                    fidcmp[fid][cmpName]+=1


            allChangesets.add(MetricsChgData[str(fid)][rev]+';'+str(fid)+';'+rev+':'+str(blamedCount)+'@'+str(blamerCount))
            
            key = str(fid)+'-'+rev
            if  not key in ChgCompBlamed['FileJustBlamed'].keys():
                ChgCompBlamed['FileJustBlamed'][key] = set()
                ChgCompBlamed['FileJustBlamed'][key].add(cmpName)
            else:
                ChgCompBlamed['FileJustBlamed'][key].add(cmpName)
            if i%50==0:
                print (i)
            i+=1

        
    json.dump(sorted(list(allChangesets)),open('Datasets/'+BlameFol[:-1]+'--File---JustBlamedAndBlamerChangeSets.txt','w'))

    

    

o = open(Name+'--File--ChgCompBlamedJustBlamed.txt','w')
for key in ChgCompBlamed['FileJustBlamed'].keys():
    o.write('%s;%s;%d\n'%(key,ChgCompBlamed['FileJustBlamed'][key],len(ChgCompBlamed['FileJustBlamed'][key])))
o.close()


if not os.path.exists('htfidcmp.json'):
    json.dump(fidcmp,open('htfidcmp.json','w'))

if not os.path.exists('htfidcmpBlamed.json'):
    json.dump(fidcmpBlamed,open('htfidcmpBlamed.json','w'))

if not os.path.exists('htfidcmpBlamer.json'):
    json.dump(fidcmpBlamer,open('htfidcmpBlamer.json','w'))

