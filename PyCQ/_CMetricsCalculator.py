import sys
from ._CharSource import CharSource
from ._BolState import BolState
from ._CKeyword import CKeyword
from ._Boilerplate import Boilerplate
from ._QualityMetrics import QualityMetrics
from ._NestingLevel import NestingDetails, NestingLevel
from io import StringIO


def isspace(char):
    return char==' '

def is_eol_char(c):
    return (c == '\r' or c == '\n')




class CMetricsCalculator:
    
    def __init__(self, s = StringIO("")):

        self.src = CharSource(s)
        self.qm = QualityMetrics()
        self.bol = BolState();
        self.top_level_depth = 0		##// 0 for C, 1 for Java
        self.current_depth = 0		#// Keeps track of { }
        self.scan_cpp_directive = True	#// Keyword after a C preprocessor #
        self.scan_cpp_line = False		#// Line after a C preprocessor #
        self.in_function = False      #;		// True when scanning functions

        self.in_dox_comment = False		#// True if processing a DOxygen comment
        self.chars_read_at_bol = 0		#// Characters that were read
                    #// at the beginning of a line
        #/** Bracket balance for control statememts. */
        self.stmt_bracket_balance = 0
        self.line_bracket_balance = 0	#// Bracket balance for each line
        self.line_nesting = 0	#	// Nesting of current line
        #/** Indentation of preceding indented line. */
        self.previous_indentation = 0
        self.continuation = False		#// True if a statement continuation line
        #/** True for keywords that don't end with semicolon */
        self.saw_non_semicolon_keyword = False;
        self.saw_unindent = False;#		// True if line is unindented
        self.saw_comment = False;	#	// True after a comment
        self.saw_cpp_directive = False	#	// True after c preprocessor directive
        self.indentation_list = False	#	// List indentation for each line
        self.nesting = NestingLevel()	#	// Track nesting level
        self.ckeyword = CKeyword()
        #/** Verify the coding style of binary operators */




    
    def calculate_metrics(self):
        self.calculate_metrics_loop();
        #// No newline at EOF
        if (self.chars_read_at_bol != self.src.get_nchar()):

            self.qm.add_line(self.src.get_nchar() - self.chars_read_at_bol)
    
    def get_metrics(self):
        return self.qm

    def enable_indentation_list(self):
        self.indentation_list = True




    
    
    
    def binary_style(self,before):
    
        #// Avoid complaining about missing space after <stdio.h>
        if (self.scan_cpp_line):
            return
        if (isspace(before)):
            self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_BINARY_OP)
        else:
            self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_BINARY_OP)
        if (isspace(self.src.char_after())):
            self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP)
        else:
            self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP)
    

    
    def keyword_style(self, before, allowed = None):
    
        if (self.scan_cpp_line):
            return;
        if (before != allowed):
            if (isspace(before)):
                self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD)
            else:
                self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD);
        
        if (isspace(self.src.char_after())):
            self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD)
        else:
            self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD)
    

    def keyword_style_left_space(self,before):
    
        if (self.scan_cpp_line):
            return;
        if (isspace(before)):
            self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD);
        else:
            self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD);
    

    def newline(self,in_non_code_block= False):
    
        if (self.in_function and (not self.continuation) and (not self.saw_cpp_directive) and (not in_non_code_block)):
            expected = self.line_nesting
            if (self.saw_unindent and expected > 0):
                expected-=1
            #// Calculation seems to be off: prevent division by zero
            if (expected < 0):
                expected = 0
            #// Actual indentation spacing in units of spaces (e.g. 8 or 4)
            spacing = self.bol.get_indentation() / float(expected + 1);
            if (self.bol.get_indentation()):
                if (self.indentation_list):
                    print ( self.qm.get_line_length().get_count() + 1,": e: ", expected," i: ", self.bol.get_indentation()," s: " , spacing )
                self.qm.add_indentation_spacing(spacing)
            
            previous_indentation = self.bol.get_indentation();
        

        if (self.bol.at_bol_space()):
            self.qm.add_empty_line();

        eol_ptr = 0;
        #c = self.src.char_before();
        c = self.src.char_before(1);
        #// Skip over \r in \r\n
        if (c == '\r'):
            c = self.src.char_before(2)
            #c = self.src.char_before()
        #// Allow empty lines
        if (c != '\n' and isspace(c)):
            self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AT_END_OF_LINE);

        #// Find first non-blank character
        while (c and c != '\n' and isspace(c)):
            c = self.src.char_before(++eol_ptr)
        #/*
        # * Heuristic: determine whether the next line could be a continuation
        # * line (where indentation practices vary widely).
        # * The following cases:
        # * Lines ending in ;{}
        # * Empty lines
        # * Comments (although they could be commenting long statement)
        # * C preprocessor directives
        # * A complete for(), while(), if(), ... statement
        # */
        self.not_continuation = (c == ';' or c == '{' or c == '}' or c == '\n' or self.saw_comment or self.saw_cpp_directive or 
            (self.saw_non_semicolon_keyword and self.line_bracket_balance == 0))
        self.continuation = not self.not_continuation

        self.bol.saw_newline();
        #// Line length minus the newline
        self.qm.add_line(self.src.get_nchar() - self.chars_read_at_bol - 1);
        self.chars_read_at_bol = self.src.get_nchar();
        self.line_bracket_balance = 0;
        self.saw_non_semicolon_keyword = False;
        self.saw_unindent = False;
        self.saw_comment = False;
        self.saw_cpp_directive = False;
        self.line_nesting = self.nesting.get_nesting_level();
    

    #def GET(self,x):
    #    ret, x = self.src.get(x) 
    #    if ( not ret):
    #        return False
            

    def calculate_metrics_switch(self):
    
        c0 = None
        c1 = None
        before = None	#// The character before the current token
        val = ''
        key = None
        bp = Boilerplate()

    

        ret, c0 = self.src.get(c0) 
        if (not ret):
            return False
        
        if c0 == '\n':
            self.newline();
            self.scan_cpp_line = False
            
        elif c0 in [' ', '\t', '\v', '\f', '\r']:
            self.bol.saw_space(c0);
            
        elif c0 == '?':
            self.bol.saw_non_space();
            self.binary_style(self.src.char_before());
            self.qm.add_short_circuit_operator("?");
            
        elif c0 == '[':
            if (isspace(self.src.char_before())):
                self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_SQUARE_BRACKET)
            else:
                self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_OPENING_SQUARE_BRACKET);
            if (isspace(self.src.char_after())):
                self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_OPENING_SQUARE_BRACKET);
            else:
                self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_OPENING_SQUARE_BRACKET);
            self.bol.saw_non_space();
            self.qm.add_operator(c0);
            
        elif c0 == '(':
            self.bol.saw_non_space();
            self.qm.add_operator(c0);
            self.stmt_bracket_balance+=1;
            self. line_bracket_balance+=1
            
        elif c0 == '~':
            #/*
            # * Unary operators can have space before them
            # * as in "a | ~b", or not, as in "foo(~b)".
            # */
            if (isspace(self.src.char_after())):
                self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_UNARY_OP);
            else:
                self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_UNARY_OP);
            self.bol.saw_non_space();
            self.qm.add_operator(c0);
            
        elif c0 == ',':
            if (isspace(self.src.char_before())):
                self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_COMMA);
            else:
                self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_COMMA);
            if (isspace(self.src.char_after())):
                self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_COMMA);
            else:
                self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_COMMA);
            self.bol.saw_non_space();
            self.qm.add_operator(c0);
            
        elif c0 == ']':
            if (isspace(self.src.char_before())):
                self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_SQUARE_BRACKET);
            else:
                self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_SQUARE_BRACKET);
            self.bol.saw_non_space();
            
        elif c0 == ')':
            if (isspace(self.src.char_before())):
                self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACKET);
            else:
                self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_BRACKET);
            self.bol.saw_non_space();
            self.stmt_bracket_balance-=1
            self.line_bracket_balance-=1
            
        elif c0 == '{':
            if (self.in_function):
                if (isspace(self.src.char_before())):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_BRACE);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_OPENING_BRACE);
                if (isspace(self.src.char_after())):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_OPENING_BRACE);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_OPENING_BRACE);
                self.nesting.saw_open_brace(self.bol.at_bol_space() and (self.bol.get_indentation() > self.previous_indentation));
            
            #// Heuristic: functions begin with { at first column
            if (self.bol.at_bol()):
                self.current_depth = 0;
                self.qm.begin_function()
                self.in_function = True;
                self.nesting.reset();
            
            self.bol.saw_non_space();
            self.current_depth+=1
            
        elif c0 == '}':
            self.current_depth-=1
            self.saw_unindent = True;
            if (self.in_function):
                if (isspace(self.src.char_before())):
                    if (not is_eol_char(self.src.char_before())):
                        self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACE);
                else: 
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_BRACE);
                if (isspace(self.src.char_after())):
                    if (not is_eol_char(self.src.char_after())):
                        self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_CLOSING_BRACE);
                else: 
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_CLOSING_BRACE);
                self.nesting.saw_close_brace();
                if (self.current_depth == self.top_level_depth):
                    self.qm.end_function();
                    self.in_function = False;
                
            
            self.bol.saw_non_space();
            
        elif c0 == ';':
            #// Allow a single ; on a line
            if (not self.bol.at_bol_space()):
                if (isspace(self.src.char_before())):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_SEMICOLON);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_SEMICOLON);
            
            if (self.src.char_after() != ';' and self.src.char_after() != ')'):#// Handle "for (;;)"
                if (isspace(self.src.char_after())):
                    if (not is_eol_char(self.src.char_after())):
                        self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_SEMICOLON);
                else: 
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_SEMICOLON);
            
            self.bol.saw_non_space();
            #// Do not add statements in for (x;y;z)
            if (self.in_function and self.stmt_bracket_balance == 0):
                self.qm.add_statement(self.nesting.get_nesting_level());
                self.nesting.saw_statement_semicolon();
            
            
        #/*
        # * Double character C tokens with more than 2 different outcomes
        # * (e.g. +, +=, ++)
        # */
        elif c0 == '+':
            self.bol.saw_non_space();
            before = self.src.char_before()
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            
            if c0 ==  '+':
                #// Could be prefix or postfix; no style checks
                if (self.in_function):
                    self.qm.add_operator("++");
                
            elif c0 == '=':
                self.binary_style(before);
                if (self.in_function):
                    self.qm.add_operator("+=");
                
            else:
                #// Could be unary operator, no style critique here
                self.src.push(c0)
                if (self.in_function):
                    self.qm.add_operator('+');
                
            
            
        elif c0 == '-':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if c0 == '-':
                #// Could be prefix or postfix; no style checks
                if (self.in_function):
                    self.qm.add_operator("--");
                
            elif c0 == '=':
                self.binary_style(before);
                if (self.in_function):
                    self.qm.add_operator("-=");
                
            elif c0 == '>':
                if (isspace(before)):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_STRUCT_OP);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_STRUCT_OP);
                if (isspace(self.src.char_after())):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_STRUCT_OP);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_STRUCT_OP);
                if (self.in_function):
                    self.qm.add_operator("->")
                
            else:
                #// Could be unary operator, no style critique here
                self.src.push(c0);
                if (self.in_function):
                    self.qm.add_operator('-');
                
            
            
        elif c0 == '&':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if c0 == '&':
                self.binary_style(before)
                if (self.in_function):
                    self.qm.add_short_circuit_operator("&&")
                
            elif c0 == '=':
                self.binary_style(before)
                if (self.in_function):
                    self.qm.add_operator("&=");
                
            else:
                #// Could be unary operator, no style critique here
                self.src.push(c0);
                if (self.in_function): 
                    self.qm.add_operator('&');
                
                        
        elif c0 == '|':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if c0 == '|':
                self.binary_style(before);
                if (self.in_function):
                    self.qm.add_short_circuit_operator("||");
                
            elif c0 == '=':
                self.binary_style(before);
                if (self.in_function):
                    self.qm.add_operator("|=");                
            else:
                self.src.push(c0);
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator('|');
                
            
            
        elif c0 == ':':
            self.bol.saw_non_space();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            
            if c0 == ':':		#// C++ ::
                pass
            else:
                self.src.push(c0);
                #// Can be "a ? b : c" or "case 42:"
                if (isspace(self.src.char_after())):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP);
                
            
            
        #/* Simple single/double character tokens (e.g. !, !=) */
        elif c0 == '!':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if (c0 == '='):
                self.binary_style(before);
                if (self.in_function): 
                    self.qm.add_operator("!=")
            else:
                self.src.push(c0);
                if (isspace(self.src.char_after())):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_UNARY_OP);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_UNARY_OP);
                if (self.in_function): self.qm.add_operator('!');
            
        elif c0 == '%':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if (c0 == '='):
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator("%=");
                
            
            self.src.push(c0);
            self.binary_style(before);
            if (self.in_function): self.qm.add_operator('%');
            
        elif c0 == '*':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if (c0 == '=') :
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator("*=");
            else:
                #// Could be unary or binary
                #// All bets are off regarding style
                self.src.push(c0)
                if (self.in_function): self.qm.add_operator('*')
            
        elif c0 == '=':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if (c0 == '=') :
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator("==");
            else:
                self.src.push(c0);
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator('=');
            
            
        elif c0 == '^':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if (c0 == '=') :
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator("^=");
            else:
                self.src.push(c0);
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator('^');
            
            
        elif c0 == '#':
            if (self.bol.at_bol_space()):
                self.qm.add_cpp_directive();
                if (self.in_function):
                    self.qm.add_fun_cpp_directive();
                self.scan_cpp_directive = True;
                self.scan_cpp_line = True;
                self.saw_cpp_directive = True;
            
            self.bol.saw_non_space();
            
        #/* Operators starting with < or > */
        elif c0 == '>':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            
            if c0 == '=':	      #			/* >= */
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator(">=");
                
            elif c0 == '>':
                ret, c0 = self.src.get(c0) 
                if (not ret):
                    return False
                if (c0 == '=') :	#/* >>= */
                    self.binary_style(before);
                    if (self.in_function): self.qm.add_operator(">>=");
                else:		#	/* >> */
                    self.src.push(c0);
                    self.binary_style(before);
                    if (self.in_function): self.qm.add_operator(">>");
                
                
            else:#				/* > */
                self.src.push(c0);
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator('>');
                
            
            
        elif c0 == '<':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            
            if c0 == '=':		#		/* <= */
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator("<=");
                
            elif c0 == '<':
                ret, c0 = self.src.get(c0) 
                if (not ret):
                    return False
                if (c0 == '=') :	#/* <<= */
                    self.binary_style(before);
                    if (self.in_function): self.qm.add_operator("<<=");
                else:		#	/* << */
                    self.src.push(c0);
                    self.binary_style(before);
                    if (self.in_function): self.qm.add_operator("<<");
                
                
            else:	#			/* < */
                self.src.push(c0);
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator('<');
                
            
            
        #/* Comments and / operators */
        elif c0 == '/':
            self.bol.saw_non_space();
            before = self.src.char_before();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            
            if c0 == '=':	#			/* /= */
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator("/=");
                
            elif c0 == '*':	#			/* Block comment */
                self.qm.add_comment();
                if (self.in_function):
                    self.qm.add_fun_comment();
                bp.begin_comment();
                ret, c0 = self.src.get(c0) 
                if (not ret):
                    return False
                bp.process_char(c0);
                if (c0 == '\n'):
                    self.newline(True);
                elif (c0 == '*'):
                    #// DOxygen block comment
                    self.in_dox_comment = True;
                    self.qm.add_dox_comment();
                    self.qm.remove_dox_comment_char();
                
                while True:
                    while (c0 != '*'):
                        if (not isspace(c0) and self.bol.at_bol_space()):
                            self.bol.saw_non_space();
                        self.qm.add_comment_char();
                        if (self.in_dox_comment):
                            self.qm.add_dox_comment_char()
                        ret, c0 = self.src.get(c0) 
                        if (not ret):
                            return False
                        bp.process_char(c0)
                        if (c0 == '\n'):
                            self.newline(True)
                    
                    if (not isspace(c0) and self.bol.at_bol_space()):
                        self.bol.saw_non_space();
                    ret, c0 = self.src.get(c0) 
                    if (not ret):
                        return False
                    bp.process_char(c0)
                    if (c0 == '/'): 
                        self.saw_comment = True;
                        self.in_dox_comment = False;
                        break
                    else:
                        if (c0 == '\n'):
                            self.newline()
                        self.qm.add_comment_char();
                        if (self.in_dox_comment):
                            self.qm.add_dox_comment_char();
                    
                
                self.qm.add_boilerplate_comment_chars(bp.get_boilerplate_chars())
                
            elif c0 == '/':	#			/* Line comment */
                self.qm.add_comment();
                if (self.in_function):
                    self.qm.add_fun_comment();
                ret, c0 = self.src.get(c0) 
                if (not ret):
                    return False
                if (c0 == '/'): 
                    #// DOxygen line comment
                    self.in_dox_comment = True;
                    self.qm.add_dox_comment();
                
                while True:
                    if (c0 == '\n'):
                        break                        
                    self.qm.add_comment_char();
                    if (self.in_dox_comment):
                        self.qm.add_dox_comment_char();
                    ret, c0 = self.src.get(c0) 
                    if (not ret):
                        return False
                
                self.src.push(c0);
                self.saw_comment = True;
                self.in_dox_comment = False;
                
            else:	#			/* / */
                self.src.push(c0);
                self.binary_style(before);
                if (self.in_function): self.qm.add_operator('/');
                
            
            
        elif c0 == '.':	#/* . and ... */
            self.bol.saw_non_space();
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if (c0.isdigit()):
                val = "." + str(c0)
                
                while True:
                    ret, c0 = self.src.get(c0) 
                    if (not ret):
                        return False
                    if (c0 == 'e' or c0 == 'E'):
                        val += c0;
                        ret, c0 = self.src.get(c0) 
                        if (not ret):
                            return False
                        if (c0 == '+' or c0 == '-'):
                            val += c0;
                            continue;
                    
                
                    if (not c0.isalnum() and c0 != '.' and c0 != '_'):
                        break
                    val += c0
            
                self.src.push(c0);
                self.qm.add_operand(val);


            if (c0 != '.'):
                self.src.push(c0);
                if (isspace(self.src.char_before())):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_BEFORE_STRUCT_OP);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_BEFORE_STRUCT_OP);
                if (isspace(self.src.char_after())):
                    self.qm.add_style_hint(QualityMetrics.StyleHint.SPACE_AFTER_STRUCT_OP);
                else:
                    self.qm.add_style_hint(QualityMetrics.StyleHint.NO_SPACE_AFTER_STRUCT_OP);
                if (self.in_function): self.qm.add_operator('.')
                
            
            ret, c1 = self.src.get(c1) 
            if (not ret):
                return False
            if (c1 != '.'):
                self.src.push(c1);
                self.src.push(c0);
                if (self.in_function): self.qm.add_operator('.');
                
            
            #// Elipsis
            
        #/* Could be a long character or string */
        elif c0 == 'L':
            self.bol.saw_non_space();
            ret, c1 = self.src.get(c1) 
            if (not ret):
                return False
            if c1 == '\'':
                val = "";
                while True:
                    ret, c1 = self.src.get(c1) 
                    if (not ret):
                        return False
                    if (c1 == '\\'):
                        #// Consume one character after the backslash
                        #// ... to deal with the '\'' problem
                        val += '\\'
                        ret, c1 = self.src.get(c1) 
                        if (not ret):
                            return False
                        val += c1;
                        continue;
                
                    if (c1 == '\''):
                        break;
                    val += c1;
            
                self.qm.add_operand(val);



            elif c1 == '"':


                val = "";
                while True:
                    ret, c1 = self.src.get(c1) 
                    if (not ret):
                        return False
                    if (c1 == '\\'):
                        val += '\\';
                        #// Consume one character after the backslash
                        ret, c1 = self.src.get(c1) 
                        if (not ret):
                            return False
                        if (c1 == '\n'):
                            self.newline(True);
                        val += c1;
                        continue;
                    elif (c1 == '"'):
                        break
                    elif (c1 == '\n'):
                        self.newline(True);
                    val += c1;
            
                self.qm.add_operand(val);


            else:
                self.src.push(c1);
                self.checkIdentifier(c0)
            
        elif c0=='_' or (ord(c0) >=ord('a') and ord(c0)<=ord('z')) or (ord(c0) >=ord('A') and ord(c0)<=ord('Z')):
        
        #identifier:
            self.checkIdentifier(c0)

            
        elif c0== '\'':
            self.bol.saw_non_space();
        #char_literal:
            val = "";
            while True:
                ret, c0 = self.src.get(c0) 
                if (not ret):
                    return False
                if (c0 == '\\'):
                    #// Consume one character after the backslash
                    #// ... to deal with the '\'' problem
                    val += '\\'
                    ret, c0 = self.src.get(c0) 
                    if (not ret):
                        return False
                    val += c0;
                    continue;
                
                if (c0 == '\''):
                    break;
                val += c0;
            
            self.qm.add_operand(val);
            
        elif c0 == '"':
            self.bol.saw_non_space();
        #string_literal:
            val = "";
            while True:
                ret, c0 = self.src.get(c0) 
                if (not ret):
                    return False
                if (c0 == '\\'):
                    val += '\\';
                    #// Consume one character after the backslash
                    ret, c0 = self.src.get(c0) 
                    if (not ret):
                        return False
                    if (c0 == '\n'):
                        self.newline(True);
                    val += c0;
                    continue;
                elif (c0 == '"'):
                    break
                elif (c0 == '\n'):
                    self.newline(True);
                val += c0;
            
            self.qm.add_operand(val);
            
        #/* Various numbers */
        elif c0 in ['0','1','2', '3', '4', '5','6','7','8','9']:
            self.bol.saw_non_space();
            val = c0
        #number:
            while True:
                ret, c0 = self.src.get(c0) 
                if (not ret):
                    return False
                if (c0 == 'e' or c0 == 'E'):
                    val += c0;
                    ret, c0 = self.src.get(c0) 
                    if (not ret):
                        return False
                    if (c0 == '+' or c0 == '-'):
                        val += c0;
                        continue;
                    
                
                if (not c0.isalnum() and c0 != '.' and c0 != '_'):
                    break
                val += c0
            
            self.src.push(c0);
            self.qm.add_operand(val);
            
        else:
            pass
        
        return True;
    

    def calculate_metrics_loop(self):
    
        while (self.calculate_metrics_switch()):            
            pass
        
    def checkIdentifier(self, c0):
        before = self.src.char_before();
        self.bol.saw_non_space();
        val = c0;
        while True:
            ret, c0 = self.src.get(c0) 
            if (not ret):
                return False
            if (not c0.isalnum() and c0 != '_'):
                break
                    
            val += c0
            
        self.src.push(c0);
        key = self.ckeyword.identifier_type(val)
        if key == CKeyword.IdentifierType.FOR or key == CKeyword.IdentifierType.WHILE:
            self.nesting.saw_nesting_keyword(key);
            self.keyword_style(before)
            self.qm.add_path();
            self.stmt_bracket_balance = 0;
            self.saw_non_semicolon_keyword = True
                
        elif key == CKeyword.IdentifierType.CASE:
            self.keyword_style(before);
            self.qm.add_path();
            self.stmt_bracket_balance = 0;
            self.saw_non_semicolon_keyword = True;
            self.saw_unindent = True;
                
        elif key == CKeyword.IdentifierType.CONST:
            self.keyword_style(before, '(');
            self.qm.add_const();
                
        elif key == CKeyword.IdentifierType.DEFAULT:
            self.keyword_style_left_space(before)
            self.qm.add_path();
            self.stmt_bracket_balance = 0;
            self.saw_non_semicolon_keyword = True;
            self.saw_unindent = True;
                
        elif key == CKeyword.IdentifierType.GOTO:
            self.keyword_style(before);
            self.qm.add_goto();
            self.stmt_bracket_balance = 0;
                
        elif key == CKeyword.IdentifierType.REGISTER:
            self.keyword_style(before);
            self.qm.add_register();
                
        elif key == CKeyword.IdentifierType.SIGNED:
            self.keyword_style(before, '(');
            self.qm.add_signed();
                
        elif key == CKeyword.IdentifierType.STATIC:
            if (not self.in_function):
                self.qm.add_internal();
                
        elif key == CKeyword.IdentifierType.TYPEDEF:
            self.qm.add_typedef();
                
        elif key == CKeyword.IdentifierType.ENUM:
            self.qm.add_enum();
            self.keyword_style(before, '(');
                
        elif key == CKeyword.IdentifierType.INLINE:
            self.keyword_style(before, '(');
            self.qm.add_inline();
                
        elif key == CKeyword.IdentifierType.NOALIAS:
            self.keyword_style(before, '(');
            self.qm.add_noalias();
                
        elif key == CKeyword.IdentifierType.RESTRICT:
            self.keyword_style(before, '(');
            self.qm.add_restrict();
                
        elif key == CKeyword.IdentifierType.STRUCT:
            self.qm.add_struct();
            self.keyword_style(before, '(');
                
        elif key == CKeyword.IdentifierType.UNION:
            self.qm.add_union();
            self.keyword_style(before, '(');
                
        elif key == CKeyword.IdentifierType.UNSIGNED:
            self.keyword_style(before, '(');
            self.qm.add_unsigned();
                
        elif key == CKeyword.IdentifierType.VOID:
            self.keyword_style(before, '(');
            self.qm.add_void();
                
        elif key == CKeyword.IdentifierType.VOLATILE:
            self.keyword_style(before, '(');
            self.qm.add_volatile();
                
        elif key == CKeyword.IdentifierType.DO or key ==  CKeyword.IdentifierType.SWITCH:
            self.nesting.saw_nesting_keyword(key);
            self.keyword_style(before);
            self.stmt_bracket_balance = 0;
            self.saw_non_semicolon_keyword = True;
                
        elif key == CKeyword.IdentifierType.BREAK or key ==  CKeyword.IdentifierType.CONTINUE or key == CKeyword.IdentifierType.RETURN:
            self.keyword_style_left_space(before);
            self.stmt_bracket_balance = 0;
                
        elif key == CKeyword.IdentifierType.OTHER:
            pass
        elif key == CKeyword.IdentifierType.INCLUDE:
            if (self.scan_cpp_directive):
                self.qm.add_cpp_include();
                                
            self.checkIdentifier(c0)
        elif key == CKeyword.IdentifierType.ELSE:
            if (not self.scan_cpp_directive):
                self.nesting.saw_nesting_keyword(key);
                self.line_nesting = self.nesting.get_nesting_level() - 1;
                self.saw_unindent = False;	#// else: 
                self.keyword_style(before);
                self.saw_non_semicolon_keyword = True;
                self.stmt_bracket_balance = 0;
                                
        elif key == CKeyword.IdentifierType.IF:
            if (self.scan_cpp_directive):
                self.qm.add_cpp_conditional();
                if (self.in_function):
                    self.qm.add_fun_cpp_conditional();
            else:
                self.nesting.saw_nesting_keyword(key);
                self.keyword_style(before);
                self.qm.add_path();
                self.stmt_bracket_balance = 0;
                self.saw_non_semicolon_keyword = True;
                
                
        elif key == CKeyword.IdentifierType.IFDEF or key == CKeyword.IdentifierType.ELIF:
            if (self.scan_cpp_directive):
                #// #if
                if (self.in_function):
                    self.qm.add_fun_cpp_conditional();
                else:
                    self.qm.add_cpp_conditional();
                    
                
            if (not self.scan_cpp_directive):
                self.qm.add_operand(val);
                self.qm.add_identifier(val);
                
            
        elif key == CKeyword.IdentifierType.IDENTIFIER:
        #plain_identifier:
            if (not self.scan_cpp_directive):
                self.qm.add_operand(val);
                self.qm.add_identifier(val);
                
                
            
        self.scan_cpp_directive = False;
        return True


