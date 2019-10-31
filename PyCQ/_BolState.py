
class BolState:
    def __init__(self):
        self.saw_newline()
    
    

    #/** True at the beginning of a line */
    def at_bol(self):
        return self.bol_state

    #/** True at the beginning of a line, possibly with spaces */
    def at_bol_space(self):
        return self.bol_space_state

    #/** Return the current line's indentation. */
    def get_indentation(self):
        return self.indentation

    #/** Called when processing a newline */
    def saw_newline(self): 
        self.bol_state = True
        self.bol_space_state = True
        self.indentation = 0
    

    #/** Called when processing a space character c0 */
    def saw_space(self,c):
        self.bol_state = False
        if (self.bol_space_state):
            if (c == ' '):
                self.indentation+=1
            #/*
            # * 0 8
            # * 1 8
            # * ...
            # * 7 8
            # * 8 16
            # * ...
            # */
            elif (c == '\t'):
                self.indentation = int((int(self.indentation / 8) + 1) * 8)
        
    

    #/** Called when processing a non-space character */
    def saw_non_space(self):
        self.bol_state =False
        self.bol_space_state = False

import unittest

class BolStateTest(unittest.TestCase):

    
    def testCtor(self): 
        b = BolState()
        self.assertTrue(b.at_bol());
        self.assertTrue(b.at_bol_space());
    

    def testAfterSpace(self): 
        b = BolState()
        b.saw_space(' ')
        self.assertTrue(not b.at_bol())
        self.assertTrue(b.at_bol_space());
    

    def testAfterNonSpace(self): 
        b = BolState()
        b.saw_space(' ');
        b.saw_non_space();
        b.saw_space(' ');
        self.assertTrue(not b.at_bol())
        self.assertTrue(not b.at_bol_space())
    

    def testAfterNewline(self): 
        b = BolState()
        b.saw_non_space();
        b.saw_newline();
        self.assertTrue(b.at_bol())
        self.assertTrue(b.at_bol_space())
    

    def testIndentation(self): 
        b = BolState()
        ##// Test space
        self.assertEqual(b.get_indentation(), 0);
        b.saw_space(' ');
        self.assertEqual(b.get_indentation(), 1);
        b.saw_space(' ');
        self.assertEqual(b.get_indentation(), 2);
        #// Test tab
        b.saw_space('\t');
        self.assertEqual(b.get_indentation(), 8);
        #// Space after tab
        b.saw_space(' ');
        self.assertEqual(b.get_indentation(), 9)
        #// Edge case
        while (b.get_indentation() != 15):
            b.saw_space(' ')
        b.saw_space('\t');
        self.assertEqual(b.get_indentation(), 16);
        #// Edge case
        b.saw_space('\t');
        self.assertEqual(b.get_indentation(), 24);
        ##// Non-space
        b.saw_non_space();
        self.assertEqual(b.get_indentation(), 24);
    

if __name__ == '__main__':
    unittest.main()

