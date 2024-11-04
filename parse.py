import sys
from lex import *
from emit import *
from environment import *
from scheme_list import *
from function import *
#Begin writing the runtime.Specifically, write the part that the asm will call for say (define x 5). Remember that I am using a tagging system for types.. then use the runtime to in global_definitions

#Todo0: work on defining functions(define <call pattern> <body>). work on self.body(). First support functions that accept and return values that are going to be on the stack(int,float,char,boolean)
#Todo1: implement the beginnings of the built in library(native functions). start with +,-,*,/,cons,append, and printing(with c libs for asm) later along the line implement more list/vector procedures and equivalence tests. All these builtin functions will be made in c and will be part of the target program's runtime environment. The asm will call to these functions.
#Todo2: Add string,symbol,list,vector and function to be allocated on the heap. Once this is working, implement gc to be able to manage memory on the heap.

#Note: define currently doesnt handle setting vars to functions. Deal with this after vector 
# Also, when implementing local vars, maybe the environment class should have an offset from the stack field. work on emitting definition rule and scoping. 
#Todo2: first implement parser, make sure you add the extra grammar(cons,car,cdr etc) to the grammar doc and to the parser.

#somewhere down the line implement special functions in vector/list, such as vector-ref for example
# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer,emitter):
        self.lexer = lexer
        self.emitter = emitter
        #store last result of an expression as an identifier class.For pairs ans lists will store pair as value field. if previous exp doesnt return anything set to None
        self.last_exp_res = None
        self.cur_token = None
        self.peek_token = None
        self.global_environment = Environment()
        self.cur_environment = self.global_environment
        self.parens = []
        self.next_token()
        self.next_token()

    # Return true if the current token matches.
    def check_token(self, type):
        return type == self.cur_token.type
    
    def set_last_exp_res(self,typeof,val):
        self.last_exp_res = Identifier(typeof,val)
    

    def is_token_any(self,type,type_arr):
        return type in type_arr
    

    # Return true if the next token matches.
    def check_peek(self, type):
        return type == self.peek_token.type

    # Try to match current token. If not, error. Advances the current token.
    def match(self, type):
        if not self.check_token(type):
            self.abort("Expected " + type.name + ", got " + self.cur_token.type.name)
        self.next_token()
        

    # Advances the current token.
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message):
        sys.exit("Error. " + message)
    
    
    def evaluate_constant(self):
        match self.cur_token.type:
            case TokenType.NUMBER:
                if isinstance(self.cur_token.text,int):
                    self.set_last_exp_res(IdentifierType.INT,str(self.cur_token.text))
                else: 
                    self.set_last_exp_res(IdentifierType.FLOAT,str(self.cur_token.text))
            case TokenType.BOOLEAN:
                self.set_last_exp_res(IdentifierType.BOOLEAN,self.cur_token.text)
            case TokenType.CHAR:
                self.set_last_exp_res(IdentifierType.BOOLEAN,self.cur_token.text)
            case TokenType.STRING:
                self.set_last_exp_res(IdentifierType.STR,self.cur_token.text)
            case _:
                self.abort("Calling evaluate_constant(). current token is not a constant") 
                                
    def evaluate_symbol(self):
        self.set_last_exp_res(IdentifierType.SYMBOL,self.cur_token.text)
        
    def evaluate_pair(self,pair_obj):
        self.set_last_exp_res(IdentifierType.PAIR,pair_obj)
    
    def evaluate_function(self,function_obj):
        self.set_last_exp_res(IdentifierType.FUNCTION,function_obj)
    
    #Python lists will be used to represent  
    def evaluate_vector(self,vector_obj):
        self.set_last_exp_res(IdentifierType.VECTOR,vector_obj)
        
    def program(self):
        print("Program")
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
        #Parse all expressions in the program
        while not self.check_token(TokenType.EOF):
            self.expression()
        self.emitter.emit_global_definitions(self.global_environment.symbol_table)
        self.emitter.emit_start_section("\tmov rax, 60\n\tmov rdi, 0\n\tsyscall")
            
    def expression(self): 
        if self.check_token(TokenType.NEWLINE):
            self.next_token()
        #<constant> ::= <boolean> | <number> | <character> | <string>
        elif self.check_token(TokenType.NUMBER):
            print("EXPRESSION-NUMBER")
            if isinstance(self.cur_token.text,int):
                self.set_last_exp_res(IdentifierType.INT,str(self.cur_token.text))
            else:
                self.set_last_exp_res(IdentifierType.FLOAT,str(self.cur_token.text))
            self.next_token()
        
        elif self.check_token(TokenType.CHAR):
            print("EXPRESSION-CHAR")
            self.set_last_exp_res(IdentifierType.CHAR,self.cur_token.text)
            self.next_token()
            
        elif self.check_token(TokenType.BOOLEAN):
            print("EXPRESSION-BOOLEAN")
            self.set_last_exp_res(IdentifierType.BOOLEAN,self.cur_token.text)
            self.next_token()

        elif self.check_token(TokenType.STRING):
            print("EXPRESSION-STRING")
            self.set_last_exp_res(IdentifierType.STR,self.cur_token.text)
            self.next_token()
        
        elif self.check_token(TokenType.IDENTIFIER):
            if not self.cur_token.text in self.cur_environment.symbol_table:
                self.abort("Identifier "+ self.cur_token.text + " not defined.")
            print("EXPRESSION-VARIABLE")
            cur_ident = self.cur_environment.find_definition(self.cur_token.text)
            self.set_last_exp_res(cur_ident.typeof,cur_ident.value)        
            self.next_token()
                    
        elif self.check_token(TokenType.QUOTE_SYMBOL):
            print("EXPRESSION-QUOTE-SYMBOL")
            self.next_token()
            self.datum()

        elif self.check_token(TokenType.EXPR_START):
            self.parens.append(self.cur_token.text)
            self.next_token()
            if self.check_token(TokenType.IF):
                self.next_token()
                self.if_exp()

            elif self.check_token(TokenType.QUOTE):
                self.next_token()
                self.quote_exp()
            
            elif self.check_token(TokenType.LAMBDA):
                self.next_token()
                self.lambda_exp()
            
            elif self.check_token(TokenType.DEFINE):
                self.next_token()
                self.definition_exp()
                
            elif self.check_token(TokenType.AND):
                self.next_token()
                self.and_exp()
                
            elif self.check_token(TokenType.OR):
                self.next_token()
                self.or_exp()
            
            elif self.check_token(TokenType.COND):
                self.next_token()
                self.cond_exp()
            
            elif self.check_token(TokenType.CASE):
                self.next_token()
                self.case_exp()
                
            elif self.check_token(TokenType.LET):
                self.next_token()
                self.let_exp()
            
            elif self.check_token(TokenType.LETSTAR):
                self.next_token()
                self.let_star_exp()
            
            elif self.check_token(TokenType.LETREC):
                self.next_token()
                self.letrec_exp()
                
            elif self.check_token(TokenType.SETEXCLAM):
                self.next_token()
                self.setexclam_exp()
            
            elif self.check_token(TokenType.REC):
                self.next_token()
                self.rec_exp()
                
            #(begin <expression>)
            elif self.check_token(TokenType.BEGIN):
                self.next_token()
                print("EXPRESSION-BEGIN")
                self.expression()
                self.match(TokenType.EXPR_END)
                self.parens.pop()
                
            # (delay <expression>)
            elif self.check_token(TokenType.DELAY):
                self.next_token()
                print("EXPRESSION-DELAY")
                self.expression()
                self.match(TokenType.EXPR_END)
                self.parens.pop()
            
            elif self.check_token(TokenType.DO):
                self.next_token()
                self.do_exp()
                
            elif self.check_token(TokenType.QUASIQUOTE):
                self.next_token()
                self.quasiquote_exp()
            #<procedure call> ::= (<operator> <operand>*)
            #in the emitter, the first expression must evaluate to a valid operator
            else:
                # self.abort("Token " + str(self.cur_token.text) + " is not an operator")
                print("EXPRESSION-PROCEDURECALL")
                print("OPERATOR")
                self.expression()
                while not self.check_token(TokenType.EXPR_END):
                    print("OPERAND")
                    self.expression()
                self.parens.pop()
                self.next_token()
                
                 
        else:
            self.abort("Token " + self.cur_token.text + " is not a valid expression")
      
    #returns a string which contains the next expression. used to extract body of a function. self.cur_token will be set to next char after exp
    #This method does not check if the expression has correct syntax(racket doesnt either), the error will occur will the function gets called
    def extract_exp(self) -> str:
        open_paren_count = 0
        exp = []
        if self.check_token(TokenType.EXPR_START):
            if self.check_peek(TokenType.EXPR_END):
                self.abort("Empty expression in body.")
            open_paren_count += 1
            exp.append(str(self.cur_token.text))
            self.next_token()
            while open_paren_count != 0:
                exp.append(str(self.cur_token.text))
                if self.check_token(TokenType.EXPR_START):
                    open_paren_count += 1
                elif self.check_token(TokenType.EXPR_END):
                    open_paren_count -= 1
                elif self.check_token(TokenType.EOF):
                    self.abort("Incorrect syntax in body. Parentheses not well formed.")
                self.next_token()
        elif self.check_token(TokenType.EXPR_END):
            self.abort("No expression in body")
        else:
            exp.append(str(self.cur_token.text))
            self.next_token()
        return ' '.join(exp)
      
    #(if <test> <consequent> <alternate>) | (if <test> <consequent>), where test,consequent and alternate are expressions
    def if_exp(self):
        print("EXPRESSION-IF")
        num_args = 0
        while not self.check_token(TokenType.EXPR_END):
            if self.check_token(TokenType.EOF):
                self.abort("Parentheses are not well formed.")
            num_args += 1
            if num_args > 3:
                self.abort("Too many arguments in if condition.")
            self.expression()
            
        if num_args < 2 :
            self.abort("Too few arguments in if condition.")
        
        if len(self.parens) == 0:
            self.abort("Parentheses are not well formed.")
                
        self.parens.pop()
        self.next_token()
        
    #(quote <datum>)
    def quote_exp(self):
        print("EXPRESSION-QUOTE")
        self.datum()        
        if not self.check_token(TokenType.EXPR_END):
            self.abort("Incorrect syntax in quote expression. ")
        if len(self.parens) == 0:
            self.abort("Parentheses in quote expression not well formed.")
        self.parens.pop()
        self.next_token()
        
    #(lambda <bound var list> <body>)
    def lambda_exp(self):
        print("EXPRESSION-LAMBDA")
        self.bound_var_list()
        self.body()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
    
    def and_exp(self):
        print("EXPRESION-AND")
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
        
    def or_exp(self):
        print("EXPRESION-OR")
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
        
    # (cond <cond clause>*) | (cond <cond clause>* (else <sequence>))
    def cond_exp(self):
        print("EXPRESSION-COND")
        #first, handle case where there are 0 cond clauses and no else. basically exp is: (cond)
        if self.check_token(TokenType.EXPR_END):
            self.parens.pop()
            self.next_token()

        # no cond clause but an else clause, so (cond (else <sequence>))
        elif self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
            self.else_rule()
            self.match(TokenType.EXPR_END)
            self.parens.pop()
            
        # one or more cond clauses and an optional else at the end
        else:
            if not self.check_token(TokenType.EXPR_START):
                self.abort("Incorrect syntax in cond expression. Expected (, got " + str(self.cur_token.text))

            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
                    self.else_rule()
                    break
                self.cond_clause()
                
            self.match(TokenType.EXPR_END)
            self.parens.pop()
            
    #(case <expression> <case clause>*) | (case <expression> <case clause>* (else <sequence>))  #<case clause> ::= ((<datum>*) <sequence>)       
    def case_exp(self):
        print("EXPRESSION-CASE")
        self.expression()
        
        if self.check_token(TokenType.EXPR_END):
            self.parens.pop()
            self.next_token()
            
        elif self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
            self.else_rule()
            self.match(TokenType.EXPR_END)
            self.parens.pop()
        
        # one or more case clauses and an optional else at the end
        else:
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
                    self.else_rule()
                    break
                self.case_clause()
            self.match(TokenType.EXPR_END)
            self.parens.pop()
    
    # (let (<binding spec>*) <body>) | (let <variable> (<binding spec>*) <body>) 
    def let_exp(self):
        print("EXPRESSION-LET")
        if self.check_token(TokenType.IDENTIFIER):
            print("VARIABLE")
            self.next_token()
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.binding_spec()
        self.next_token()
        self.body()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
    
    # (let* (<binding spec>*) <body>)
    def let_star_exp(self):
        print("EXPRESSION-LET*")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.binding_spec()
        self.next_token()
        self.body()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
        
    # (letrec (<binding spec>*) <body>)
    def letrec_exp(self):
        print("EXPRESSION-LETREC")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.binding_spec()
        self.next_token()
        self.body()
        self.match(TokenType.EXPR_END)
        self.parens.pop()

    # (set! <variable> <expression>)
    def setexclam_exp(self):
        print("EXPRESSION-SET!")
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
        
    #(rec <variable> <expression>)
    def rec_exp(self):
        print("EXPRESSION-REC")
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
        
    # (do (<iteration spec>*) (<end test> <sequence>+) <expression>*)
    def do_exp(self):
        print("EXPRESSION-DO")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.iteration_spec()
        self.next_token()
        self.end_test()
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.parens.pop()
        self.next_token()

    # (quasiquote <datum>) , but datum is handled differently here. It must accept unquote and unquote-splicing keywords
    #remember for the emitter that for unquote, expr must evaluate to a constant, and for unquote-splicing, expr must eval to a list/vector
    def quasiquote_exp(self):
        print("EXPRESSION-QUASIQUOTE")
        self.quasiquote_datum()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
        
    # <iteration spec> ::= (<variable> <init> <step>), init and step are expressions
    def iteration_spec(self):
        print("ITERATION-SPEC")
        self.match(TokenType.EXPR_START)
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.expression()
        self.match(TokenType.EXPR_END)

    # (<end test> <sequence>+) , <end test> is an expression
    def end_test(self):
        print("END-TEST")
        self.match(TokenType.EXPR_START)
        self.expression()
        self.expression()
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.next_token()
        
        
    #<binding spec> ::= (<variable> <expression>)  
    def binding_spec(self):
        print("BINDING-SPEC")
        self.match(TokenType.EXPR_START)
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.match(TokenType.EXPR_END)
 
    # <cond clause> ::= (<test> <sequence>), sequence will be implemented as just one expression, not 1 or more. although in r5rs one or more exp is valid scheme, it always takes the right most expression and ignores the rest, which is confusing
    def cond_clause(self):
        print("COND-CLAUSE")
        self.match(TokenType.EXPR_START)
        self.parens.append("(")
        self.expression()
        self.expression()
        self.match(TokenType.EXPR_END)
        self.parens.pop()
        
    #<case clause> ::= ((<datum>*) <sequence>)
    def case_clause(self):
        print("CASE-CLAUSE")
        self.match(TokenType.EXPR_START)
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.datum()
        self.match(TokenType.EXPR_END)
        self.expression()
        self.match(TokenType.EXPR_END)
   
    # (else <sequence>)     
    def else_rule(self):
        #no need to add and remove parens from stack since this else rule is self contained and checks for start and end parens.
        print("ELSE")
        self.match(TokenType.EXPR_START)
        self.match(TokenType.ELSE)
        self.expression()
        self.match(TokenType.EXPR_END)
        
    #<bound var list> ::= <variable> | (<variable>*) | (<variable>+ . <variable>)
    def bound_var_list(self):
        print("BOUND-VAR-LIST")
        if self.check_token(TokenType.IDENTIFIER):
            print("VARIABLE")
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            self.parens.append(self.cur_token.text)
            token_count = 0
            self.next_token()
            
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.DOT):
                    print("DOT")
                    if token_count < 1:
                        self.abort("Incorrect syntax in creating a pair of variables. Requires one or more variables before the " + self.cur_token.text + " token.")
                    self.next_token()
                    self.match(TokenType.IDENTIFIER)
                    print("VARIABLE")
                    if not self.check_token(TokenType.EXPR_END):
                        self.abort("Incorrect syntax after the" + self.cur_token.text + " token in bound var list.")
                    break
                elif self.check_token(TokenType.IDENTIFIER):
                    print("VARIABLE")
                    self.next_token()
                    token_count += 1
                else:
                    self.abort("Incorrect syntax in varlist of lambda expression.")
            #no nesting in this grammar rule so no need to check stack 
            self.parens.pop()
            self.next_token()
            
        else:
            self.abort("Incorrect syntax in lambda expression, " + self.cur_token.text + " not a valid variable list.")
      
    # <definition> ::= (define <variable> <expression>) | (define <call pattern> <body>)
    # the define with the call pattern syntax essentially defines a function. The first arg in call pattern is function name and rest are the names of its args
    #returns name of definition
    def definition_exp(self) -> str:
        print("EXPRESSION-DEFINE")
        ident_name = None
        num_parens = len(self.parens) - 1
        if self.check_token(TokenType.IDENTIFIER):
            print("VARIABLE")
            ident_name = self.cur_token.text
            self.next_token()
            self.expression()
            self.cur_environment.add_definition(ident_name,Identifier(self.last_exp_res.typeof,self.last_exp_res.value))

        elif self.check_token(TokenType.EXPR_START):
            function = Function()
            self.call_pattern(function)
            self.body(function)
            self.evaluate_function(function)
            ident_name = function.get_name()
            self.cur_environment.add_definition(ident_name,Identifier(self.last_exp_res.typeof,self.last_exp_res.value))
        else:
            self.abort("Incorrect syntax in definition expression")
            
        self.match(TokenType.EXPR_END)
        if len(self.parens) != 1 + num_parens:
            self.abort("Parentheses are not well formed.")
        self.parens.pop()
        return ident_name
         
    # <call pattern> ::= (<pattern> <variable>*) | (<pattern> <variable>* . <variable>), where pattern ::= variable | <call pattern>
    def call_pattern(self,function):
        print("CALL_PATTERN")
        num_parens = len(self.parens)
        self.parens.append(self.cur_token.text)
        self.next_token()
        if self.check_token(TokenType.IDENTIFIER):
            print("PATTERN")
            function.set_name(self.cur_token.text)
            self.next_token()
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.DOT):
                    print("DOT")
                    self.next_token()
                    self.match(TokenType.IDENTIFIER)
                    if not self.check_token(TokenType.EXPR_END):
                        self.abort("Parentheses in call pattern not well formed.") 
                    break
                elif self.check_token(TokenType.IDENTIFIER):
                    print("VARIABLE")
                    function.add_param(self.cur_token.text)
                    self.next_token()
                else:
                    self.abort(self.cur_token.text + " is not an identifier.")
            if len(self.parens) != 1 + num_parens:
                self.abort("Parentheses in call pattern are not well formed.")
            self.parens.pop()
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            self.call_pattern() 
        else:
            self.abort("Incorrect syntax for call pattern.")
        
    # the definition are the local variables declared (within the function) which will be usable in the sequence.
    # <body> ::= <definition>* <sequence>   
    def body(self,function):
        print("BODY")
        #Process all definitions first. then process sequence with self.expression()
        while self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.DEFINE):  
            self.parens.append(self.cur_token.text)
            self.next_token()
            self.next_token()
            definition_name = self.definition_exp()
            function.add_local_definition(definition_name,Identifier(self.last_exp_res.typeof,self.last_exp_res.value))
        #extract function body
        function.add_to_body(self.extract_exp())
        # self.expression()
            
    def is_constant(self):
        return self.is_token_any(self.cur_token.type,[TokenType.BOOLEAN,TokenType.NUMBER,TokenType.CHAR,TokenType.STRING])
        
    # starts from parens
    # <list> ::= ( <datum>* ) | ( <datum>+ . <datum> )
    def list(self,is_quasi = False):
        #since this is not an expression, a list could potentially be deep within an exp, therefore store current amount of parens before processing the list
        print("LIST")
        num_parens = len(self.parens)
        self.parens.append(self.cur_token.text)
        token_count = 0
        self.next_token()
        first = Pair()
        cur_node = first
        while not self.check_token(TokenType.EXPR_END):
            if self.check_token(TokenType.DOT):
                print("DOT")
                if token_count < 1:
                    self.abort(" Creating a pair requires one or more datums before the " + self.cur_token.text + " token.")
                self.next_token()
                self.datum() if not is_quasi else self.quasiquote_datum()
                
                if not self.check_token(TokenType.EXPR_END):
                    self.abort("Incorrect syntax for making pairs.")
                cur_node.set_cdr(self.last_exp_res)
                break    
            else:
                self.datum() if not is_quasi else self.quasiquote_datum()                
                cur_node.set_car(self.last_exp_res)
                if not self.check_token(TokenType.DOT):
                    cur_node.set_cdr(Identifier(IdentifierType.PAIR,Pair()) if not self.check_token(TokenType.EXPR_END) else None)
                    cur_node = cur_node.get_cdr_value()
                token_count += 1
                
        if len(self.parens) != 1 + num_parens:
            self.abort("Parentheses in list are not well formed.")
        self.parens.pop()
        self.evaluate_pair(first)
        # print("PRINTING LIST:")
        # first.print()
        self.next_token()
    
    # <vector> ::= #( <datum>* ), starts from (
    def vector(self,is_quasi = False):
        if not self.check_token(TokenType.EXPR_START):
            self.abort("Incorrect syntax for vector.")
        print("VECTOR")
        num_parens = len(self.parens)
        self.parens.append(self.cur_token.text)
        self.next_token()
        vector = []
        while not self.check_token(TokenType.EXPR_END):
            if self.check_token(TokenType.EXPR_START) and (self.check_peek(TokenType.UNQUOTE) or self.check_peek(TokenType.UNQUOTESPLICING)):
                if not is_quasi:
                    self.abort("UNQUOTE and UNQUOTE-SPLICING only valid in quasiquote expression.")
                self.next_token()
                self.next_token()
                self.expression()
                self.match(TokenType.EXPR_END)
            else:
                self.datum() if not is_quasi else self.quasiquote_datum()
                vector.append(self.last_exp_res)
        
        if len(self.parens) != 1 + num_parens:
            self.abort("Parentheses in list are not well formed.")
        self.parens.pop()
        self.evaluate_vector(vector)
        # print("PRINTING VECTOR:")
        # [print(ident.typeof,ident.value) for ident in vector]
        self.next_token()
    #<datum> ::= <constant> | <symbol> | <list> | <vector>
    def datum(self):
        print("DATUM")
        if self.is_constant():
            print("CONSTANT")
            self.evaluate_constant()
            self.next_token()
        elif self.check_token(TokenType.IDENTIFIER):
            print("SYMBOL")
            self.evaluate_symbol()
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            self.list()  
        elif self.check_token(TokenType.HASH):
            self.next_token()
            self.vector()
        else:
            self.abort(self.cur_token.text + " Is not a valid datum.")
    
    # (quasiquote <datum>) , but datum is handled differently here. It must accept unquote and unquote-splicing keywords
    # (unquote expr) , (unquote-splicing expr)
    def quasiquote_datum(self):
        print("QUASIDATUM")
        if self.is_constant():
            print("CONSTANT")
            self.next_token()   
        elif self.check_token(TokenType.IDENTIFIER):
            print("SYMBOL")
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            if self.check_peek(TokenType.UNQUOTE) or self.check_peek(TokenType.UNQUOTESPLICING):
                self.next_token()
                self.next_token()
                self.expression()
                self.match(TokenType.EXPR_END)
            else:
                self.list(True)       
        elif self.check_token(TokenType.HASH):
            self.next_token()
            self.vector(True)     
        else:
            self.abort(self.cur_token.text + " Is not a valid datum.")
        