import numpy as np
import random
import copy
from .LSH_Module import LSH

class LSHMinHash(LSH):

    THRESHOLD = 0.5

    def __init__(self, **kwargs):
        mh = None
    
        if 's' in kwargs.keys() and 'b' in kwargs.keys() and 'n' in kwargs.keys():
            super(LSHMinHash,self).__init__(stages = kwargs['s'], buckets = kwargs['b'])
            signature_size = self.computeSignatureSize(kwargs['s'],kwargs['n'])
            if 'seed' in kwargs.keys():
                self.mh = MinHash(size = signature_size, dict_size = kwargs['n'],seed = kwargs['seed']);
            else:
                self.mh = MinHash(size = signature_size, dict_size = kwargs['n']);

    def computeSignatureSize(self,s,n):
        r = int(np.ceil(np.log(1.0 / s) / np.log(LSHMinHash.THRESHOLD)) + 1)
        return r * s    

    
    def hash(self,vector):
        return self.hashSignature(self.mh.signature(vector))   


    def getCoefficients(self):
        return self.mh.getCoefficients()

class MinHash:

    def jaccardIndex(s11,s22):

        if isinstance(s11,list):
            s1 = MinHash.convert2Set(s11)
        else:
            s1 = s11
        if isinstance(s22,list):
            s2 = MinHash.convert2Set(s22)
        else:
            s2 = s22
        intersection = s1.intersection(s2)
        
        union = s1.union(s2)
        
        if (len(union)==0):
            return 0;
        
        return float(len(intersection)) / float(len(union))
    
    def size(error):
        if (error < 0 or error > 1):
            raise Exception("error should be in [0 .. 1]")
        
        return int (1 / (error * error))
    

    def __init__(self,**kwargs):
        self.n = 0
        self.hash_coefs = None

        self.dict_size = 0

        if 'size' in kwargs.keys() and 'dict_size' in kwargs.keys() and 'seed' in kwargs.keys():            
            self.init(kwargs['size'],kwargs['dict_size'],random.Random(kwargs['seed']))
        elif 'error' in kwargs.keys() and 'dict_size' in kwargs.keys() and 'seed' in kwargs.keys():            
            self.init(MinHash.size(kwargs['error']),kwargs['dict_size'], random.Random(kwargs['seed']))
        elif 'size' in kwargs.keys() and 'dict_size' in kwargs.keys():
            self.init(kwargs['size'],kwargs['dict_size'], random.Random())
        elif 'error' in kwargs.keys() and 'dict_size' in kwargs.keys():
            self.init(MinHash.size(kwargs['error']),kwargs['dict_size'], random.Random())
    
    
    
    def signature(self,s):
        
        
        if isinstance(s, list):
            if (len(s) != self.dict_size):
                raise Exception("Size of array should be dict_size")        
            s2 = MinHash.convert2Set(s)

        else:
            s2 = s
        sig = [np.inf for _ in range(self.n)]

        
        lst = sorted(list(s2))
        
        for r in lst:

            
            for i in range(self.n):
                sig[i] = min(sig[i],self.h(i, r))                    
        return sig;


    def similarity(self,sig1, sig2):
        if (len(sig1) != len(sig2)):
            raise Exception("Size of signatures should be the same")
        

        sim = 0
        for i in range(len(sig1)):
            if (sig1[i] == sig2[i]):
                sim += 1                    

        return sim / len(sig1)

    
    def error(self):
        return 1.0 / np.sqrt(self.n)
    

    
    def init(self, size, dict_size, rand):
        if (size <= 0):
            raise Exception("Signature size should be positive")
        

        if (dict_size <= 0):
            raise Exception("Dictionary size (or vector size) should be positive")
        
        self.dict_size = dict_size;
        self.n = size;

        
        
        self.hash_coefs = []
        for i in range(self.n):
            self.hash_coefs.append([rand.randint(0,self.dict_size-1),rand.randint(0,self.dict_size-1)])
            
    def h(self,i,x):
        return int((self.hash_coefs[i][0] * int(x) + self.hash_coefs[i][1]) % self.dict_size)
    

    
    def getCoefficients(self):
        return self.hash_coefs   



    def convert2Set(array):
        s = set()
        for i in range(len(array)):
            if (array[i]):
                s.add(i)                    
        return s
    
