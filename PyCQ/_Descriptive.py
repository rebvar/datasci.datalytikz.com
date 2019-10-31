
import numpy as np

class Descriptive:
    def __init__(self,):
        self.sum = 0;
        self.min = np.inf;
        self.max = -np.inf;
        self.values = [];	#// Required for median
    

    def get_sum(self):
        return self.sum;
    

    def get_count(self):
        return len(self.values)
    

    def get_min(self):
        return self.min
    

    def get_max(self) :
        return self.max
    

    #/** Return the artihmetic mean of the measured value */
    def get_mean(self):
        return np.mean(self.values)
    

    #/** Return the median of the measured value */
    def get_median(self):
        return np.median(self.values)
    

    def add(self,v):
        self.values.append(v)
        self.sum += v;
        if (v < self.min):
            self.min = v;
        if (v > self.max):
            self.max = v;

    #/** Return the population's standard deviation. */
    def get_standard_deviation(self):
        return np.std(self.values)
        #/*
        # * The standard deviation of an empty population is not defined,
        # * but for measuring quality, 0, is a reasonable value.
        # */
        #return values.size() ? sqrt(q / values.size()) : nan("");


    def __repr__(self, **kwargs):
    
        if self.get_count() != 0:
            ret = (str(self.get_count()) + '\t' +str( self.get_min()) +'\t' +str( self.get_mean()) +'\t' +str( self.get_median())+ '\t' +str(  self.get_max()) + '\t' +  str(   self.get_standard_deviation())).replace('.0\t','\t')
            if ret.endswith('.0'):
                return ret[:-2]
            return ret
        else:
            return "0\t\t\t\t\t"


import unittest

class DescriptiveTest (unittest.TestCase):
    
    def testCtor(self) :
        a = Descriptive();
        self.assertEqual(a.get_count(), 0);
        self.assertEqual(a.get_sum(), 0);
        self.assertTrue(np.isnan(a.get_standard_deviation()))
        self.assertTrue(np.isnan(a.get_mean()))
        self.assertTrue(np.isnan(a.get_median()))
    

    def testAdd(self) :
        a = Descriptive()
        a.add(12)
        self.assertEqual(a.get_sum(), 12);
        self.assertEqual(a.get_count(), 1);
        a.add(2);
        self.assertEqual(a.get_sum(), 14);
        self.assertEqual(a.get_count(), 2);
    

    def testMean(self) :
        a = Descriptive()
        a.add(3);
        a.add(12);
        self.assertEqual(a.get_mean(), 7.5);
    

    def testMeanDouble(self) :
        a = Descriptive()
        a.add(3);
        a.add(1.5);
        a.add(1.5);
        self.assertEqual(a.get_mean(), 2.);

    def testMinMax(self) :
        a = Descriptive()
        a.add(5)
        a.add(2);
        a.add(12);
        self.assertEqual(a.get_min(), 2);
        self.assertEqual(a.get_max(), 12);
    
    def testMinMaxDouble(self) :
        a = Descriptive()
        a.add(5.1);
        a.add(2.5);
        a.add(12.5);
        self.assertEqual(a.get_min(), 2.5);
        self.assertEqual(a.get_max(), 12.5);
    

    def testOutput(self) :
        
        a = Descriptive()
        a.add(2);
        a.add(4);
        
        #// Don't forget to update testOutputEmpty
        self.assertEqual(str(a), "2\t2\t3\t3\t4\t1")
    

    def testOutputEmpty(self) :
        
        a= Descriptive()
        
        self.assertEqual(str(a), "0\t\t\t\t\t");
    

    def testSDZero(self) :
        a = Descriptive()
        a.add(1);
        a.add(1);
        a.add(1);
        self.assertEqual(a.get_standard_deviation(), 0.);
    

    #// From https://en.wikipedia.org/wiki/Standard_deviation#Basic_examples
    def testSDTwo(self) :
        a = Descriptive()
        a.add(2);
        a.add(4);
        a.add(4);
        a.add(4);
        a.add(5);
        a.add(5);
        a.add(7);
        a.add(9);
        self.assertEqual(a.get_standard_deviation(), 2.)

    #// Verified in R with:
    #// x <- c(1,2,rep(3,16)); sqrt(sum((x-mean(x))^2)/(length(x))
    def testSDHalf(self) :
        a = Descriptive()
        a.add(1);
        a.add(2);
        for i in range(16):
            a.add(3);
        self.assertTrue(abs(a.get_standard_deviation() - 0.5) < 1e-10)
    
    def testMedianOne(self) :
        a = Descriptive()
        a.add(42);
        self.assertEqual(a.get_median(), 42.);
    

    def testMedianTwo(self) :
        a = Descriptive()
        a.add(4);
        a.add(2);
        self.assertEqual(a.get_median(), 3.);
    

    def testMedianOdd(self) :
        a = Descriptive()
        a.add(2);
        a.add(0);
        a.add(1);
        self.assertEqual(a.get_median(), 1.);
    

    def testMedianEven(self) :
        a = Descriptive()
        a.add(2);
        a.add(0);
        a.add(1);
        a.add(5);
        self.assertEqual(a.get_median(), 1.5);
    

    def testMedianPartial(self) :
        a = Descriptive()
        a.add(100);
        a.add(3);
        a.add(0);
        a.add(5);
        a.add(7);
        a.add(9);
        self.assertEqual(a.get_median(), 6.);
    





if __name__ == '__main__':
    unittest.main()
