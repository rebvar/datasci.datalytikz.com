

import sys

class CharSource:

    MAX_REWIND = 10
    
    def __init__(self, s = sys.stdin):

        self.pushed_char = [] #Stack
        self.returned_char = []  # QUE
        self.instream = s
        self.nchar = 0 
        

    #/** Obtain the next character from the source */
    def get(self,c):
        if (len(self.pushed_char)==0):
            c = self.instream.read(1)
            if (c!=''):
                self.nchar+=1
            else:
                return False,c
        else:
            c = self.pushed_char.pop()  
                              
        self.returned_char.append(c)
        while len(self.returned_char) > CharSource.MAX_REWIND:
            del self.returned_char[0]
        return True,c

    #/**
    # * Return the next character from source without removing it
    # * Return 0 on EOF.
    # */
    def char_after(self): 
        c = None
        res, c = self.get(c)
        if (res):
            self.push(c)
            return c
        else:
            return '\x00'
    

    #/**
    # * Return the nth character before the one returned
    # * Return 0 if no such character is available.
    # */
    def char_before(self,n = 1):
        index = len(self.returned_char) - n - 1

        if (index >= 0):
            return self.returned_char[index]
        else:
            return '\x00'
    

    #/** Return number of characters read */
    def get_nchar(self):
        return self.nchar - len(self.pushed_char)


    #/**
    # * Push the specified character back into the source
    # * In effect, this is an undo of the last get, and therefore
    # * also moves back one character in the returned character queue.
    # * */
    def push(self,c):
        self.pushed_char.append(c)
        if (len(self.returned_char)> 0):
            self.returned_char.pop()


from io import StringIO

import unittest

class CharSourceTest(unittest.TestCase):

    def testCtor(self):         
        s = CharSource()
    

    def testStrCtor(self): 
        string = StringIO("hi")

        s = CharSource(string)
        c = None
        self.assertEqual(s.get(c)[1], 'h')
        self.assertEqual(s.get(c)[1], 'i')
    

    def testPush(self): 
        string = StringIO("he");

        s = CharSource(string)
        c = None
        self.assertEqual(s.get(c)[1], 'h')        
        s.push('o')
        self.assertEqual(s.get(c)[1], 'o')
        ##// Again
        s.push('p')
        self.assertEqual(s.get(c)[1], 'p');
        ##// Two
        s.push('q');
        s.push('r');
        self.assertEqual(s.get(c)[1], 'r');
        self.assertEqual(s.get(c)[1], 'q');
        self.assertEqual(s.get(c)[1], 'e');
        ##// Push at EOF
        s.push('s')
        self.assertEqual(s.get(c)[1], 's');
    

    class StateHandler:
    
        def __init__ (self, s = 0):
            self.state = s
    
        
        def get_state(self):
            return self.state
        def operator(self):
            self.state = 42
        
    
    def testNchar(self): 
        string = StringIO("he");

        s = CharSource(string)
        c = None
        self.assertEqual(s.get(c)[1], 'h');
        self.assertEqual(s.get(c)[1], 'e');
        self.assertTrue(not s.get(c)[0]);
        self.assertEqual(s.get_nchar(), 2)
    

    def testNcharPush(self): 
        string = StringIO("he");

        s = CharSource(string)
        c = None
        self.assertEqual(s.get(c)[1], 'h');
        self.assertEqual(s.get_nchar(), 1);
        self.assertEqual(s.get(c)[1], 'e');
        s.push('e');
        self.assertEqual(s.get_nchar(), 1);
        self.assertEqual(s.get(c)[1], 'e');
        self.assertTrue(not s.get(c)[0])
        self.assertEqual(s.get_nchar(), 2);
    

    def testCharAfter(self): 
        string = StringIO("he");

        s = CharSource(string)
        c = None
        self.assertEqual(s.char_after(), 'h');
        self.assertEqual(s.get(c)[1], 'h');
        self.assertEqual(s.char_after(), 'e');
        s.push('p');
        self.assertEqual(s.char_after(), 'p');
        self.assertEqual(s.get(c)[1], 'p');
        self.assertEqual(s.char_after(), 'e');
        self.assertEqual(s.get(c)[1], 'e');
        self.assertTrue(not s.get(c)[0]);
        self.assertEqual(s.char_after(), '\x00');
        self.assertEqual(s.get_nchar(), 2);
    

    def testCharBefore(self): 
        string = StringIO("he");

        s = CharSource(string)
        c = None
        self.assertEqual(s.char_before(), '\x00');
        self.assertEqual(s.char_after(), 'h');

        self.assertEqual(s.get(c)[1], 'h');
        self.assertEqual(s.char_before(), '\x00');
        self.assertEqual(s.char_after(), 'e');

        self.assertEqual(s.get(c)[1], 'e');
        self.assertEqual(s.char_before(), 'h');
        self.assertTrue(not s.get(c)[0]);
        self.assertEqual(s.char_after(), '\x00');
        self.assertEqual(s.get_nchar(), 2);
    

    def testCharBeforeNewline(self): 
        string = StringIO("h\ne");

        s = CharSource(string)
        c = None
        self.assertEqual(s.char_before(), '\x00');
        self.assertEqual(s.char_after(), 'h');

        self.assertEqual(s.get(c)[1], 'h');
        self.assertEqual(s.char_before(), '\0');

        self.assertEqual(s.get(c)[1], '\n');
        self.assertEqual(s.char_before(), 'h');   

    def testCharBeforePush(self): 
        string = StringIO("he");

        s = CharSource(string)
        c = None
        self.assertEqual(s.char_before(), '\x00');
        self.assertEqual(s.char_after(), 'h');

        self.assertEqual(s.get(c)[1], 'h');
        self.assertEqual(s.char_before(), '\x00');
        self.assertEqual(s.char_after(), 'e');
        s.push('h');
        self.assertEqual(s.char_after(), 'h');

        self.assertEqual(s.get(c)[1], 'h');
        self.assertEqual(s.char_before(), '\x00');
        self.assertEqual(s.char_after(), 'e');

        self.assertEqual(s.get(c)[1], 'e');
        self.assertEqual(s.char_before(), 'h');
        self.assertTrue(not s.get(c)[0]);
        self.assertEqual(s.char_after(), '\x00');
        self.assertEqual(s.get_nchar(), 2);
    

    def testCharBeforeN(self): 
        string = StringIO("hat");

        s = CharSource(string)
        c = None
        self.assertEqual(s.char_before(), '\x00');
        self.assertEqual(s.char_after(), 'h');

        self.assertEqual(s.get(c)[1], 'h');
        self.assertEqual(s.char_before(), '\x00');

        self.assertEqual(s.get(c)[1], 'a');
        self.assertEqual(s.char_before(), 'h');
        self.assertEqual(s.char_before(2), '\x00');

        self.assertEqual(s.get(c)[1], 't');
        self.assertEqual(s.char_before(), 'a');
        self.assertEqual(s.char_before(2), 'h');
    


    def testCharBeforeQueueShrink(self): 
        string = StringIO("abcdefghijklmnopqrstuvwxyz");

        s = CharSource(string)
        c = None

        self.assertEqual(s.get(c)[1], 'a')
        for t in range(ord('b'), ord('z')):
            i = chr(t)
            
            self.assertEqual(s.char_after(), i)
            self.assertEqual(s.get(c)[1], i)
            self.assertEqual(s.char_before(), chr(t-1))
        
            
    
if __name__ == '__main__':
    unittest.main()

