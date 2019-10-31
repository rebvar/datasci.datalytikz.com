class Cyclomatic:
    def __init__(self):
        self.paths = 0
        self.boolean_branches = 0

        self.reset()

    def reset(self):
        self.paths = 1
        self.boolean_branches = 0;
    

    #/** Called to add a path established by a predicate, e.g. if, while */
    def add_path(self):
        self.paths+=1

    #/** Called to add paths established by short-circuit Boolean operators */
    def add_boolean_branch(self): 
        self.boolean_branches+=1

    #/** Return number of paths through the code */
    def complexity(self): 
        return self.paths

    #/** Return number of paths, taking into account Boolean operators */
    def extended_complexity(self):
        return self.paths + self.boolean_branches


import unittest

class CyclomaticTest (unittest.TestCase):    

    def testCtor(self):
        c = Cyclomatic()
        self.assertEqual(c.complexity(), 1);
        self.assertEqual(c.extended_complexity(), 1);    

    def testAdd(self):
        c= Cyclomatic()
        c.add_path()
        c.add_path()
        c.add_boolean_branch();
        self.assertEqual(c.complexity(), 3);
        self.assertEqual(c.extended_complexity(), 4);
    



if __name__ == '__main__':
    unittest.main()
