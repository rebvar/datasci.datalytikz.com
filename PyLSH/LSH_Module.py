import numpy as np

class LSH(object):

    LARGE_PRIME =  433494437
    MAX_INT = 2147483647
    DEFAULT_STAGES = 3;
    DEFAULT_BUCKETS = 10;
    def __init__(self, **kwargs):
        self.stages = LSH.DEFAULT_STAGES
        self.buckets = LSH.DEFAULT_BUCKETS

        if 'stages' in kwargs.keys() and 'buckets' in kwargs.keys():
            self.stages = kwargs['stages']
            self.buckets = kwargs['buckets']



    def hashSignature(self,signature):
        
        hash = [0 for _ in range(self.stages)]
        
        rows =int( len(signature) / self.stages)

        for i in range(len(signature)):
            stage = min(int(i / rows), self.stages - 1)
            hash[stage] = int((hash[stage] + int(signature[i]) * LSH.LARGE_PRIME) % self.buckets)

        return hash    

    
    def hashSignatureBool(self,signature):

        
        acc = [0 for _ in range(self.stages)]
        
        rows = int(len(signature) / self.stages)

        for i in range(len(signature)):
            v = 0
            if (signature[i]):
                v = (i + 1) * LSH.LARGE_PRIME

            j = min(int (float(i)/rows), self.stages - 1)
            acc[j] = (acc[j] + v) % LSH.MAX_INT

        r = []
        for i in range(self.stages):
            r.append(int(acc[i] % self.buckets))

        return r


