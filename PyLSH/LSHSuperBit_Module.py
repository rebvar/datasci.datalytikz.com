import random
import copy
import numpy as np
from .LSH_Module import LSH

class LSHSuperBit(LSH):

    def __init__(self, **kwargs):

        self.sb = None
        if 'stages' in kwargs.keys() and 'buckets' in kwargs.keys() and 'dimensions' in kwargs.keys():

            super(LSHSuperBit,self).__init__(stages=kwargs['stages'], buckets=kwargs['buckets'])

            code_length = int(self.stages * self.buckets / 2);
            superbit = self.computeSuperBit(self.stages, self.buckets, kwargs['dimensions']);
            if 'seed' in kwargs.keys():
                self.sb = SuperBit(d=kwargs['dimensions'], n=superbit, l=code_length / superbit, seed=kwargs['seed'])
            else:
                self.sb = SuperBit(d=kwargs['dimensions'], n=superbit, l=code_length / superbit)
    


    def computeSuperBit(self,stages, buckets, dimensions):

        
        code_length = int(stages * buckets / 2)
        superbit = dimensions
        while superbit >= 1:
            if (code_length % superbit == 0):
                break            
            superbit-=1        

        if (superbit == 0):
            raise Exception("Superbit is 0 with parameters: s=" + str(stages)+ " b=" + str(buckets) + " n=" + str(dimensions))
        
        return superbit    

    def hash(self,vector):
        return self.hashSignatureBool(self.sb.signature(vector))

    



class SuperBit:

    DEFAULT_CODE_LENGTH = 10000

    def __init__(self, **kwargs):
        self.hyperplanes = []
         

        if 'd' in kwargs.keys() and 'n' in kwargs.keys() and 'l' in kwargs.keys() and 'seed' in kwargs.keys():
             self.SB(kwargs['d'],kwargs['n'],kwargs['l'],random.Random(kwargs['seed']))

        elif 'd' in kwargs.keys() and 'n' in kwargs.keys() and 'l' in kwargs.keys():
            self.SB(kwargs['d'],kwargs['n'],kwargs['l'], random.Random())
        elif 'd'  in kwargs.keys():
            self.SB(kwargs['d'],kwargs['d'], SuperBit.DEFAULT_CODE_LENGTH/kwargs['d'], random.Random())


    def SB(self, d, n, l, rand):
        if (d <= 0):
            raise Exception("Dimension d must be >= 1")
        

        if (n < 1 or n > d):
            raise Exception("Super-Bit depth N must be 1 <= N <= d");
        

        if (l < 1):
            raise Exception("Number of Super-Bit L must be >= 1")
        
        code_length = int( n * l);

        v = []

        for i in range(code_length):
            vector = []
            for j in range(d):
                vector.append(rand.gauss(0,1))
            

            vector = SuperBit.normalize(vector)
            v.append(vector)        

        w = [[0 for i in range(d)] for _ in range(code_length)]

        for i in range(int(l)):
            for j in range(1,n+1):
                
                for k in range(d):
                    w[i * n + j - 1][k] = v[i * n + j - 1][k]
                
                for k in range(1,j):
                    w[i * n + j - 1] = SuperBit.sub(w[i * n + j - 1],SuperBit.product(
                        SuperBit.dotProduct(w[i * n + k - 1],v[ i * n + j - 1]),w[i * n + k - 1]))                
                SuperBit.normalize(w[i * n + j - 1])
                    
        self.hyperplanes = w;
    

    
    
    def signature(self,vector):
        sig = []
        if isinstance(vector,list):
            for i in range(len(self.hyperplanes)):            
                sig.append(SuperBit.dotProduct(vector, self.hyperplanes[i]) >=0)
        else:
            for i in range(len(self.hyperplanes)):
                sig.append(vector.dotProduct(self.hyperplanes[i]) >=0)
        return sig

    def similarity(self,sig1,sig2):

        agg = 0
        for i in range(len(sig1)):
            if (sig1[i] == sig2[i]):
                agg+=1                    
        agg = agg / len(sig1)
        return np.cos((1 - agg) * np.pi)




    def getHyperplanes(self):
        return self.hyperplanes
    

    def cosineSimilarity(v1, v2):
        return SuperBit.dotProduct(v1, v2) / (SuperBit.norm(v1) * SuperBit.norm(v2))
    

    def product(x, v):
        r = []
        for i in range(len(v)):
            r.append( x * v[i])        
        return r

    def sub(a, b):
        r = []
        for i in range(len(a)):
            r.append(a[i] - b[i])        
        return r

    def normalize(vector):
        try:
            nrm = SuperBit.norm(vector)
        
            for i in range(len(vector)):
                vector[i] = vector[i] / nrm
        
            return vector
        except Exception as ex:
            print (ex)
            input()


    
    def norm(vec):        
        return np.sqrt(sum([v*v for v in vec]));    

    def dotProduct(v1,v2):
        return sum([float(v1[i])*float(v2[i]) for i in range(len(v1))])            
