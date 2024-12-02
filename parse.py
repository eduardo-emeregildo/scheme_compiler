import sys
from lex import *
from emit import *
from environment import *
from function import *
from scheme_builtins import *
#Things I have to do complete implementation of function calling:
# 1. Now that builtin.h has the value objects, make the lexer 
# recognize builtins separately, handle all of these collectively in the parser

#After this, look at comments in scheme_builtins to see what I have to do next
#for builtin functions. finish implementing calling builtin functions.
#After builtins can be called, make sure stuff like: 
# (define new-display display)
# (new-display 1) work.

#3. have to implement function_call for variadic functions. implementing +,- etc
# in the built in library will require this since these are variadic functons

#4. right now function_call doesnt have the prettiest code. especially with
#all the is_global checks. definitely refactor

#Todo1: implement calling a normal function and a variadic function
#Todo2: begin writing some library functions in the runtime. start with 
#equality tests, +,-,*,/,cons,append, and printing

# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer,emitter):
        self.lexer = lexer
        self.emitter = emitter
        #store last result of an expression as an identifier class.
        #For pairs ans vecs will store an array of identifier objs.
        #how to denote empty list?
        self.last_exp_res = None
        self.cur_token = None
        self.peek_token = None
        self.global_environment = Environment()
        self.cur_environment = self.global_environment
        self.next_token()
        self.next_token()

    # Return true if the current token matches.
    def check_token(self, type):
        return type == self.cur_token.type
    
    def set_last_exp_res(self,typeof,val):
        self.last_exp_res = Identifier(typeof,val)
    
    def get_last_exp_type(self):
        if self.last_exp_res is None:
            self.abort("Cant get type, last expression evaluated to None.")
        return self.last_exp_res.typeof
        
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
                self.set_last_exp_res(IdentifierType.CHAR,self.cur_token.text)
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
    
    #sets last_exp_res to a vector. Might need to rename other functions above
    #to have set in the name instead of evaluate
    def set_vector(self,vector_obj):
        self.set_last_exp_res(IdentifierType.VECTOR,vector_obj)
        
    def program(self):
        print("Program")
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
        #Parse all expressions in the program
        while not self.check_token(TokenType.EOF):
            self.expression()
        # self.emitter.emit_global_definitions(self.global_environment.symbol_table)
        self.emitter.emit_main_section("\tmov rax,0\n\tpop rbp\n\tret")
    
    #after self.expression() is executed, what the expression evaluates to
    #will be in rax   
    def expression(self): 
        if self.check_token(TokenType.NEWLINE):
            self.next_token()
        #<constant> ::= <boolean> | <number> | <character> | <string>
        elif self.check_token(TokenType.NUMBER):
            print("EXPRESSION-NUMBER")
            if isinstance(self.cur_token.text,int):
                self.set_last_exp_res(IdentifierType.INT,str(self.cur_token.text))
                self.emitter.emit_identifier_to_section(self.last_exp_res,
                self.cur_environment.is_global())
            else:
                self.set_last_exp_res(IdentifierType.FLOAT,str(self.cur_token.text))
                self.emitter.emit_identifier_to_section(self.last_exp_res,
                self.cur_environment.is_global())
            self.next_token()
        
        elif self.check_token(TokenType.CHAR):
            print("EXPRESSION-CHAR")
            self.set_last_exp_res(IdentifierType.CHAR,self.cur_token.text)
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment.is_global())
            self.next_token()
            
        elif self.check_token(TokenType.BOOLEAN):
            print("EXPRESSION-BOOLEAN")
            self.set_last_exp_res(IdentifierType.BOOLEAN,self.cur_token.text)
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment.is_global())
            self.next_token()

        elif self.check_token(TokenType.STRING):
            print("EXPRESSION-STRING")
            self.set_last_exp_res(IdentifierType.STR,self.cur_token.text)
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment.is_global())
            self.next_token()
        
        elif self.check_token(TokenType.IDENTIFIER):
            print("EXPRESSION-VARIABLE")
            print(self.cur_token.type)
            print(self.cur_token.text)
            is_global = self.cur_environment.is_global()
            definition = None
            if self.cur_token.text in BUILTINS:
                definition = [None,Identifier(
                IdentifierType.FUNCTION,BUILTINS[self.cur_token.text])]
                self.emitter.add_extern(self.cur_token.text)
            else:
                definition = self.cur_environment.find_definition(
                self.cur_token.text)
            def_ident_obj = Environment.get_ident_obj(definition)
            
            if def_ident_obj is not None:
                self.set_last_exp_res(def_ident_obj.typeof,def_ident_obj.value)
            else:
                self.last_exp_res = None
            
            if is_global:
                self.emitter.emit_var_to_global(self.cur_token.text,definition)
            else:
                self.emitter.emit_var_to_local(self.cur_token.text,definition)
            self.next_token()
                    
        elif self.check_token(TokenType.QUOTE_SYMBOL):
            print("EXPRESSION-QUOTE-SYMBOL")
            self.next_token()
            self.datum()

        elif self.check_token(TokenType.EXPR_START):
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
                #self.parens.pop()
                
            # (delay <expression>)
            elif self.check_token(TokenType.DELAY):
                self.next_token()
                print("EXPRESSION-DELAY")
                self.expression()
                self.match(TokenType.EXPR_END)
                #self.parens.pop()
            
            elif self.check_token(TokenType.DO):
                self.next_token()
                self.do_exp()
                
            elif self.check_token(TokenType.QUASIQUOTE):
                self.next_token()
                self.quasiquote_exp()
            #<procedure call> ::= (<operator> <operand>*)
            #first exp must be an ident_obj of type function
            else:
                print("EXPRESSION-PROCEDURECALL")
                print("OPERATOR")
                self.expression()
                #this if is for register args. If a register arg is used as a
                #procedure, the type must be checked at runtime.
                if self.last_exp_res is None:
                    #this probably needs its own function
                    self.abort("Using register arg as procedure. Have to implement")
                if self.get_last_exp_type() != IdentifierType.FUNCTION:
                    self.abort(f"Application not a procedure.")
                    
                func_obj = self.last_exp_res.value
                if func_obj.is_variadic:
                    pass #function call for variadic
                else:
                    self.function_call(func_obj)  
                
        else:
            self.abort("Token " + self.cur_token.text + " is not a valid expression")
    
    def function_call(self,func_obj):
        arg_count = 0
        is_global = self.cur_environment.is_global()
        env_depth = self.cur_environment.depth
        while not self.check_token(TokenType.EXPR_END):
            print("OPERAND")
            arg_count += 1
            if arg_count > func_obj.arity:
                break
            self.expression()
            if self.last_exp_res is None:
                self.abort("In function_call, arg evaluated to None.")
            #pushes each arg to the stack so that they're stored while 
            # evaluating each arg
            self.emitter.push_arg(arg_count,func_obj.arity,env_depth,is_global)
        if arg_count != func_obj.arity:
                self.abort(f"Arity mismatch. Function " + 
                f"{func_obj.name} requires {str(func_obj.arity)} arguments.")
        #now put args in the right place and advance rsp if applicable
        for cur_arg in range(arg_count):
            if cur_arg < 6:
                self.emitter.emit_register_arg(
                cur_arg,arg_count,env_depth,is_global)
            else:
                #advance rsp to point to seventh arg
                self.emitter.subtract_rsp(
                abs(env_depth - (arg_count - 6)*8),is_global)
                break
        #function call using the pointer in a value object of type function(in c)
        if is_global:
            self.emitter.emit_main_section(
            f"\tmov rax,QWORD[{func_obj.name}]\n\t" + 
            f"lea rax,QWORD[rax + 8]\n\tcall QWORD[rax]")
        else:
            local_function_obj = self.cur_environment.find_definition(func_obj.name)
            function_offset = Environment.get_offset(local_function_obj)
            if function_offset is None:
                self.abort("local function call has no offset.")
            self.emitter.emit_function(
            f"\tmov rax,QWORD[rbp{function_offset:+}]\n\t" + 
            f"lea rax,QWORD[rax + 8]\n\tcall QWORD[rax]")
        #now add back the rsp if it was decremented :)
        if arg_count > 6:
            self.emitter.add_rsp(abs(env_depth - (arg_count - 6)*8),is_global)
        self.next_token()
        
    #returns a string which contains the next expression. used to extract body 
    # of a function. self.cur_token will be set to next char after exp
    #This method does not check if the expression has correct syntax(racket doesnt either), 
    # the error will occur will the function gets called
    #leave this function for now, but might be deleted in the future
    def extract_exp(self) -> str:
        open_paren_count = 0
        exp = []
        if self.check_token(TokenType.QUOTE_SYMBOL):
            exp.append(self.cur_token.text)
            self.next_token()
        if self.check_token(TokenType.HASH):
            exp.append(self.cur_token.text)
            self.next_token()
        if self.check_token(TokenType.EXPR_START):
            if self.check_peek(TokenType.EXPR_END):
                self.abort("Empty expression in body.")
            open_paren_count += 1
            exp.append(str(self.cur_token.text))
            self.next_token()
            while open_paren_count != 0:
                exp.append(f"{str(self.cur_token.text)} ")
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
        exp.append("\0")
        return ''.join(exp)
      
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
        
        # if len(self.parens) == 0:
        #     self.abort("Parentheses are not well formed.")
                
        #self.parens.pop()
        self.next_token()
        
    #(quote <datum>)
    def quote_exp(self):
        print("EXPRESSION-QUOTE")
        self.datum()        
        if not self.check_token(TokenType.EXPR_END):
            self.abort("Incorrect syntax in quote expression. ")
        self.next_token()
        
    #(lambda <bound var list> <body>)
    def lambda_exp(self):
        print("EXPRESSION-LAMBDA")
        self.bound_var_list()
        self.body()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
    
    def and_exp(self):
        print("EXPRESION-AND")
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.next_token()
        #self.parens.pop()
        
    def or_exp(self):
        print("EXPRESION-OR")
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.next_token()
        #self.parens.pop()
        
    # (cond <cond clause>*) | (cond <cond clause>* (else <sequence>))
    def cond_exp(self):
        print("EXPRESSION-COND")
        #first, handle case where there are 0 cond clauses and no else. basically exp is: (cond)
        if self.check_token(TokenType.EXPR_END):
            #self.parens.pop()
            self.next_token()

        # no cond clause but an else clause, so (cond (else <sequence>))
        elif self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
            self.else_rule()
            self.match(TokenType.EXPR_END)
            #self.parens.pop()
            
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
            #self.parens.pop()
            
    #(case <expression> <case clause>*) | (case <expression> <case clause>* (else <sequence>))  #<case clause> ::= ((<datum>*) <sequence>)       
    def case_exp(self):
        print("EXPRESSION-CASE")
        self.expression()
        
        if self.check_token(TokenType.EXPR_END):
            #self.parens.pop()
            self.next_token()
            
        elif self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
            self.else_rule()
            self.match(TokenType.EXPR_END)
            #self.parens.pop()
        
        # one or more case clauses and an optional else at the end
        else:
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
                    self.else_rule()
                    break
                self.case_clause()
            self.match(TokenType.EXPR_END)
            #self.parens.pop()
    
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
        #self.parens.pop()
    
    # (let* (<binding spec>*) <body>)
    def let_star_exp(self):
        print("EXPRESSION-LET*")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.binding_spec()
        self.next_token()
        self.body()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
        
    # (letrec (<binding spec>*) <body>)
    def letrec_exp(self):
        print("EXPRESSION-LETREC")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.binding_spec()
        self.next_token()
        self.body()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()

    # (set! <variable> <expression>)
    def setexclam_exp(self):
        print("EXPRESSION-SET!")
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
        
    #(rec <variable> <expression>)
    def rec_exp(self):
        print("EXPRESSION-REC")
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
        
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
        #self.parens.pop()
        self.next_token()

    # (quasiquote <datum>) , but datum is handled differently here. It must accept unquote and unquote-splicing keywords
    #remember for the emitter that for unquote, expr must evaluate to a constant, and for unquote-splicing, expr must eval to a list/vector
    def quasiquote_exp(self):
        print("EXPRESSION-QUASIQUOTE")
        self.quasiquote_datum()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
        
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
        #self.parens.append("(")
        self.expression()
        self.expression()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
        
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
            #self.parens.append(self.cur_token.text)
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
            #self.parens.pop()
            self.next_token()
            
        else:
            self.abort("Incorrect syntax in lambda expression, " + self.cur_token.text + " not a valid variable list.")
      
    # <definition> ::= (define <variable> <expression>) | (define <call pattern> <body>)
    # the define with the call pattern syntax essentially defines a function. The first arg in call pattern is function name and rest are the names of its args
    #returns name of definition
    def definition_exp(self) -> str:
        print("EXPRESSION-DEFINE")
        ident_name = None
        #num_parens = len(self.parens) - 1
        if self.check_token(TokenType.IDENTIFIER):
            print("VARIABLE")
            ident_name = self.cur_token.text
            is_global = self.cur_environment.is_global()
            #define label in bss section only if its new var
            if is_global and not self.cur_environment.is_defined(ident_name):
                self.emitter.emit_bss_section(f"\t{ident_name}: resq 1")                    
            self.next_token()
            self.expression()
            self.set_last_exp_res(self.last_exp_res.typeof,self.last_exp_res.value)
            self.cur_environment.add_definition(ident_name,
            Identifier(self.last_exp_res.typeof,self.last_exp_res.value))
            offset = Environment.get_offset(
            self.cur_environment.symbol_table[ident_name])
            self.emitter.emit_definition(ident_name,is_global,offset)
            
        elif self.check_token(TokenType.EXPR_START):
            #function case
            function = Function()
            parent_env = self.cur_environment
            previous_cur_function = self.emitter.cur_function
            self.cur_environment = parent_env.create_local_env()
            
            self.call_pattern(function)
            self.body(function)
            self.emitter.set_current_function(previous_cur_function)
            #now add function definition to parent environment
            ident_name = function.get_name()
            self.cur_environment = parent_env
            self.cur_environment.add_definition(ident_name,Identifier(
            IdentifierType.FUNCTION,function))
            self.evaluate_function(function)
            #lastly, make function object in the runtime
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment.is_global())
            is_global = self.cur_environment.is_global()
            offset = Environment.get_offset(
            self.cur_environment.symbol_table[ident_name])
            self.emitter.emit_definition(ident_name,is_global,offset)
        else:
            self.abort("Incorrect syntax in definition expression")
            
        self.match(TokenType.EXPR_END)
        # self.last_exp_res = None # since definitions arent exps
        return ident_name

    #adds param to current environment and emits if its arg 1-6. 
    #used in call_pattern
    def add_param_to_env(self,arg_count):
        if arg_count < 7:
            self.cur_environment.add_definition(self.cur_token.text,None)
            self.emitter.emit_register_param(arg_count)
        else:
            #add stack definition to env. 
            # no need to emit since on the other side of the stack
            self.cur_environment.add_stack_definition(
            self.cur_token.text,(arg_count-5)*8)
    
    # <call pattern> ::= (<pattern> <variable>*) | 
    # (<pattern> <variable>* . <variable>) where pattern ::= variable
    # populates Function obj with everything except local definitions and body
    def call_pattern(self,function):
        print("CALL_PATTERN")
        self.match(TokenType.EXPR_START)
        if self.check_token(TokenType.IDENTIFIER):
            print("PATTERN")
            function.set_name(self.cur_token.text)
            self.emitter.set_current_function(function.name)
            if function.name in self.emitter.functions: #for redifining function
                del self.emitter.functions[function.name]
            #declare space in bss section for function obj if function was made
            # from global env
            is_parent_global = self.cur_environment.parent.is_global()
            ident = self.cur_token.text
            if is_parent_global and not self.cur_environment.parent.is_defined(ident):
                self.emitter.emit_bss_section(f"\t{ident}: resq 1")
            self.emitter.emit_function_label("..@" + function.name)
            self.emitter.emit_function_prolog()
            self.next_token()
            arg_count = 0
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.DOT):
                    print("DOT")
                    function.set_variadic()
                    self.next_token()
                    if not self.check_token(TokenType.IDENTIFIER):
                        self.abort(
                        "Incorrect syntax for call pattern. Illegal use of '.'")
                    arg_count += 1
                    self.add_param_to_env(arg_count)
                    self.next_token()
                    if not self.check_token(TokenType.EXPR_END):
                        self.abort("Parentheses in call pattern not well formed.") 
                    break
                elif self.check_token(TokenType.IDENTIFIER):
                    print("VARIABLE")
                    function.add_param(self.cur_token.text)
                    #now add ALL args to environment and emit only args 1-6
                    arg_count += 1
                    self.add_param_to_env(arg_count)
                    self.next_token()
                else:
                    self.abort(self.cur_token.text + " is not an identifier.")
            self.next_token()
        else:
            self.abort("Incorrect syntax for call pattern.")

    # the definitions are the local variables declared (within the function) 
    # which will be usable in the sequence.
    # <body> ::= <definition>* <sequence>   
    def body(self,function):
        print("BODY")
        #Process all definitions, then call self.expression to create function
        #body
        while self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.DEFINE):
            self.next_token()
            self.next_token()            
            definition_name = self.definition_exp()
            function.add_local_definition(definition_name,
            Identifier(self.last_exp_res.typeof,self.last_exp_res.value))
        self.expression()
        self.emitter.emit_function_epilog()
        
    def is_constant(self):
        return self.is_token_any(self.cur_token.type,[TokenType.BOOLEAN,
        TokenType.NUMBER,TokenType.CHAR,TokenType.STRING])
    
    #evaluate_datum,evaluate_list,evaluate_vector evaluate a datnum without
    #emitting asm code
    def evaluate_datum(self):
        if self.is_constant():
            print("CONSTANT")
            self.evaluate_constant()
            self.next_token()
        elif self.check_token(TokenType.IDENTIFIER):
            print("SYMBOL")
            self.evaluate_symbol()
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            print("LIST")
            self.evaluate_list()
        elif self.check_token(TokenType.HASH):
            print("VECTOR")
            self.next_token()
            self.evaluate_vector()
        else:
            self.abort(self.cur_token.text + "Is not a valid datum.")

    #empty list is denoted by Identifier(IdentifierType.PAIR,[])
    #end of list is denoted by a None at the end. If no None at the end, then
    #it fell in to the DOT branch when evaluating list.
    #Note: None value can ONLY appear at the end
    #  # <list> ::= ( <datum>* ) | ( <datum>+ . <datum> )
    def evaluate_list(self):
        self.match(TokenType.EXPR_START)
        datum_list = []
        token_count = 0
        while not self.check_token(TokenType.EXPR_END):
            if self.check_token(TokenType.DOT):
                if token_count < 1:
                    self.abort("Creating a pair requires a car and a cdr.")
                self.next_token()
                self.evaluate_datum()
                datum_list.append(self.last_exp_res)
                break
            else:
                self.evaluate_datum()
                datum_list.append(self.last_exp_res)
                if self.check_token(TokenType.EXPR_END):
                    datum_list.append(None)
                token_count += 1
        self.match(TokenType.EXPR_END)
        self.evaluate_pair(datum_list)
    
    # <vector> ::= #( <datum>* ), starts from (
    def evaluate_vector(self):
        self.match(TokenType.EXPR_START)
        datum_list = []
        while not self.check_token(TokenType.EXPR_END):
            self.evaluate_datum()
            datum_list.append(self.last_exp_res)
        self.match(TokenType.EXPR_END)
        self.set_vector(datum_list)
        
    # starts from parens
    # <list> ::= ( <datum>* ) | ( <datum>+ . <datum> )
    
    
    # def list(self,is_quasi = False):
    #     #since this is not an expression, a list could potentially be deep within an exp, therefore store current amount of parens before processing the list
    #     print("LIST")
    #     num_parens = len(self.parens)
    #     self.parens.append(self.cur_token.text)
    #     token_count = 0
    #     self.next_token()
        
    #     datums = []
    #     is_global = self.cur_environment.is_global()
    #     self.add_extern("allocate_pair")
    #     self.emitter.emit_to_section(f"\tcall allocate_pair\n\tpush rax\n\tpush rax")
        
    #     while not self.check_token(TokenType.EXPR_END):
    #         if self.check_token(TokenType.DOT):
    #             print("DOT")
    #             if token_count < 1:
    #                 self.abort(" Creating a pair requires one or more datums before the " + self.cur_token.text + " token.")
    #             self.next_token()
    #             self.datum() if not is_quasi else self.quasiquote_datum()
                
    #             if not self.check_token(TokenType.EXPR_END):
    #                 self.abort("Incorrect syntax for making pairs.")
    #             # cur_node.set_cdr(self.last_exp_res)
    #             break
    #         else:
    #             self.datum() if not is_quasi else self.quasiquote_datum()
    #             #now set car of current(which is at the top of the stack)
    #             if not self.check_token(TokenType.DOT):
    #                 # cur_node.set_cdr(Identifier(IdentifierType.PAIR,Pair()) if not self.check_token(TokenType.EXPR_END) else None)
    #                 # cur_node = cur_node.get_cdr_value()
    #                 pass
    #             token_count += 1
                
    #     if len(self.parens) != 1 + num_parens:
    #         self.abort("Parentheses in list are not well formed.")
    #     self.parens.pop()
    #     self.evaluate_pair(datums)
    #     self.next_token()
    
    
    
    # <vector> ::= #( <datum>* ), starts from (
    # def vector(self,is_quasi = False):
    #     if not self.check_token(TokenType.EXPR_START):
    #         self.abort("Incorrect syntax for vector.")
    #     print("VECTOR")
    #     num_parens = len(self.parens)
    #     self.parens.append(self.cur_token.text)
    #     self.next_token()
    #     vector = []
    #     while not self.check_token(TokenType.EXPR_END):
    #         if self.check_token(TokenType.EXPR_START) and (self.check_peek(TokenType.UNQUOTE) or self.check_peek(TokenType.UNQUOTESPLICING)):
    #             if not is_quasi:
    #                 self.abort("UNQUOTE and UNQUOTE-SPLICING only valid in quasiquote expression.")
    #             self.next_token()
    #             self.next_token()
    #             self.expression()
    #             self.match(TokenType.EXPR_END)
    #         else:
    #             self.datum() if not is_quasi else self.quasiquote_datum()
    #             vector.append(self.last_exp_res)
        
    #     if len(self.parens) != 1 + num_parens:
    #         self.abort("Parentheses in list are not well formed.")
    #     self.parens.pop()
    #     self.evaluate_vector(vector)
    #     # print("PRINTING VECTOR:")
    #     # [print(ident.typeof,ident.value) for ident in vector]
    #     self.next_token()
    
    #<datum> ::= <constant> | <symbol> | <list> | <vector>
    def datum(self):
        print("DATUM")
        self.evaluate_datum()
        is_global = self.cur_environment.is_global()
        self.emitter.emit_identifier_to_section(self.last_exp_res,is_global)
    
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