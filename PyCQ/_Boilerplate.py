
class Boilerplate():
    def __init__(self):
        self.word = ''
        self.found_boilerplate = False
        self.nchar = 0

    #/** Process a single comment character */
    def process_char(self,c):
        self.nchar+=1
        if (self.found_boilerplate):
            return

        if (c.isalpha()):
            self.word += c
        else:
            if (self.word == "Copyright" or self.word == "WARRANTIES"):
                self.found_boilerplate = True
            self.word = ''
            

    #/** Return number of characters in boilerplate comment */
    def get_boilerplate_chars(self):
        if self.found_boilerplate:
           return self.nchar
        return 0
    

    #/** Reset state to that at the beginning of a new comment */
    def begin_comment(self):
        self.word = ''
        self.found_boilerplate = False;
        self.nchar = 0


import unittest

class BoilerplateTest (unittest.TestCase):        

    #/** Process the characters of the specified string */
    def process_string(self, b, s):
        for i in s:
            b.process_char(i)
    
    def testCtor(self):
        o = Boilerplate()
        self.assertEqual(o.get_boilerplate_chars(),0)
    

    def testNonBoilerplate(self):
        o = Boilerplate()

        self.process_string(o, "/** This is a test */")
        self.assertEqual(o.get_boilerplate_chars(), 0)
        self.process_string(o, "not copyrighted code")
        self.assertEqual(o.get_boilerplate_chars(), 0)
    

    def testBoilerplateWarranties(self):
        o = Boilerplate()

        self.process_string(o, " * THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND\n")
        self.process_string(o, " * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE\n")
        self.assertTrue(o.get_boilerplate_chars() > 100)
        self.assertTrue(o.get_boilerplate_chars() < 200)
    

    def testBoilerplateCopyright(self):
        o = Boilerplate()
        self.process_string(o, "Copyright (c) 1999 Lennart")
        self.assertTrue(o.get_boilerplate_chars() > 20)
        self.assertTrue(o.get_boilerplate_chars() < 80)    

    def testBoilerplateBegin(self):
        o = Boilerplate()

        self.process_string(o, "Copyright (c) 1999 Lennart")
        o.begin_comment()
        self.assertEqual(o.get_boilerplate_chars(), 0)
    

if __name__ == '__main__':
    unittest.main()