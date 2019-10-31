
from ._Descriptive import Descriptive
from ._Halstead import Halstead
from ._Cyclomatic import Cyclomatic
from enum import Enum, auto


class QualityMetrics:

    class StyleHint (Enum):        
        NO_SPACE_AFTER_BINARY_OP=auto()
        NO_SPACE_AFTER_CLOSING_BRACE=auto()
        NO_SPACE_AFTER_COMMA=auto()
        NO_SPACE_AFTER_KEYWORD=auto()
        NO_SPACE_AFTER_OPENING_BRACE=auto()
        NO_SPACE_AFTER_SEMICOLON=auto()
        NO_SPACE_BEFORE_BINARY_OP=auto()
        NO_SPACE_BEFORE_CLOSING_BRACE=auto()
        NO_SPACE_BEFORE_KEYWORD=auto()
        NO_SPACE_BEFORE_OPENING_BRACE=auto()
        SPACE_AFTER_OPENING_SQUARE_BRACKET=auto()
        SPACE_AFTER_STRUCT_OP=auto()
        SPACE_AFTER_UNARY_OP=auto()
        SPACE_AT_END_OF_LINE=auto()
        SPACE_BEFORE_CLOSING_BRACKET=auto()
        SPACE_BEFORE_CLOSING_SQUARE_BRACKET=auto()
        SPACE_BEFORE_COMMA=auto()
        SPACE_BEFORE_OPENING_SQUARE_BRACKET=auto()
        SPACE_BEFORE_SEMICOLON=auto()
        SPACE_BEFORE_STRUCT_OP=auto()
        #// We also track the opposite rules to measure inconsistency
        SPACE_AFTER_BINARY_OP=auto()
        SPACE_AFTER_CLOSING_BRACE=auto()
        SPACE_AFTER_COMMA=auto()
        SPACE_AFTER_KEYWORD=auto()
        SPACE_AFTER_OPENING_BRACE=auto()
        SPACE_AFTER_SEMICOLON=auto()
        NO_SPACE_AFTER_STRUCT_OP=auto()
        SPACE_BEFORE_BINARY_OP=auto()
        SPACE_BEFORE_CLOSING_BRACE=auto()
        SPACE_BEFORE_KEYWORD=auto()
        SPACE_BEFORE_OPENING_BRACE=auto()
        NO_SPACE_BEFORE_STRUCT_OP=auto()
        NO_SPACE_AFTER_OPENING_SQUARE_BRACKET=auto()
        NO_SPACE_AFTER_UNARY_OP=auto()
        NO_SPACE_BEFORE_CLOSING_BRACKET=auto()
        NO_SPACE_BEFORE_CLOSING_SQUARE_BRACKET=auto()
        NO_SPACE_BEFORE_COMMA=auto()
        NO_SPACE_BEFORE_OPENING_SQUARE_BRACKET=auto()
        NO_SPACE_BEFORE_SEMICOLON=auto()
        #// Add more elements here
        STYLE_HINT_SIZE = auto()    



    def __init__(self):

        self.line_length = Descriptive()	#// Line lengths
        self.nempty_line = 0;#		// Number of whitespace lines.
        self.ncomment = 0 #			// Number of comments
        self.ncomment_char = 0;	#	// Number of comment characters
        self.nboilerplate_comment_char = 0;#	// Number of boilerplate (license) comment characters
        self.ndox_comment = 0    #		// Number of DOxygen comments
        self.ndox_comment_char = 0		#// Number of DOxygen comment characters
        self.nfunction = 0;			#// Number of functions
        self.ncpp_directive = 0;		#// Number of C preprocessor directives

        self.ncpp_include = 0;	#	// Number of include directives
        self.ninternal = 0;		#	// Number of internal visibility
                        #// declarations (static in file scope)
        self.nconst = 0  #;			// Number of const keywords
        self.nenum= 0  #;			// Number of enum keywords
        self.ngoto= 0  #;			// Number of goto statements
        self.ninline= 0  #;			// Number of inline keywords
        self.nnoalias= 0  #;			// Number of noalias keywords
        self.nregister= 0  #;			// Number of register keywords
        self.nrestrict= 0  #;			// Number of restrict keywords
        self.nsigned= 0  #;			// Number of signed keywords
        self.nstruct= 0  #;			// Number of struct keywords
        self.ntypedef= 0  #;			// Number of type definitions
        self.nunion= 0  #;			// Number of union keywords
        self.nunsigned= 0  #;			// Number of unsigned keywords
        self.nvoid= 0  #;			// Number of void keywords
        self.nvolatile= 0  #;			// Number of volatile keywords
        self.nfun_comment= 0  #;		// Number of comments in functions
        self.nfun_cpp_directive= 0  #;		// Number of C preprocessor directives
        #                // in functions
        self.ncpp_conditional = 0  #;		// Number of C preprocessor conditionals
        self.nfun_cpp_conditional= 0  #;	// Number of C preprocessor conditionals
                       # // in functions

        self.identifier = set() #;	// Unique identifiers
        self.identifier_length = Descriptive();
        self.unique_identifier_length = Descriptive();

        self.statement_nesting = Descriptive()  #;	// Statement nesting
        self.halstead = Descriptive();		#// Halstead complexity
        self.halstead_tracker = Halstead();
        self.cyclomatic = Descriptive()    #;		// Cyclomatic complexity
        self.indentation_spacing = Descriptive()    #// Spacing used for indentation
        self.cyclomatic_tracker = Cyclomatic();
        self.nstyle_hint = [0 for i in range(QualityMetrics.StyleHint.STYLE_HINT_SIZE.value)]

    
    #// The name for each metric in the enum. Needed for test reporting.
    metric_name = []

    def add_empty_line(self): 
        self.nempty_line+=1

    def add_line(self, length): 
        self.line_length.add(length)
    def add_statement(self, nesting):
        self.statement_nesting.add(nesting)

    def add_internal(self): 
        self.ninternal+=1
    def add_const(self): 
        self.nconst+=1
    def add_enum(self): 
        self.nenum+=1
    def add_goto(self): 
        self.ngoto+=1
    def add_inline(self): 
        self.ninline+=1
    def add_noalias(self): 
        self.nnoalias+=1
    def add_register(self): 
        self.nregister+=1
    def add_restrict(self): 
        self.nrestrict+=1
    def add_signed(self): 
        self.nsigned+=1
    def add_struct(self):
        self.nstruct+=1
    def add_typedef(self): 
        self.ntypedef+=1
    def add_union(self): 
        self.nunion+=1
    def add_unsigned(self): 
        self.nunsigned+=1
    def add_void(self): 
        self.nvoid+=1
    def add_volatile(self): 
        self.nvolatile+=1
    def add_comment(self): 
        self.ncomment+=1
    def add_fun_comment(self): 
        self.nfun_comment+=1
    def add_comment_char(self): 
        self.ncomment_char+=1
    def add_boilerplate_comment_chars(self,n):
        self.nboilerplate_comment_char += n;
    
    def add_dox_comment(self): 
        self.ndox_comment+=1
    def add_dox_comment_char(self): 
        self.ndox_comment_char+=1
    def remove_dox_comment_char(self): 
        self.ndox_comment_char-=1
    def add_cpp_directive(self): 
        self.ncpp_directive+=1
    def add_cpp_conditional(self): 
        self.ncpp_conditional+=1
    def add_cpp_include(self): 
        self.ncpp_include+=1
    def add_fun_cpp_directive(self):
        self.nfun_cpp_directive+=1
    def add_fun_cpp_conditional(self):
        self.nfun_cpp_conditional+=1
    #if defined(SHOW_STYLE_HINTS)
    def add_style_hint(self,*args):
        if len(args)>1:
            name = args[0].value
            num = args[1].value
            print ('Error', self.line_length.get_count() + 1,": ",name)
        else:
            num = args[0].value 
        self.nstyle_hint[num]+=1  # = self.nstyle_hint[num].value+1
    
    def begin_function(self):
        self.halstead_tracker.reset();
        self.cyclomatic_tracker.reset();
        self.nfunction+=1
    
    def end_function(self):
        self.halstead.add(self.halstead_tracker.complexity());
        self.cyclomatic.add(self.cyclomatic_tracker.extended_complexity());
       
    
    def add_operand(self,s):
        self.halstead_tracker.add(s)
    
    def add_path(self):
        self.cyclomatic_tracker.add_path();
    
    def add_short_circuit_operator(self,s):
        self.halstead_tracker.add(s);
        self.cyclomatic_tracker.add_boolean_branch();
    
    def add_operator(self,c):
        self.halstead_tracker.add(c)
    
    
    
    def add_indentation_spacing(self,s):
        self.indentation_spacing.add(s)
    
    def add_identifier(self, s):
        if (not s in self.identifier):
            self.unique_identifier_length.add(len(s));
            self.identifier.add(s)
        
        self.identifier_length.add(len( s));
    

    def get_line_length(self): 
        return self. line_length
    def get_nchar(self):
        return self.line_length.get_sum() + self.line_length.get_count();
    
    def  get_nempty_line(self):
        return self.nempty_line;
    
    def  get_nfunction(self): 
        return self.nfunction
    def get_statement_nesting(self):
        return self.statement_nesting
    
    def  get_ninternal(self): return self.ninternal
    def  get_nconst(self): return self.nconst
    def  get_nenum(self): return self.nenum
    def  get_ngoto(self): return self.ngoto
    def  get_ninline(self): return self.ninline
    def  get_nnoalias(self): return self.nnoalias
    def  get_nregister(self): return self.nregister
    def  get_nrestrict(self): return self.nrestrict
    def  get_nsigned(self): return self.nsigned
    def  get_nstruct(self): return self.nstruct
    def  get_ntypedef(self): return self.ntypedef
    def  get_nunion(self): return self.nunion
    def  get_nunsigned(self): return self.nunsigned
    def  get_nvoid(self): return self.nvoid
    def  get_nvolatile(self): return self.nvolatile
    def  get_ncomment(self): return self.ncomment
    def  get_ncomment_char(self): return self.ncomment_char
    def  get_nboilerplate_comment_char(self): return self.nboilerplate_comment_char
    def  get_ndox_comment(self): return self.ndox_comment
    def  get_ndox_comment_char(self): return self.ndox_comment_char
    def  get_nfun_comment(self): return self.nfun_comment
    #/// Return the code's weighted style inconsistency.
    
    def IA(self,val1,val2,ncases, inc_sum):
        return self.inconsistency_accumulate(val1,val2, ncases, inc_sum)

    def get_style_inconsistency(self):
        ncases = 0
        inc_sum = 0

        #define IA(a) inconsistency_accumulate(a, NO_ ## a, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP,QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_CLOSING_BRACE,QualityMetrics.StyleHint.NO_SPACE_AFTER_CLOSING_BRACE, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_COMMA,QualityMetrics.StyleHint.NO_SPACE_AFTER_COMMA, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD,QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_OPENING_BRACE,QualityMetrics.StyleHint.NO_SPACE_AFTER_OPENING_BRACE, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_SEMICOLON,QualityMetrics.StyleHint.NO_SPACE_AFTER_SEMICOLON, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_STRUCT_OP,QualityMetrics.StyleHint.NO_SPACE_AFTER_STRUCT_OP, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_BINARY_OP,QualityMetrics.StyleHint.NO_SPACE_BEFORE_BINARY_OP, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACE,QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_BRACE, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD,QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_BRACE,QualityMetrics.StyleHint.NO_SPACE_BEFORE_OPENING_BRACE, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_STRUCT_OP,QualityMetrics.StyleHint.NO_SPACE_BEFORE_STRUCT_OP, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_OPENING_SQUARE_BRACKET,QualityMetrics.StyleHint.NO_SPACE_AFTER_OPENING_SQUARE_BRACKET, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_AFTER_UNARY_OP,QualityMetrics.StyleHint.NO_SPACE_AFTER_UNARY_OP, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACKET,QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_BRACKET, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_SQUARE_BRACKET,QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_SQUARE_BRACKET, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_COMMA,QualityMetrics.StyleHint.NO_SPACE_BEFORE_COMMA, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_SQUARE_BRACKET,QualityMetrics.StyleHint.NO_SPACE_BEFORE_OPENING_SQUARE_BRACKET, ncases, inc_sum)
        ncases, inc_sum = self.IA(QualityMetrics.StyleHint.SPACE_BEFORE_SEMICOLON,QualityMetrics.StyleHint.NO_SPACE_BEFORE_SEMICOLON, ncases, inc_sum)
        

        return float(inc_sum) / float( ncases);

    #/*
    # * The global preprocessor directive functions include in their
    # * result the directives that occur within function bodies.
    # */
    def  get_ncpp_directive(self):
        return self.ncpp_directive
    def  get_ncpp_include(self):
        return self.ncpp_include
    def  get_ncpp_conditional(self): 
        return self.ncpp_conditional
    def  get_nfun_cpp_directive(self): 
        return self.nfun_cpp_directive
    def  get_nfun_cpp_conditional(self): 
        return self.nfun_cpp_conditional

    def get_halstead(self): return self.halstead
    def get_cyclomatic(self): return self.cyclomatic
    def get_indentation_spacing(self):
        return self.indentation_spacing;
    
    def get_identifier_length(self):
        return self.identifier_length;
    
    def get_unique_identifier_length(self):
        return self.unique_identifier_length;
    
    def  get_style_hint(self,e = None): 
        if e == None:
            return self.nstyle_hint
        return self.nstyle_hint[e]
    

