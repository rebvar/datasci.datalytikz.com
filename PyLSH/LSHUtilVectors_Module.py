import numpy as np


class SparseBooleanVector:
    
    def __init__(self, par = None):
        self.keys = []        
        self.size = 0
        
        if isinstance(par,dict):
            self.SBVHM(par)
        elif isinstance(par, list):
            self.SBVArr(par)
        elif par!=None:
            self.SBV(par)
        else:
            self.SBV()

    def SBV(self,size):
        self.keys = [0 for _ in range(size)]
        self.size = size
    
    def SBV(self):
        self.SBV(20)
    
    
    def SBVHM(self, hm):
        sorted_keys = sorted(list(hm.keys()))
        self.SBV(len(sorted_keys))
        
        self.size = 0
        for key in sorted_keys:
            self.keys.append(key)
            self.size+=1
        
    
    
    def SBVArr(self,array):                
        self.keys = []
        self.size = 0
        for i in range(len(array)):
            if array[i]:
                self.keys.append(i);
                self.size+=1    
    
            
    def jaccard(self, other):
        intersection = self.intersection(other);
        return float(intersection) / (self.size() + other.size() - intersection)    
    
    
    def union(self,other):
        return self.size() + other.size() - self.intersection(other);
    
    
    def intersection(self,other):
        agg = 0;
        i = 0;
        j = 0;
        while (i < len(self.keys)  and j < len(other.keys)):
            k1 = self.keys[i]
            k2 = other.keys[j]

            if (k1 == k2):
                agg+=1
                i+=1
                j+=1

            elif (k1 < k2):
                i+=1
                
            else:
                j+=1
            
        
        return agg    
    
    
    def toString(self):
        r = ""
        for i in range(self.size()):
            r += str(self.keys[i]) + ":" + str(self.keys[i]) + " "
        
        
        return r;
    

    
    def size(self):
        return len(self.keys())    




class SparseDoubleVector:
    
    def __init__(self, par = None):
        self.keys = []
        self.values = []
        self.size = 0
        self.nrm = -1.0
        self.total_size = 1        
        self.sq_gamma = np.inf

        
        if isinstance(par,dict):
            self.SDVHM(par)
        elif isinstance(par, list):
            self.SDVArr(par)
        elif par!=None:
            self.SDV(par)
        else:
            self.SDV()

    def SDV(self,size):
        self.keys = [0 for _ in range(size)]
        self.values = [0.0 for _ in range(size)]
        self.size = size
    
    def SDVHM(self, hm):
        self.keys = []
        self.values = []
        self.size = 0
        sorted_keys = sorted(list(hm.keys()))
        self.SDV(len(sorted_keys))
        
        for key in sorted_keys:
            self.keys.append(key)
            self.values.append(hm[key])
            self.size+=1
                        

    def SDVArr(self,array):                
        self.keys = []
        self.values = []
        self.size = 0
        for i in range(len(array)):
            if (array[i] != 0):
                self.keys.append(i)
                self.values.append(array[i])
                self.size+=1                    
    
    
    

    def dotProduct(self,other):

        if isinstance(other, list):
            agg = 0
            for i in range(len(self.keys)):
                agg += other[self.keys[i]] * self.values[i];
            
            return agg;        

        #ELSE if same class as self:

        agg = 0
        i = 0
        j = 0
        while (i < len(self.keys)  and j < len(other.keys)):
            k1 = self.keys[i]
            k2 = self.keys[j]

            if (k1 == k2):
                agg += self.values[i] * other.values[j]
                i+=1
                j+=1

            elif (k1 < k2):
                i+=1
            else:
                j+=1                    
        return agg;    
    
    
    
    

    def jaccard(self,other):
        intersection = self.intersection(other);
        return float(intersection) / float((self.size + other.size - intersection))
    
    

    def union(self,other):
        return self.size + other.size - self.intersection(other);
    
    
    def intersection(self, other):
        agg = 0
        i = 0
        j = 0
        while (i < len(self.keys)  and  j < len(other.keys)):
            k1 = self.keys[i]
            k2 = other.keys[j]

            if (k1 == k2):
                agg+=1
                i+=1
                j+=1

            elif (k1 < k2):
                i+=1
                
            else:
                j+=1
            
        
        return agg;
    
    
    def toString(self):
        r = "";
        for i in range(self.size):
            r += self.keys[i] + ":" + self.values[i] + " ";
        
        
        return r;
    

    
    def qgram(self,other):
        agg = 0
        i = 0
        j = 0        
        k1 = 0
        k2 = 0
        
        while (i < len(self.keys)  and j < len(other.keys)):
            k1 = self.keys[i]
            k2 = other.keys[j]

            if (k1 == k2):
                agg += abs(self.values[i] - other.values[j])
                i+=1
                j+=1

            elif (k1 < k2):
                agg += abs(self.values[i]);
                i+=1
                
            else:
                agg += abs(other.values[j]);
                j+=1
                    

        while (i < len(self.keys)):
            agg += abs(self.values[i])
            i+=1        
        
        while (j < len(other.keys)):
            agg += abs(other.values[j]);
            j+=1        
        return agg;
  

  
    def size(self):
        return self.size;
    
    

    def norm(self):
        if (self.nrm >= 0):
            return self.nrm;
        
        
        agg = sum([v*v for v in self.values])
        
        
        self.nrm = np.sqrt(agg)
        return self.nrm
    
    
    
    def cosineSimilarity(self,other):
        
        
        den = min(self.sq_gamma, self.norm()) * min(other.sq_gamma, other.norm())
        
        agg = 0
        i = 0
        j = 0
        while (i < len(self.keys)  and j < len(other.keys)):
            k1 = self.keys[i];
            k2 = other.keys[j]

            if (k1 == k2):
                agg += self.values[i] * other.values[j]
                i+=1
                j+=1

            elif (k1 < k2):
                i+=1
            else:
                j+=1
            
        
        return agg/den
    
    
    def sampleDIMSUM(self, threshold, count, size):
        self.total_size = size
        gamma = 10 * np.log(count) / threshold
        self.sq_gamma = np.sqrt(gamma)        
        
        probability =  self.sq_gamma / self.norm()
        
        if (probability >= 1.0):
            return        
                        
        new_keys = []
        new_values = []
        
        for i in range(len(self.keys)):
            
            if (np.random.rand() < probability):
                new_keys.add(self.keys[i])
                new_values.add(self.values[i])                                    
        self.keys = new_keys
        self.values = new_values
        self.size = len(new_keys)
            
    
    def toArray(self,size):
        
        array = [None for _ in range(size)]
        for i in range(len(self.keys)):
            array[self.keys[i]] = self.values[i];
        
        return array;    







