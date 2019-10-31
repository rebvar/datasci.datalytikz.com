
from enum import Enum, auto

class CKeyword:

    class IdentifierType(Enum):
        BREAK = auto()
        CASE = auto()
        CONST = auto()
        CONTINUE = auto()
        DEFAULT = auto()
        DO = auto()
        ELIF = auto()
        ELSE = auto()
        ENUM = auto()
        FOR = auto()
        GOTO = auto()
        IF = auto()
        IFDEF = auto()
        INCLUDE = auto()
        INLINE = auto()
        NOALIAS = auto()
        REGISTER = auto()
        RESTRICT = auto()
        RETURN = auto()
        SIGNED = auto()
        STATIC = auto()
        STRUCT = auto()
        SWITCH = auto()
        TYPEDEF = auto()
        UNION = auto()
        UNSIGNED = auto()
        VOID = auto()
        VOLATILE = auto()
        WHILE = auto()
        OTHER = auto()		#// All other keywords
        IDENTIFIER = auto()	#// Plain identifier (not a keyword)
    

    #// Keyword map
    
    

    def __init__ (self):
        self.km = {}
        self.km["auto"] = CKeyword.IdentifierType.OTHER;
        self.km["break"] = CKeyword.IdentifierType.BREAK;
        self.km["case"] = CKeyword.IdentifierType.CASE;
        self.km["char"] = CKeyword.IdentifierType.OTHER;
        self.km["const"] = CKeyword.IdentifierType.CONST;
        self.km["continue"] = CKeyword.IdentifierType.CONTINUE;
        self.km["default"] = CKeyword.IdentifierType.DEFAULT;
        self.km["do"] = CKeyword.IdentifierType.DO;
        self.km["double"] = CKeyword.IdentifierType.OTHER;
        self.km["elif"] = CKeyword.IdentifierType.ELIF;		#// Preprocessor only
        self.km["else"] = CKeyword.IdentifierType.ELSE;
        self.km["enum"] = CKeyword.IdentifierType.ENUM;
        self.km["extern"] = CKeyword.IdentifierType.OTHER;
        self.km["float"] = CKeyword.IdentifierType.OTHER;
        self.km["for"] = CKeyword.IdentifierType.FOR;
        self.km["goto"] = CKeyword.IdentifierType.GOTO;
        self.km["if"] = CKeyword.IdentifierType.IF;
        self.km["ifdef"] = CKeyword.IdentifierType.IFDEF;		#// Preprocessor only
        self.km["include"] = CKeyword.IdentifierType.INCLUDE;	#// Preprocessor only
        self.km["inline"] = CKeyword.IdentifierType.INLINE;
        self.km["int"] = CKeyword.IdentifierType.OTHER;
        self.km["long"] = CKeyword.IdentifierType.OTHER;
        self.km["noalias"] = CKeyword.IdentifierType.NOALIAS;
        self.km["register"] = CKeyword.IdentifierType.REGISTER;
        self.km["restrict"] = CKeyword.IdentifierType.RESTRICT;
        self.km["return"] = CKeyword.IdentifierType.RETURN;
        self.km["short"] = CKeyword.IdentifierType.OTHER;
        self.km["signed"] = CKeyword.IdentifierType.SIGNED;
        self.km["sizeof"] = CKeyword.IdentifierType.OTHER;
        self.km["static"] = CKeyword.IdentifierType.STATIC;
        self.km["struct"] = CKeyword.IdentifierType.STRUCT;
        self.km["switch"] = CKeyword.IdentifierType.SWITCH;
        self.km["typedef"] = CKeyword.IdentifierType.TYPEDEF;
        self.km["union"] = CKeyword.IdentifierType.UNION;
        self.km["unsigned"] = CKeyword.IdentifierType.UNSIGNED;
        self.km["void"] = CKeyword.IdentifierType.VOID;
        self.km["volatile"] = CKeyword.IdentifierType.VOLATILE;
        self.km["while"] = CKeyword.IdentifierType.WHILE;

    def identifier_type(self,s):
        if s in self.km.keys():
            return self.km[s]
        return CKeyword.IdentifierType.IDENTIFIER


import unittest
class CKeywordTest(unittest.TestCase):
    
    

    def testBranch(self):
        ck = CKeyword()
        self.assertEqual(ck.identifier_type("if"), CKeyword.IdentifierType.IF)
        self.assertEqual(ck.identifier_type("elif"), CKeyword.IdentifierType.ELIF);
        self.assertEqual(ck.identifier_type("ifdef"), CKeyword.IdentifierType.IFDEF);
        self.assertEqual(ck.identifier_type("for"), CKeyword.IdentifierType.FOR);
        self.assertEqual(ck.identifier_type("while"), CKeyword.IdentifierType.WHILE);
        self.assertEqual(ck.identifier_type("case"), CKeyword.IdentifierType.CASE);
        self.assertEqual(ck.identifier_type("default"), CKeyword.IdentifierType.DEFAULT);
    

    def testGoto(self):
        ck = CKeyword()
        self.assertEqual(ck.identifier_type("goto"), CKeyword.IdentifierType.GOTO);
    

    def testRegister(self):
        ck = CKeyword()
        self.assertEqual(ck.identifier_type("register"), CKeyword.IdentifierType.REGISTER);
    

    def testInclude(self):
        ck = CKeyword()
        self.assertEqual(ck.identifier_type("include"), CKeyword.IdentifierType.INCLUDE);
    

    def testTypedef(self):
        ck = CKeyword()
        self.assertEqual(ck.identifier_type("typedef"), CKeyword.IdentifierType.TYPEDEF);
    

    def testOther(self):
        ck = CKeyword()
        self.assertEqual(ck.identifier_type("sizeof"), CKeyword.IdentifierType.OTHER);
        self.assertEqual(ck.identifier_type("int"), CKeyword.IdentifierType.OTHER);
        self.assertEqual(ck.identifier_type("static"), CKeyword.IdentifierType.STATIC);
    

    def testId(self):
        ck = CKeyword()
        self.assertEqual(ck.identifier_type("returning"), CKeyword.IdentifierType.IDENTIFIER);
        self.assertEqual(ck.identifier_type("id"), CKeyword.IdentifierType.IDENTIFIER);
        self.assertEqual(ck.identifier_type("xyzzy"), CKeyword.IdentifierType.IDENTIFIER);
    

    
if __name__ == '__main__':
    unittest.main()