#    friend class QualityMetricsTest;

    #/// Accumulate # cases and sum of two inconsistency measures.
    def inconsistency_accumulate(self, a,  b, ncases, inc_sum):
        ca = self.nstyle_hint[a.value];
        cb = self.nstyle_hint[b.value];

        ncases += ca + cb;
        inc_sum += QualityMetrics.inconsistency(ca,cb);
        return ncases,inc_sum
     #/// Unweighted inconsistency of two complimentary choices a and b.
    def inconsistency(a,b):
        if (a < b):
            return a
        else:
            return b




    def __repr__(self):
        out = [str(self.get_nchar())+'\t', 
                " line len: " + str(self.get_line_length()) + '\t'
                , " empty: " + str(self.get_nempty_line()) + '\t' ,
                " fun: " + str(self.get_nfunction()) + '\t' , 
                " nest: " + str(self.get_statement_nesting()) + '\t',
                " ninternal: " + str(self.get_ninternal()) + '\t' ,
                " nconst: " + str(self.get_nconst()) + '\t' ,
                " nenum: " + str(self.get_nenum()) + '\t' ,
                " ngoto: " + str(self.get_ngoto()) + '\t' ,
                " ninline: " + str(self.get_ninline()) + '\t' ,
                " nnoalias: " + str(self.get_nnoalias()) + '\t' ,
                " nregister: " + str(self.get_nregister()) + '\t',
                " nrestrict: " + str(self.get_nrestrict()) + '\t',
                " signed: " + str(self.get_nsigned()) + '\t' ,
                " struct: " + str(self.get_nstruct()) + '\t',
                " union: " + str(self.get_nunion()) + '\t' ,
                " nunsigned: " + str(self.get_nunsigned()) + '\t' ,
                " nvoid: " + str(self.get_nvoid()) + '\t' ,
                " nvolatile: " + str(self.get_nvolatile()) + '\t' ,
                " ntypedef: " + str(self.get_ntypedef()) + '\t' ,
                " comment: " + str(self.get_ncomment()) + '\t' ,
                str(self.get_ncomment_char()) + '\t' , 
                str(self.get_nboilerplate_comment_char()) + '\t' ,
                " comment: " + str(self.get_ndox_comment()) + '\t' ,
                str(self.get_ndox_comment_char()) + '\t' ,
                str(self.get_nfun_comment()) + '\t',
                " cpp: " + str(self.get_ncpp_directive()) + '\t' ,  
                str(self.get_ncpp_include()) + '\t' , 
                str(self.get_ncpp_conditional()) + '\t' ,
                str(self.get_nfun_cpp_directive()) + '\t' , 
                str(self.get_nfun_cpp_conditional()) + '\t',
                " inconsistency: " + str(self.get_style_inconsistency()) + '\t',
                " halstead: " + str(self.get_halstead()) + '\t',
                " cyclomatic: " + str(self.get_cyclomatic()) + '\t', 
                " id len: " + str(self.get_identifier_length()) + '\t',
                " unique id len: " + str(self.get_unique_identifier_length()) + '\t',
                " identation spacing: " + str(self.get_indentation_spacing()),
                " style: " +'\t'.join([str(e) for e in self.get_style_hint()])]
        return ''.join(out)

