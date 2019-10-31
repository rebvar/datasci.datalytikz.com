
from ._CKeyword import CKeyword
import copy
  
class NestingDetails(object):

    def __init__(self, key = CKeyword.IdentifierType.OTHER):
        
        self.key = key
        self.saw_statement = False;	# #// True after seeing a statement	
        self.brace_indentation = [1]
        
    def brace_balance(self):#	// Number of matching {} pairs
        return len(self.brace_indentation)- 1;

    def indent(self): #		// How much to indent at this level
        level = 0;
        for i in self.brace_indentation:
            level += i
        return level;    

#/** Track nesting level */
class NestingLevel:

    #typedef std::list<NestingDetails> NDList;	// Details for each nesting level
    def __init__(self):
        self.nd = [];  #		// Details for each nesting level
        self.backtrack = [] #;	// Details for each nesting level
        self.reset()
    #/**
    # * Pop nesting within a function that is not protected by braces.
    # * Ensure that at least one level remains, in case the parsing algorithm
    # * gets thrown off by the use of macros.
    # */
    def pop(self):
        saved_backtrack = False;

        while (len(self.nd)>0 and self.nd[-1].brace_balance() == 0 and self.nd[-1].key != CKeyword.IdentifierType.DO):
            #// Save if stack for possible else
            if ((self.nd[-1].key == CKeyword.IdentifierType.IF or self.nd[-1].key == CKeyword.IdentifierType.ELIF) and not saved_backtrack):
                self.backtrack = copy.deepcopy(self.nd)
                saved_backtrack = True
            
            self.nd.pop()
        if (len(self.nd)==0):
            self.reset();	#// We lost track of the state    

    #/**
    # * To be called after encountering a statement's semicolon
    # * or a closing brace.
    # */
    def saw_statement(self):
        if (self.nd[-1].brace_balance() == 0):
            self.pop()
            self.nd[-1].saw_statement = True;
        
    

    
    
    
    def reset(self):
        self.nd = [NestingDetails()]
    
    #/**
    # * To be called after encountering an opening brace.
    # * indented is set to true if there is an additional level
    # * of indentation associated with a standalone brace.
    # */
    def saw_open_brace(self,indented=False):
        self.nd[-1].brace_indentation.append(indented)
    

    #/** To be called after encountering a closing brace */
    def saw_close_brace(self):
        if (self.nd[-1].brace_balance() > 0):
            self.nd[-1].brace_indentation.pop()
        self.saw_statement()
    

    #/** To be called after encountering a statement's semicolon */
    def saw_statement_semicolon(self):
        self.saw_statement()
    

    #/** To be called after encountering a keyword associated with nesting */
    def saw_nesting_keyword(self,t):
        if (t == CKeyword.IdentifierType.WHILE and self.nd[-1].key == CKeyword.IdentifierType.DO and self.nd[-1].saw_statement):
            #// Handle while of do while
            self.nd.pop()
        elif (t == CKeyword.IdentifierType.IF and self.nd[-1].key == CKeyword.IdentifierType.ELSE and self.nd[-1].brace_balance() == 0):

            #// else if -> elif
            self.nd[-1].key = CKeyword.IdentifierType.ELIF
        else:
            #/*
            # * On an "else" keyword backtrack: undo preceding
            # * full pop and add a single level one.
            # */
            if (t == CKeyword.IdentifierType.ELSE and len(self.backtrack)>0):
                self.nd = self.backtrack
                if len(self.nd)>0:
                    self.nd.pop();
                self.backtrack = self.nd
            
            self.nd.append(NestingDetails(key = t))
        
    

    #/** Return the current level of nesting. */
    def get_nesting_level(self):
        nesting = 0
        #// One day: for (auto& level : nd)
        for level in self.nd:
            nesting += level.indent()
        return nesting - 1;    




import unittest

