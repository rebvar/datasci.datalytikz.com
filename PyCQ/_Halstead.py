
import math

class Halstead:
    def __init__(self):
        #/* Unique operators and operands */
        self.unique = None
        #/* All operators and operands */
        self.total = 0
        self.reset()

    #/** Reset tracking */
    def reset(self):
        self.unique = set()
        self.total = 0;
    

    #/** Add an operator or operand */
    def add(self,s):
        self.unique.add(s)
        self.total+=1
    

    #/** Return the Halstead complexity */
    def complexity(self):
        if (self.total == 0):
            return 0
        else:
            return self.total * math.log(len(self.unique)) / math.log(2)
    


EPSILON = 1e-10;
import unittest

class HalsteadTest(unittest.TestCase):

    
    def testCtor(self):
        h = Halstead()

        self.assertEqual(h.complexity(), 0.0);
    

    def testReset(self):
        h = Halstead()

        h.add("a");
        h.add("b");
        h.reset();
        self.assertEqual(h.complexity(), 0.0);
    

    def testSimple(self):
        h = Halstead()
        
        h.add("a");
        self.assertEqual(h.complexity(), 0.0);

        h.add("b");
        #/* 2 * log2(2) == 2 * 1 == 2 */
        self.assertAlmostEqual(h.complexity(), 2, 10)

        h.add("b");
        #/* 3 * log2(2) == 3 * 1 == 3 */
        self.assertAlmostEqual(h.complexity(), 3, 10)
    

    #/* From Code Quality: The Open Source Perspective, p. 328 */
    def testComplex(self):
        h = Halstead()

        h.add("old_bucket");
        h.add("=");
        h.add("(");
        h.add("hashp");
        h.add("->");
        h.add("MAX_BUCKET");
        h.add("&");
        h.add("hashp");
        h.add("->");
        h.add("LOW_MASK");
        h.add(")");

        #/*
        # * The book performs the multiplication after rounding log2
        # * to 9 and gives 35.2 as the result.
        # */
        self.assertAlmostEqual(h.complexity(), 34.87, 2)
    
#endif /*  HALSTEADTEST_H */




if __name__ == '__main__':
    unittest.main()