
from .Helpers import Helpers
from .DBHelper import DBHelper
import datetime
import networkx as nx
import matplotlib.pyplot as plt

import os
import matplotlib
import numpy as np


Name = 'KIM'
num = '5'
BlameFolp = 'Blames'+num+Name+'AudioVideoAllLikePercentUpdate+starDel+/'
BlameFolps = 'Blames'+num+Name+'AudioVideoAllLikePercentDel+star/'
bugDates = {}
logDates = {}
dbh = DBHelper()
logAuthors={}
keys = ['bug','reportTimestamp','status','product','component']
quer = "select "+','.join(keys)+" from VALIDBUGS where status like '%fixed%' and (product = 'Core' or product='core')"
vbugs,vbugscolnames = dbh.GET_ALL(table='VALIDBUGS',fields = keys)


for line in vbugs:
            
    b = str(line[0])
            
    bugDates[b] = line[1]

logs,logcolnames = dbh.GET_ALL(table='LOGS')

blamedMultiParents=[]
blamedHasMergeKeyword=[]
logsd = {}
authorMails = set()
blamedAuthors = {}
blamerAuthors = {}
for log in logs:
    key = log[logcolnames.index('locid')]
    logsd[key]=log
    logDates[key]=log[logcolnames.index('timestamp')]    
    email = log[logcolnames.index('author')]
    logAuthors[key] = email
    

    authorMails.add(email)
logs = None
input('Converted To Dict')

for key in logsd.keys():
    lg =logsd[key]
    logDates[key]=lg[logcolnames.index('timestamp')]    


def ExtractBlames(lines,ruBlamer,ruBlamed):
    for i,line in enumerate(lines):
        
        line = line.split(Helpers.bcSep)
        file = line[2]
        if not  Helpers.isExtValidCpp(file):
            continue

        commitId = line[0]
        bugId = line[1]
        blamerAuth = logAuthors[int(commitId)]
        cmb = commitId+'--'+bugId
        lcode1 = line[-2]
        lcode2 = line[-1]

        if cmb.find(';')>0:
            pass
        parentNode = line[3].split('-')
        subjNode = line[4].split('-')
        blamedRev = parentNode[0]
        BlameLines = parentNode[1]+'-'+parentNode[2]+','+subjNode[1]+'-'+subjNode[2]
        BlameLinesCodes = lcode1+'---'+lcode2
        if blamedRev.find(';')>=0:
            print (line)
            input()
            pass
        
        #blamedAuth = logAuthors[int(blamedRev)]
        #if not blamerAuth in blamerAuthors.keys():
        #    blamerAuthors[blamerAuth] = set()
        #blamerAuthors[blamerAuth].add(cmb+";"+blamedRev)

        #if not blamedAuth in blamedAuthors.keys():
        #    blamedAuthors[blamedAuth] = set()
        #blamedAuthors[blamedAuth].add(cmb+";"+blamedRev)

        #parentsForBlamedRev = logsd[int(blamedRev)][logcolnames.index('parents')]
        #if parentsForBlamedRev.count(',')>0:
        #    blamedMultiParents.append(blamedRev)
            
        
        #msg = logsd[int(blamedRev)][logcolnames.index('m')]
        #if msg.lower().find('merge')>=0:
        #    blamedHasMergeKeyword.append(blamedRev)
            
        
        ##RUBlamer
        if not cmb in ruBlamer.keys():
            ruBlamer[cmb] = {}

        if blamedRev not in ruBlamer[cmb].keys():
            ruBlamer[cmb][blamedRev] = []
        ruBlamer[cmb][blamedRev].append(BlameLines+';;;;'+BlameLinesCodes)

        ###Blamer
        #if not cmb in Blamer.keys():
        #    Blamer[cmb] = {}

        #if blamedRev not in Blamer[cmb].keys():
        #    Blamer[cmb][blamedRev] = []
        #Blamer[cmb][blamedRev].append(BlameLines)


        ##RUBlamed
        if not blamedRev in ruBlamed.keys():
            ruBlamed[blamedRev]=set()

        if not cmb in ruBlamed[blamedRev]:
            ruBlamed[blamedRev].add(cmb+'-'+file+'---'+lcode2)

        ##Blamed
        #if not blamedRev in Blamed.keys():
        #    Blamed[blamedRev]=set()

        #if not cmb in Blamed[blamedRev]:
        #    Blamed[blamedRev].add(cmb)
      
    




rBlamed1 = {}
rBlamer1 = {}
rBlamed2 = {}
rBlamer2 = {}


for file in os.listdir(BlameFolp):
    if file.startswith('RemovedBlames-'):
        f= open(BlameFolp+file,encoding='utf8')
        lines = [line for line in f.read().split(Helpers.bcSep+'\n\n\n') if len(line)>3]
        f.close()
        print ('Removed: For file',file,'Count Lines:',len(lines))
        ExtractBlames(lines,rBlamer1,rBlamed1)
        
for file in os.listdir(BlameFolps):
    if file.startswith('RemovedBlames-'):
        f= open(BlameFolps+file,encoding='utf8')
        lines = [line for line in f.read().split(Helpers.bcSep+'\n\n\n') if len(line)>3]
        f.close()
        print ('Removed: For file',file,'Count Lines:',len(lines))
        ExtractBlames(lines,rBlamer2,rBlamed2)
    

print ('P :RBlamer1:',len(rBlamer1.keys()),'RBlamed1:',len(rBlamed1.keys()))
print ('PS:RBlamer2:',len(rBlamer2.keys()),'RBlamed2:',len(rBlamed2.keys()))

#print ('Blamed MultiParents (all,unique): ',len(blamedMultiParents),len(set(blamedMultiParents)))
#print ('Blamed HasMergeKeyword (all,unique): ',len(blamedHasMergeKeyword),len(set(blamedHasMergeKeyword)))
#print ('Count Unique Authors: ',len(authorMails))
#print ('Blamed and Blamer Authors Counts:',len(blamedAuthors.keys()), len(blamerAuthors.keys()),len(set.intersection(set(blamerAuthors.keys()),set(blamedAuthors.keys()))))

allBlamed1 = set(rBlamed1.keys())
allBlamed2 = set(rBlamed2.keys())
print ('Union:',len(set.union(allBlamed1,allBlamed2)))
print ('Inter:',len(set.intersection(allBlamed1,allBlamed2)))

blamedonlyps = {b:rBlamed2[b] for b in rBlamed2.keys() if not b in rBlamed1.keys()}
print (len(blamedonlyps.keys()))