import unittest

class QualityMetricsTest(unittest.TestCase):
    
    def testCtor(self):
        q = QualityMetrics()
        self.assertEqual(q.get_nchar(), 0);
        self.assertEqual(q.get_ntypedef(), 0);
    

    def testNline(self):
        q = QualityMetrics()

        q.add_line(10);
        q.add_line(12);
        self.assertEqual(q.get_line_length().get_count(), 2);
    

    #// Uncovered specification error
    def testInconsistency(self):
        self.assertEqual(QualityMetrics.inconsistency(5, 0), 0);
        self.assertEqual(QualityMetrics.inconsistency(0, 5), 0);
        self.assertEqual(QualityMetrics.inconsistency(5, 5), 5);
        self.assertEqual(QualityMetrics.inconsistency(2, 4), 2);
        self.assertEqual(QualityMetrics.inconsistency(6, 2), 2);
        self.assertEqual(QualityMetrics.inconsistency(1, 100), 1);
    

    def testInconsistencyAccumulate(self):
        ncases = 0;
        inc_sum = 0;
        q = QualityMetrics()

        q.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP);
        q.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP);
        q.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP);
        ncases, inc_sum = q.inconsistency_accumulate(
                QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP,
                QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP, ncases,
                inc_sum);
        self.assertEqual(ncases, 4);
        self.assertEqual(inc_sum, 1);
    

    def testStyleInconsistency(self):
        q = QualityMetrics()

        q.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP);

        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_COMMA);
        q.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_COMMA);

        #// (1 + 3) inconsistent cases / out of 16 total
        self.assertEqual(q.get_style_inconsistency(), 0.25);   



if __name__ == '__main__':
    unittest.main()

