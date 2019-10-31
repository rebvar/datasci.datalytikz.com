from .LSHSuperBit_Module import SuperBit

import random


class SuperBitExample:
    def main():
        
        n = 20;
        
        sb = SuperBit(d = n)
        
        rand = random.Random()
        v1 = []
        v2 = []
        for i in range(n):
            v1.append(rand.randint(1,100000))
            v2.append(rand.randint(1,100000))    

        sig1 = sb.signature(v1)
        sig2 = sb.signature(v2)
        
        print("Signature (estimated) similarity: " + str(sb.similarity(sig1, sig2)))
        print("Real (cosine) similarity: " +  str(SuperBit.cosineSimilarity(v1, v2)))

#SuperBitExample.main()

from .LSHMinHash_Module import MinHash

class InitialSeed: 
    
    def main():

        
        signature_size = 20
        dictionary_size = 100
        initial_seed = 123456

        mh = MinHash(size=signature_size, dict_size=dictionary_size, seed = initial_seed)
        mh2 = MinHash(size=signature_size, dict_size=dictionary_size, seed = initial_seed)

        
        r = random.Random()
        vector = []
        for i in range(dictionary_size):
            vector.append(r.randint(0,1)==1)

        
        print(mh.signature(vector))
        print(mh2.signature(vector))

#InitialSeed.main()



from .LSHMinHash_Module import LSHMinHash

class LSHMinHashExample:


    def main():
        
        count = 300
        
        
        n = 100
        
        buckets = 10;
        
        vectors = []
        r = random.Random()
        
        vectors.append([])
        for j in range(n):
            vectors[0].append(r.randint(0,10) == 0)
        
        
        for i in range(1, count):

            vectors.append([])
            
            for j in range(n):
                if r.random() <= 0.7:

                    vectors[i].append(vectors[0][j])
                else:
                    vectors[i].append(r.randint(0,10) == 0)
            
        
        
        for stages in range(1,11):
            
            lsh = LSHMinHash(s = stages, b = buckets, n = n);
            hashes = []
            for i in range(count):
                vector = vectors[i];
                hashes.append(lsh.hash(vector));
                

            

            results = [[0,0] for _ in range(11)]
            for i in range(len(vectors)):
                vector1 = vectors[i]
                hash1 = hashes[i]

                for j in range(i):
                    vector2 = vectors[j]
                    hash2 = hashes[j]
                    
                    similarity = MinHash.jaccardIndex(vector1, vector2)

                    results[int(10 * similarity)][0]+=1

                    for stage in range(stages):
                        if (hash1[stage] == hash2[stage]):
                            results[int(10 * similarity)][1]+=1
                            break
                        
                    
                
            

            
            for i in range(len(results)):
                similarity = float(i) / 10.0;
                
                probability = 0
                if (results[i][0] != 0):
                    probability = float(results[i][1]) / float(results[i][0])
                
                print("" + str(similarity) + "\t" + str(probability) + "\t" + str(stages));
            
            
            
            print()
             


#LSHMinHashExample.main()


from .LSHSuperBit_Module import LSHSuperBit

class LSHSuperBitExample:

    def main():
        
        count = 100;
            
        # R^n
        n = 3
            
        stages = 2
        buckets = 4
            
        # Produce some vectors in R^n
        r = random.Random();
        vectors = []
        for i in range(count):
            vectors.append([])
                
            for j in range(n):
                vectors[i].append(r.gauss(0,1))
                
            
        
        lsh = LSHSuperBit(stages = stages,buckets = buckets, dimensions = n)
            
        # Compute a SuperBit signature, and a LSH hash
        for i in range(count):
            vector = vectors[i]
            hash = lsh.hash(vector)
            x = ""
            for v in vector:
                x+= ("%6.2f\t" % v)

            x = x+str(hash[0])
            print(x)
            
                                        
#LSHSuperBitExample.main()




class MinHashExample:

    def main():
        minhash = MinHash(error=0.1, dict_size=5);
        
        vector1 = [True, False, False, True, False];
        sig1 = minhash.signature(vector1)
        
        set2=set()
        set2.add(0)
        set2.add(2)
        set2.add(3)
        sig2 = minhash.signature(set2)
        
        print("Signature similarity: " + str(minhash.similarity(sig1, sig2)));
        print("Real similarity (Jaccard index)" + str(MinHash.jaccardIndex(MinHash.convert2Set(vector1), set2)));
    


#MinHashExample.main()


class SimpleLSHMinHashExample:

    
    def main():
        sparsity = 0.75
        
        count = 10000
        
        n = 100
        
        stages = 2;
        
        buckets = 10
        
        vectors = []
        rand = random.Random()
        
        for i in range(count):
            vectors.append([])
            for j in range(n):

                vectors[i].append(rand.random() > sparsity)
            
        
        
        lsh = LSHMinHash(s = stages, b = buckets, n = n)
        
        counts = [[0 for i in range(buckets)] for _ in range(stages)];
        
        #// Perform hashing
        for vector in vectors:
            hash = lsh.hash(vector)
            
            for i in range(len(hash)):
                counts[i][hash[i]]+=1
            
            
            print(str(vector)+":"+str(hash))
            
        
        print("Number of elements per bucket at each stage:");
        
        print(counts);
        

#SimpleLSHMinHashExample.main()

from .LSHUtilVectors_Module import SparseIntegerVector

class SuperBitSparseExample:

    
    def main():
        
        n = 10;
        
        sb = SuperBit(d = n)
        
        
        rand = random.Random()
        
        v = [0 for _ in range(n)]
        for i in range(int(n/10)):
            v[rand.randint(0,n-1)] = rand.randint(0,100)
        
        v1 = SparseIntegerVector(v)
        
        v = [0 for _ in range(n)]

        for i in range(int(n/10)):
            v[rand.randint(0,n-1)] = rand.randint(0,100)
        
        v2 = SparseIntegerVector(v);

        sig1 = sb.signature(v1)
        sig2 = sb.signature(v2)
        
        print("Signature (estimated) similarity: " + str( sb.similarity(sig1, sig2)));
        print("Real cosine similarity: " + str(v1.dotProduct(v2) / (v1.norm() * v2.norm())));
        
        
#SuperBitSparseExample.main()   