class SparseIntegerVector:
    
    def __init__(self, par = None):
        self.keys = []
        self.values = []
        self.size = 0
    
        if isinstance(par, dict):
            self.SIVHM(par)
        elif isinstance(par, list):
            self.SIVArr(par)
        elif par!=None:
            self.SIV(par)
        else:
            self.SIV()

    def SIV(self,size):
        self.keys = [0 for _ in range(size)]
        self.values = [0 for _ in range(size)]
    
    
    def SIVHM(self, hm):
        self.keys = []
        self.values = []
        self.size = 0
        sorted_keys = sorted(list(hm.keys()))
        self.SIV(len(sorted_keys))
        
        for key in sorted_keys:
            self.keys.append(key)
            self.values.append(hm[key])
            self.size+=1
                        

    def SIVArr(self,array):                
        self.keys = []
        self.values = []
        self.size = 0
        for i in range(len(array)):
            if (array[i] != 0):
                self.keys.append(i)
                self.values.append(array[i])
                self.size+=1                    
    
    
    

    
    
    def cosineSimilarity(self, other):
        den = self.norm() * other.norm()
        agg = 0
        i = 0;
        j = 0;
        while (i < len(self.keys) and j < len(other.keys)):
            k1 = self.keys[i]
            k2 = other.keys[j]

            if (k1 == k2):
                agg += self.values[i] * other.values[j] / den;
                i+=1
                j+=1

            elif (k1 < k2):
                i+=1;
            else:
                j+=1
            
        
        return agg;
    
    
    def dotProduct(self, other):

        if isinstance(other, list):
            agg = 0
            for i in range(len(self.keys)):
                agg += other[self.keys[i]] * self.values[i];
            
            return agg;


        #else another SIV
        agg = 0;
        i = 0;
        j = 0;
        while (i < len(self.keys) and j < len(other.keys)):
            k1 = self.keys[i];
            k2 = other.keys[j];

            if (k1 == k2):
                agg += self.values[i] * other.values[j];
                i+=1;
                j+=1

            elif (k1 < k2):
                i+=1;
            else:
                j+=1
            
        
        return agg;        
    
    

    def norm(self):
        return np.sqrt(sum([v*v for v in self.values]))        
    
    def jaccard(self, other):
        intersection = self.intersection(other)
        return float(intersection) / float(self.size + other.size - intersection)
    
        
    def  union(self, other):
        return self.size + other.size - self.intersection(other);
    
    
    
    def  intersection(self, other):
        agg = 0;
        i = 0;
        j = 0;
        while (i < len(self.keys) and j < len(other.keys)):
            k1 = self.keys[i];
            k2 = other.keys[j];

            if (k1 == k2):
                agg+=1
                i+=1;
                j+=1

            elif (k1 < k2):
                i+=1;
                
            else:
                j+=1
            
        
        return agg;
    
    
    
    def toString(self):
        r = ""
        for i in range(self.size):
            r += self.keys[i] + ":" + self.values[i] + " "
        
        
        return r
    

    def qgram(self, other):
        agg = 0;
        i = 0
        j = 0
        k1
        k2
        
        while (i < len(self.keys) and j < len(other.keys)):
            k1 = self.keys[i];
            k2 = other.keys[j];

            if (k1 == k2):
                agg += abs(self.values[i] - other.values[j]);
                i+=1
                j+=1

            elif (k1 < k2):
                agg += abs(self.values[i])
                i+=1
                
            else:
                agg += abs(other.values[j]);
                j+=1
            
        
        
        
        while (i < len(self.keys)):
            agg += abs(self.values[i]);
            i+=1
        
        
        while (j < len(other.keys)):
            agg += abs(other.values[j]);
            j+=1
        
        return agg;
    

    def  size(self):
        return self.size;
    