class NestingLevelTest (unittest.TestCase):
    
    def testCtor(self): 
        n = NestingLevel()
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// }}}
 #// Uncovered implementation error
    def testReset(self): 
        n = NestingLevel()
        n.saw_close_brace();
        n.saw_close_brace();
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) 1;
    def testSingleIf(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) if (y) 2; 0;
 #// Uncovered implementation error
    def testDouble(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// { 0; }
    def testTrivialBrace(self): 
        n = NestingLevel()
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// {{ 0; }{
    def testDoubleTrivialBrace(self): 
        n = NestingLevel()
        n.saw_open_brace();
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_close_brace();
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) { 1; 1; }
    def testSimpleBrace(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) if (y) { 2; 2; }
    def testNestingBrace(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) { 1; if (y) { 2; 2; } 1; 1; } 0;
    def testDoubleNestingBrace(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) { if (y) 2; 1; 1; } 0;
    def testBraceProtection(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) { if (y) if (z) 3; 1; } 0;
    def testDoubleBraceProtection(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 3);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) { if (y) 2; else 2; 1; } 0;
    def testIfElseBrace(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) 1; else 1; 0;
    def testIfElse(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) { 1; } else { 1; } 0;
    def testBracedIfElse(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

    #/*
    # * if (x)
    # *   {
    # *     2;
    # *   }
    # * else
    # *   {
    # *     2;
    # *   }
    # *   0;
    # */
    def testGnuBracedIfElse(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_open_brace(True);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        n.saw_open_brace(True);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) if (y) 2; else 2; 1; 0;
 #// Modeled implementation error
    def testIfIfElse(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) 1; else if (y) 1; else 1; 0;
 #// Uncovered specification error: strictly it is
 #// if (x) 1; else if (y) 2; else 1; 0;
 #// Uncovered two implementation errors
    def testElseIf(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    
 #// if (x) 1; else { if (y) 2; else 2; } 0;
    def testBracedElseIf(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        n.saw_open_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) 1; else { if (y) 2; else if (z) 2; else 2; } 0;
    def testBracedElseIfElse(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        n.saw_open_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    


 #// if (x) 1; else { 1; if (y) 2; else 2; 1; } 0;
    def testComplexBracedElseIf(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_close_brace();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// do 1; while(z); 0;
    def testSimpleDo(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.DO);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// do { 1; 1; } while(z); 0;
    def testBracedDo(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.DO);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        n.saw_close_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// do { 1; while (x) 2; 1; } while(z); 0;
    def testBracedDoWhile(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.DO);
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_close_brace();
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// do while (x) 2; while(z); 0;
    def testUnbracedDoWhile(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.DO);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// do while (x) while(y) 3; while(z); 0;
    def testUnbracedDoNestedWhile(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.DO);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 3);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// do do while (x) while(y) 4; while(z); while (w) 0;
    def testUnbracedNestedDoNestedWhile(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.DO);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.DO);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 3);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 4);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    


 #// while (x) 1;
    def testSingleWhile(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) for (;;) switch while (y) do 5; while(z); 0;
    def testAllStatements(self): 
        n = NestingLevel()
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.FOR);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_nesting_keyword(CKeyword.IdentifierType.SWITCH);
        self.assertEqual(n.get_nesting_level(), 3);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        self.assertEqual(n.get_nesting_level(), 4);
        n.saw_nesting_keyword(CKeyword.IdentifierType.DO);
        self.assertEqual(n.get_nesting_level(), 5);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 5);
        n.saw_nesting_keyword(CKeyword.IdentifierType.WHILE);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// a = { 0 }; 0;
    def testBracedAssignment(self): 
        n = NestingLevel()
        n.saw_open_brace();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_close_brace();
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// if (x) for (;;) 2; else 1;
 #// Added to investigate and verify fixing testElseComment
    def testIfForElse(self): 
        n = NestingLevel()
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_nesting_keyword(CKeyword.IdentifierType.IF);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_nesting_keyword(CKeyword.IdentifierType.FOR);
        self.assertEqual(n.get_nesting_level(), 2);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// 0; else 1;
 #// Added to investigate and verify fixing testNoIf
    def testElse(self): 
        n = NestingLevel()
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    

 #// 0; else 1; else 1;
    def testElseElse(self): 
        n = NestingLevel()
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
        n.saw_nesting_keyword(CKeyword.IdentifierType.ELSE);
        self.assertEqual(n.get_nesting_level(), 1);
        n.saw_statement_semicolon();
        self.assertEqual(n.get_nesting_level(), 0);
    





if __name__ == '__main__':
    unittest.main()