from io import StringIO

import unittest


class CMetricsCalculatorTest(unittest.TestCase):
    

    class PSTest:
        def __init__(self, prefix, suffix, e, result):        
            self.prefix = prefix
            self.suffix = suffix
            self.e = e
            self.result = result
    

    def testCtor(self):
        calc = CMetricsCalculator()

        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_nchar(), 0);
        self.assertEqual(qm.get_line_length().get_count(), 0);
        self.assertEqual(qm.get_line_length().get_sum(), 0);
    

    def testLine(self):
        tstring = StringIO("hi\nt-\naa")
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics()
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_nchar(), 9);
        self.assertEqual(qm.get_line_length().get_count(), 3);
    

    def testNEmptyLine(self):
        tstring = StringIO("foo()\n{int bar;\n\n\r\n}\n}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_nempty_line(), 2);
    

    def testNFunction(self):
        tstring = StringIO("foo()\n{((??}\nstruct bar {}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_nfunction(), 1);
    

    def testHalsteadOperator(self):
        tstring = StringIO("foo()\n{((??}\nstruct bar {}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_halstead().get_count(), 1);
        self.assertEqual(qm.get_halstead().get_mean(), 4.);
    

    def testHalsteadOperand(self):
        tstring = StringIO("foo()\n{a a b b}\nstruct bar {}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_halstead().get_count(), 1);
        self.assertEqual(qm.get_halstead().get_mean(), 4.0);


    def testHalsteadOperandTwoFunctions(self):
        tstring = StringIO("foo()\n{a a b b}bar()\n{a a b b}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_halstead().get_count(), 2);
        self.assertEqual(qm.get_halstead().get_mean(), 4.0);
    

    def testNStatement(self):
        tstring = StringIO("foo()\n{a;b;c;}\nint a;");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_statement_nesting().get_count(), 3);
    

    def testStatementNesting(self):
        tstring = StringIO("foo()\n{a;if (1) {b; if (2) c;}}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_statement_nesting().get_count(), 3);
        #// (0 + 1 + 2) / 3 == 1
        self.assertEqual(qm.get_statement_nesting().get_mean(), 1.);
        self.assertEqual(2, qm.get_statement_nesting().get_max());
    

    #// Used to test error found in use (Issue 8)
    def testStatementNestingCase(self):
        tstring = StringIO("f()\n{\nf:\n {\n ;\n }\nf:\n {\n ;\n }\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(1, qm.get_statement_nesting().get_max());
    

    def testStatementNestingTwoFunction(self):
        tstring = StringIO("foo()\n{a;if(1) if(2) c;\n}\n"+	"bar()\n{if(1){a;if(1){b;if(1){if(1){if(1){c;}}} d; }}}");			
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_statement_nesting().get_count(), 6);
        #// (0 + 3 + 1 + 2 + 6 + 2)  == 12; 12 / 6 == 2
        self.assertEqual(qm.get_statement_nesting().get_mean(), 2.0);
    

    def testNBlockComment(self):
        tstring = StringIO("/* hi\n * / */\n"+"fun()\n{\n/* block */\n}\n")
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ncomment(), 2);
        self.assertEqual(qm.get_nfun_comment(), 1);

        tstring = StringIO("/* hi\n * / */ /**//* */");
        calc2 = CMetricsCalculator(tstring)
        calc2.calculate_metrics();
        qm2 = calc2.get_metrics()
        self.assertEqual(qm2.get_ncomment(), 3);
    

    def testDoxComment(self):
        tstring = StringIO("/** hi\n */\n/* no dox */\n/// foo\n// No dox\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ndox_comment(), 2);
        self.assertEqual(qm.get_ncomment(), 4);

        tstring = StringIO("///Hi\n");
        calc2 = CMetricsCalculator(tstring)
        calc2.calculate_metrics();
        qm2 = calc2.get_metrics()
        self.assertEqual(qm2.get_ndox_comment_char(), 3);

        tstring = StringIO("/**hi*/\n");
        calc3 = CMetricsCalculator(tstring)
        calc3.calculate_metrics();
        qm3 = calc3.get_metrics()
        self.assertEqual(qm3.get_ndox_comment_char(), 2);
    

    def testNLineComment(self):
        tstring = StringIO(" // hi\n / /\n"+"fun()\n{\n f // line /* */\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ncomment(), 2);
        self.assertEqual(qm.get_nfun_comment(), 1);

        tstring = StringIO(" // hi\n //\n");
        calc2 = CMetricsCalculator(tstring)
        calc2.calculate_metrics();
        qm2 = calc2.get_metrics()
        self.assertEqual(qm2.get_ncomment(), 2);
    

    def testNBlockCommentChar(self):
        tstring = StringIO("/* hi\n * / */ /  there !\n");
        #//                       123 456789
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ncomment(), 1);
        self.assertEqual(qm.get_ncomment_char(), 9);
    

    def testNLineCommentChar(self):
        tstring = StringIO("// hi  * /  there */\n");
        #//                       123456789012345678
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ncomment(), 1);
        self.assertEqual(qm.get_ncomment_char(), 18);
    

    def testNCommentChar(self):
        tstring = StringIO("/* hi\n * / */ // there /*\n");
     #//                       123 456789     012345678
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ncomment(), 2);
        self.assertEqual(qm.get_ncomment_char(), 18);


    def testCyclomaticBoolean(self):
        tstring = StringIO("foo()\n{a && b && d || c (?}\nstruct bar { a = d && e}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_cyclomatic().get_count(), 1);
     #// One path plus four additional ones
        self.assertEqual(qm.get_cyclomatic().get_mean(), 5.);

    def testCyclomaticLogical(self):
        tstring = StringIO("foo()\n{for while case default if do switch}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
     #// One path plus five additional ones
        self.assertEqual(qm.get_cyclomatic().get_mean(), 6.);

    def testCyclomaticLogicalTwoFunctions(self):
        tstring = StringIO("foo()\n{for (;;) {while () switch (self):case 2: default:}} if (); do }  \n bar()\n{ if }");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
     #// ((1 + 5) + (1 + 1))
        self.assertEqual(qm.get_cyclomatic().get_count(), 2);
        self.assertEqual(qm.get_cyclomatic().get_mean(), 4.);


    def testCyclomaticCombined(self):
        tstring = StringIO("foo()\n{for while case default}"
            +"bar()\n{a && b && d}\nstruct bar { a = d && e}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_cyclomatic().get_count(), 2);
     #// ((4 + 1) + (2 + 1)) / 2
        self.assertEqual(qm.get_cyclomatic().get_mean(), 4.);

    def testCppDirective(self):
        tstring = StringIO("#include <stdio.h>\n\t #define a #b\n#ifdef foo\n#if bar\n#elif k\n#endif\n"
            +"foo()\n{\n#if FOO\n#undef a\n}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ncpp_directive(), 8);
        self.assertEqual(qm.get_nfun_cpp_directive(), 2);
        self.assertEqual(qm.get_ncpp_conditional(), 4);
        self.assertEqual(qm.get_nfun_cpp_conditional(), 1);
        self.assertEqual(qm.get_ncpp_include(), 1);

    def testInternal(self):
        tstring = StringIO("static a; static b;\nint\nfoo()\n{\n\tstatic d;\n}\n" );
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ninternal(), 2);

    def testCKeyword(self):
        tstring = StringIO("register x; typedef int a; typedef double b; typedef short s;\ngoto c; goto d; void, void, void, void;" );
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_ngoto(), 2);
        self.assertEqual(qm.get_ntypedef(), 3);
        self.assertEqual(qm.get_nregister(), 1);
        self.assertEqual(qm.get_nvoid(), 4);

    def testCKeyword2(self):
        tstring = StringIO("signed unsigned unsigned const const const volatile volatile volatile volatile noalias noalias noalias noalias noalias;" );
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_nsigned(), 1);
        self.assertEqual(qm.get_nunsigned(), 2);
        self.assertEqual(qm.get_nconst(), 3);
        self.assertEqual(qm.get_nvolatile(), 4);
        self.assertEqual(qm.get_nnoalias(), 5);


    def testCKeyword3(self):
        tstring = StringIO("struct union union enum enum enum;" );
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_nstruct(), 1);
        self.assertEqual(qm.get_nunion(), 2);
        self.assertEqual(qm.get_nenum(), 3);


    def testCKeyword4(self):
        tstring = StringIO("restrict inline inline;" );
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_nrestrict(), 1);
        self.assertEqual(qm.get_ninline(), 2);


    def testIdentifierLength(self):
        tstring = StringIO("#define aa bab(123)\n if (aa == b)");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_identifier_length().get_count(), 4);
     #// 2 + 3 + 2 + 1 == 8; 8 / 4 = 2
        self.assertEqual(qm.get_identifier_length().get_mean(), 2.);
        self.assertEqual(qm.get_unique_identifier_length().get_count(), 3);
     #// 2 + 3 + 1 == 6; 6 / 3 = 2
        self.assertEqual(qm.get_unique_identifier_length().get_mean(), 2.);
    

    def message(self,t = None, test = None):
        if t!=None:                    
            m = "Prefix \""+str( t.prefix)+ "\" Suffix: \"" +str( t.suffix)+"\" Hint: " + str(QualityMetrics.StyleHint[t.e.name])+" Expected: " + str(t.result)+ ' '
            return m
        elif test !=None:
            
            m = "Code \"" +str( test.code)+ "\" Hint: " +str( QualityMetrics.StyleHint[test.e.name]) +" Expected: " +str(test.result)+ ' '
            return m
        

    def testPrefixSuffix(self,strings, test):
        for o in strings:
            for t in test:             
                code = str(t.prefix)
                code+=o
                code+=str(t.suffix)
                tstring = StringIO(code)
                calc = CMetricsCalculator(tstring)
                calc.calculate_metrics();
                qm = calc.get_metrics()   ###For Replace H
                self.assertEqual(qm.get_style_hint(t.e.value), t.result, self.message(t))
                
            
    

    def testBinaryOperatorStyle(self):
        
        binary_operator = [
            "/", "%", "<<", ">>", "<", "<=", ">", ">=", "==", "!=",
            "^", "|", "&&", "||", "?", "=", "+=", "-=", "*=", "/=",
            "%=", "<<=", ">>=", "&=", "^=", "|=",            
        ]

        test = [
              CMetricsCalculatorTest.PSTest("a ", " b", QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP,0),
              CMetricsCalculatorTest.PSTest("a ", "b", QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP,1),
              CMetricsCalculatorTest.PSTest("a ", " b", QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP, 1),
              CMetricsCalculatorTest.PSTest("a ", "b", QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP, 0),
              CMetricsCalculatorTest.PSTest("a ", " b", QualityMetrics.StyleHint.NO_SPACE_BEFORE_BINARY_OP, 0),
              CMetricsCalculatorTest.PSTest("a", " b", QualityMetrics.StyleHint.NO_SPACE_BEFORE_BINARY_OP, 1 ),
              CMetricsCalculatorTest.PSTest("a ", " b", QualityMetrics.StyleHint.SPACE_BEFORE_BINARY_OP, 1 ),
              CMetricsCalculatorTest.PSTest("a", " b", QualityMetrics.StyleHint.SPACE_BEFORE_BINARY_OP, 0 ),
              CMetricsCalculatorTest.PSTest("a ", " b", QualityMetrics.StyleHint.SPACE_BEFORE_BINARY_OP, 1 ),
              CMetricsCalculatorTest.PSTest("a", " b", QualityMetrics.StyleHint.SPACE_BEFORE_BINARY_OP, 0 )          
        ]

        self.testPrefixSuffix(binary_operator, test)
    

    def testKeywordStyle(self):
        
        keyword = [
            "case", "do", "else", "for", "goto", "if", "switch",
            "while",
        
        ]

        test = [
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 0 ),
          CMetricsCalculatorTest.PSTest(";",  " (1)", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 1 ),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 0 ),
          CMetricsCalculatorTest.PSTest("; ", "(1)", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 1 ),
          CMetricsCalculatorTest.PSTest(" #include <", ">", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 0 ),
          CMetricsCalculatorTest.PSTest(" #define <", ">", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 0 ),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 1 ),
          CMetricsCalculatorTest.PSTest(";",  " (1)", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 0 ),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 1 ),
          CMetricsCalculatorTest.PSTest("; ", "(1)", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 0 ),
          CMetricsCalculatorTest.PSTest(" #include <", ">", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 0 ),
          CMetricsCalculatorTest.PSTest(" #define <", ">", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 0 ),
        
        ]

        self.testPrefixSuffix(keyword, test);
    

    def testDeclKeywordStyle(self):
        
        keyword = [
            "enum", "struct", "union",
        
        ]

        test = [
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest("foo(", " (1)", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(";",  " (1)", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 1),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest("; ", "(1)", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 1),
          CMetricsCalculatorTest.PSTest(" #include <", ">", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(" #define <", ">", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 1),
          CMetricsCalculatorTest.PSTest("foo(", " (1)", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(";",  " (1)", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 1),
          CMetricsCalculatorTest.PSTest("; ", "(1)", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(" #include <", ">", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(" #define <", ">", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 0),
          
        ]

        self.testPrefixSuffix(keyword, test);
    

    def testKeywordStyleLeft(self):
        
        keyword = [
         
            "break", "continue", "default", "return",
            
        ]

        test = [
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(";",  " (1)", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 1),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest("; ", "(1)", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(" #include <", ">", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(" #define <", ">", QualityMetrics.StyleHint.NO_SPACE_AFTER_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 1),
          CMetricsCalculatorTest.PSTest(";",  " (1)", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest("; ", " (1)", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest("; ", "(1)", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(" #include <", ">", QualityMetrics.StyleHint.SPACE_BEFORE_KEYWORD, 0),
          CMetricsCalculatorTest.PSTest(" #define <", ">", QualityMetrics.StyleHint.SPACE_AFTER_KEYWORD, 0),
          
        ]

        self.testPrefixSuffix(keyword, test);
    
    


    class Test:
        def __init__(self,code=None, e=None, result = None):
            self.code = code;
            self.e = e;
            self.result = result;
    


    def testStyle(self):
        
        test = [
                 CMetricsCalculatorTest.Test("a[4]", QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_SQUARE_BRACKET, 0 ),
                 CMetricsCalculatorTest.Test("a [4]", QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_SQUARE_BRACKET, 1 ),
                 CMetricsCalculatorTest.Test("a[4]", QualityMetrics.StyleHint.NO_SPACE_BEFORE_OPENING_SQUARE_BRACKET, 1 ),
                 CMetricsCalculatorTest.Test("a [4]", QualityMetrics.StyleHint.NO_SPACE_BEFORE_OPENING_SQUARE_BRACKET, 0 ),
                 CMetricsCalculatorTest.Test("a[4]", QualityMetrics.StyleHint.SPACE_AFTER_OPENING_SQUARE_BRACKET, 0 ),
                 CMetricsCalculatorTest.Test("a[ 4]", QualityMetrics.StyleHint.SPACE_AFTER_OPENING_SQUARE_BRACKET, 1 ),
                 CMetricsCalculatorTest.Test("a[4]", QualityMetrics.StyleHint.NO_SPACE_AFTER_OPENING_SQUARE_BRACKET, 1 ),
                 CMetricsCalculatorTest.Test("a[ 4]", QualityMetrics.StyleHint.NO_SPACE_AFTER_OPENING_SQUARE_BRACKET, 0 ),
                 CMetricsCalculatorTest.Test("~0xff", QualityMetrics.StyleHint.SPACE_AFTER_UNARY_OP, 0 ),
                 CMetricsCalculatorTest.Test("~ 0xff", QualityMetrics.StyleHint.SPACE_AFTER_UNARY_OP, 1 ),
                 CMetricsCalculatorTest.Test("~0xff", QualityMetrics.StyleHint.NO_SPACE_AFTER_UNARY_OP, 1 ),
                 CMetricsCalculatorTest.Test("~ 0xff", QualityMetrics.StyleHint.NO_SPACE_AFTER_UNARY_OP, 0 ),
                 CMetricsCalculatorTest.Test("a, b", QualityMetrics.StyleHint.SPACE_BEFORE_COMMA, 0 ),
                 CMetricsCalculatorTest.Test("a , b", QualityMetrics.StyleHint.SPACE_BEFORE_COMMA, 1 ),
                 CMetricsCalculatorTest.Test("a, b", QualityMetrics.StyleHint.NO_SPACE_BEFORE_COMMA, 1 ),
                 CMetricsCalculatorTest.Test("a , b", QualityMetrics.StyleHint.NO_SPACE_BEFORE_COMMA, 0 ),
                 CMetricsCalculatorTest.Test("a, b", QualityMetrics.StyleHint.NO_SPACE_AFTER_COMMA, 0 ),
                 CMetricsCalculatorTest.Test("a,b", QualityMetrics.StyleHint.NO_SPACE_AFTER_COMMA, 1 ),
                 CMetricsCalculatorTest.Test("a, b", QualityMetrics.StyleHint.SPACE_AFTER_COMMA, 1 ),
                 CMetricsCalculatorTest.Test("a,b", QualityMetrics.StyleHint.SPACE_AFTER_COMMA, 0 ),
                 CMetricsCalculatorTest.Test("foo(int a)", QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACKET, 0 ),
                 CMetricsCalculatorTest.Test("foo(int a )", QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACKET, 1 ),
                 CMetricsCalculatorTest.Test("foo(int a)", QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_BRACKET, 1 ),
                 CMetricsCalculatorTest.Test("foo(int a )", QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_BRACKET, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{x;\n}", QualityMetrics.StyleHint.NO_SPACE_BEFORE_OPENING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo[a]", QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_SQUARE_BRACKET, 0 ),
                 CMetricsCalculatorTest.Test("foo[a ]", QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_SQUARE_BRACKET, 1 ),
                 CMetricsCalculatorTest.Test("foo[a]", QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_SQUARE_BRACKET, 1 ),
                 CMetricsCalculatorTest.Test("foo[a ]", QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_SQUARE_BRACKET, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{x;\n}", QualityMetrics.StyleHint.NO_SPACE_BEFORE_OPENING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{x;\n}", QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nif (1){x;}}\n", QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nif (1) {x;}}\n", QualityMetrics.StyleHint.SPACE_BEFORE_OPENING_BRACE, 1 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nx;\n}", QualityMetrics.StyleHint.NO_SPACE_AFTER_OPENING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nif (1){x;}}\n", QualityMetrics.StyleHint.NO_SPACE_AFTER_OPENING_BRACE, 1 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nx;\n}", QualityMetrics.StyleHint.SPACE_AFTER_OPENING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nif (1){ x;}}\n", QualityMetrics.StyleHint.SPACE_AFTER_OPENING_BRACE, 1 ),
                 CMetricsCalculatorTest.Test("foo()\n{x;\n}", QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{x;\n}", QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nx;}\n", QualityMetrics.StyleHint.NO_SPACE_BEFORE_CLOSING_BRACE, 1 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nx;}\n", QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nx; }\n", QualityMetrics.StyleHint.SPACE_BEFORE_CLOSING_BRACE, 1 ),
                 CMetricsCalculatorTest.Test("foo()\n{x;\n}\n", QualityMetrics.StyleHint.NO_SPACE_AFTER_CLOSING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{x;\n}\n", QualityMetrics.StyleHint.SPACE_AFTER_CLOSING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{x;\n}\n", QualityMetrics.StyleHint.SPACE_AFTER_CLOSING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nif(1){foo;}}\n", QualityMetrics.StyleHint.NO_SPACE_AFTER_CLOSING_BRACE, 1 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nif(1){foo;}}\n", QualityMetrics.StyleHint.SPACE_AFTER_CLOSING_BRACE, 0 ),
                 CMetricsCalculatorTest.Test("foo()\n{\nif(1){foo;} }\n", QualityMetrics.StyleHint.SPACE_AFTER_CLOSING_BRACE, 1 ),
                 CMetricsCalculatorTest.Test("int a;", QualityMetrics.StyleHint.SPACE_BEFORE_SEMICOLON, 0 ),
                 CMetricsCalculatorTest.Test("int a ;", QualityMetrics.StyleHint.SPACE_BEFORE_SEMICOLON, 1 ),
                 CMetricsCalculatorTest.Test(" \t;", QualityMetrics.StyleHint.SPACE_BEFORE_SEMICOLON, 0 ),
                 CMetricsCalculatorTest.Test("int a;", QualityMetrics.StyleHint.NO_SPACE_BEFORE_SEMICOLON, 1 ),
                 CMetricsCalculatorTest.Test("int a ;", QualityMetrics.StyleHint.NO_SPACE_BEFORE_SEMICOLON, 0 ),
                 CMetricsCalculatorTest.Test(" \t;", QualityMetrics.StyleHint.NO_SPACE_BEFORE_SEMICOLON, 0 ),
                 CMetricsCalculatorTest.Test("int a; int b;\n", QualityMetrics.StyleHint.NO_SPACE_AFTER_SEMICOLON, 0 ),
                 CMetricsCalculatorTest.Test("int a;int b;\n", QualityMetrics.StyleHint.NO_SPACE_AFTER_SEMICOLON, 1 ),
                 CMetricsCalculatorTest.Test("int a; int b;\n", QualityMetrics.StyleHint.SPACE_AFTER_SEMICOLON, 1 ),
                 CMetricsCalculatorTest.Test("int a;int b;\n", QualityMetrics.StyleHint.SPACE_AFTER_SEMICOLON, 0 ),
                 CMetricsCalculatorTest.Test("a->b", QualityMetrics.StyleHint.SPACE_BEFORE_STRUCT_OP, 0 ),
                 CMetricsCalculatorTest.Test("a ->b", QualityMetrics.StyleHint.SPACE_BEFORE_STRUCT_OP, 1 ),
                 CMetricsCalculatorTest.Test("a->b", QualityMetrics.StyleHint.NO_SPACE_BEFORE_STRUCT_OP, 1 ),
                 CMetricsCalculatorTest.Test("a ->b", QualityMetrics.StyleHint.NO_SPACE_BEFORE_STRUCT_OP, 0 ),
                 CMetricsCalculatorTest.Test("a->b", QualityMetrics.StyleHint.SPACE_AFTER_STRUCT_OP, 0 ),
                 CMetricsCalculatorTest.Test("a->b", QualityMetrics.StyleHint.NO_SPACE_AFTER_STRUCT_OP, 1 ),
                 CMetricsCalculatorTest.Test("a-> b", QualityMetrics.StyleHint.SPACE_AFTER_STRUCT_OP, 1 ),
                 CMetricsCalculatorTest.Test("a-> b", QualityMetrics.StyleHint.NO_SPACE_AFTER_STRUCT_OP, 0 ),
                 CMetricsCalculatorTest.Test("a.b", QualityMetrics.StyleHint.SPACE_BEFORE_STRUCT_OP, 0 ),
                 CMetricsCalculatorTest.Test("a .b", QualityMetrics.StyleHint.SPACE_BEFORE_STRUCT_OP, 1 ),
                 CMetricsCalculatorTest.Test("a.b", QualityMetrics.StyleHint.NO_SPACE_BEFORE_STRUCT_OP, 1 ),
                 CMetricsCalculatorTest.Test("a .b", QualityMetrics.StyleHint.NO_SPACE_BEFORE_STRUCT_OP, 0 ),
                 CMetricsCalculatorTest.Test("a.b", QualityMetrics.StyleHint.SPACE_AFTER_STRUCT_OP, 0 ),
                 CMetricsCalculatorTest.Test("a.b", QualityMetrics.StyleHint.NO_SPACE_AFTER_STRUCT_OP, 1 ),
                 CMetricsCalculatorTest.Test("a. b", QualityMetrics.StyleHint.SPACE_AFTER_STRUCT_OP, 1 ),
                 CMetricsCalculatorTest.Test("a. b", QualityMetrics.StyleHint.NO_SPACE_AFTER_STRUCT_OP, 0 ),
                 CMetricsCalculatorTest.Test("a ? b : c", QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP, 0 ),
                 CMetricsCalculatorTest.Test("a ? b :c", QualityMetrics.StyleHint.NO_SPACE_AFTER_BINARY_OP, 1 ),
                 CMetricsCalculatorTest.Test("a ? b : c", QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP, 2 ),
                 CMetricsCalculatorTest.Test("a ?b :c", QualityMetrics.StyleHint.SPACE_AFTER_BINARY_OP, 0 ),
                 CMetricsCalculatorTest.Test("case 42:\n", QualityMetrics.StyleHint.NO_SPACE_BEFORE_BINARY_OP, 0 ),
                 CMetricsCalculatorTest.Test("case 42 :\n", QualityMetrics.StyleHint.SPACE_BEFORE_BINARY_OP, 0 ),
                 CMetricsCalculatorTest.Test("!a", QualityMetrics.StyleHint.SPACE_AFTER_UNARY_OP, 0 ),
                 CMetricsCalculatorTest.Test("! a", QualityMetrics.StyleHint.SPACE_AFTER_UNARY_OP, 1 ),
                 CMetricsCalculatorTest.Test("!a", QualityMetrics.StyleHint.NO_SPACE_AFTER_UNARY_OP, 1 ),
                 CMetricsCalculatorTest.Test("! a", QualityMetrics.StyleHint.NO_SPACE_AFTER_UNARY_OP, 0 ),
                 CMetricsCalculatorTest.Test("\nreturn;", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 0 ),
                 CMetricsCalculatorTest.Test(";return;", QualityMetrics.StyleHint.NO_SPACE_BEFORE_KEYWORD, 1 ),
                 CMetricsCalculatorTest.Test(";return;", QualityMetrics.StyleHint.SPACE_AT_END_OF_LINE, 0 ),
                 CMetricsCalculatorTest.Test(";return; \n", QualityMetrics.StyleHint.SPACE_AT_END_OF_LINE, 1 ),
                
        ]

        for t in test:
            tstring = StringIO(t.code)
            calc = CMetricsCalculator(tstring)
            calc.calculate_metrics();
            qm = calc.get_metrics()   ###For Replace H
            self.assertEqual(qm.get_style_hint(t.e.value), t.result, self.message(test=t))
        
    

    def testIndentationSimple(self):
        tstring = StringIO("foo()\n{\n\treturn;\n}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 1);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

    def testIndentationIf(self):
        tstring = StringIO("foo()\n{\n\tif (a)\n\t\treturn;\n}");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 2);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

    def testIndentationBrace(self):
        tstring = StringIO("foo()\n{\n\tif (a) { \n\t\treturn;\n\t}\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 3);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

    def testIndentationGnuBrace(self):
        tstring = StringIO("foo()\n{\n  if (a)\n    {\n      return;\n    }\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 4);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 2.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

 #// Written to find implementation error
    def testIfFor(self):
        tstring = StringIO("foo()\n{\n\tif (a)\n\t\tfor (;;)\n\t\t\tbar();\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 3);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

 #// Written to investigate implementation error
    def testLineComment(self):
        tstring = StringIO("foo()\n{\n\tif (x) {\n\t\t// foo\n\t\tbar();\n\t}\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 4);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

 #// Written to investigate implementation error
    def testCppLine(self):
        tstring = StringIO("foo()\n{\n\tif (x) {\n\t\t#define x 1\n\t\tbar();\n\t}\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 3);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

 #// Written to investigate implementation error
    def testCppCommentLine(self):
        tstring = StringIO("foo()\n{\n\tif (x) {\n\t\t#define x 1\n\t\t// Comment\n\t\tbar();\n\t}\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 4);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);    

 #// Written to investigate implementation error
    def testElseCppCommentLine(self):
        tstring = StringIO("foo()\n{\n\tif (x) {\n\t\tfoo();\n\t} else {\n#define x 1\n\t\t// Comment\n\t\tbar();\n\t}\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 6);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

    def testBlockCommentIndent(self):
        tstring = StringIO("foo()\n{\n\tif (x)\n\t\t/*\n\t\t * comment\n\t\t */\n\t\tfoo();\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 2);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

 #// Added after problem that set indentation level to -1
    def testIfElseCppComment(self):
        tstring = StringIO("foo()\n{\n\tif (x) {\n#if x\n\t\t\n\t\tfoo();\n#else\n\t\tbar();\n#endif\n\t}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 5);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

 #// Added after problem that set indentation level to -1
    def testBracedAssignment(self):
        tstring = StringIO("foo()\n{\n\tx[] = {3};\n\tfoo();\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 2);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

 #// Added after problem that set indentation level to -1
    def testElseComment(self):
        tstring = StringIO("foo()\n{\n\tif(x)\n\t\tfor (;;) foo();\n\telse\n\t\tbar();\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 4);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
   

 #// Added after problem that set indentation level to -1
    def testElseNoIf(self):
        tstring = StringIO("foo()\n{\n\tIF(x)\n\t\tfoo();\n\telse\n\t\tbar();\n}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        self.assertEqual(qm.get_indentation_spacing().get_count(), 3);
        self.assertEqual(qm.get_indentation_spacing().get_mean(), 8.);
        self.assertEqual(qm.get_indentation_spacing().get_standard_deviation(), 0.);
    

    def testInconsistency(self):
        tstring = StringIO("foo()\n{\n"+
                "foo(a,b);\n"+
                "foo(a,b) ;\n"+
                "foo(a, b);;;;\n"+
            "}\n");
        calc = CMetricsCalculator(tstring)
        calc.calculate_metrics();
        qm = calc.get_metrics()   ###For Replace H
        #/*
        # * (NO)SPACE_AFTER_COMMA 3 (1 inconistent)
        # * (NO)SPACE_BEFORE_CLOSING_BRACKET 4
        # * (NO)SPACE_BEFORE_COMMA 3
        # * (NO)SPACE_BEFORE_SEMICOLON 6 (1 inconsistent)
        # * Total=16
        # */
        self.assertEqual(qm.get_style_inconsistency(), 2 / 21.);

    def setUp(self):
        print ("In method", self._testMethodName)
#endif /*  CMETRICSCALCULATORTEST_H */


if __name__ == '__main__':
    unittest.main()
