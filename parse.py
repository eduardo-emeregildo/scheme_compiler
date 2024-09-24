import sys
from lex import *
#Todo0: implement let expression
#Todo1: first implement parser, make sure you add the extra grammar(cons,car,cdr etc) to the grammar doc and to the parser. then add syntax analysis. Keep in mind that Scheme is dynamically typed and has garbage collection

#somewhere down the line implement special functions in vector/list, such as vector-ref for example
# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.cur_token = None
        self.peek_token = None
        #scoping will be implemented at a later stage
        # self.definitions = set()
        #parens will be a stack to easily keep track of parens
        self.parens = []
        self.next_token()
        self.next_token()

    # Return true if the current token matches.
    def check_token(self, type):
        return type == self.cur_token.type
    

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
        
        
    def program(self):
        print("Program")
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
        #Parse all expressions in the program
        while not self.check_token(TokenType.EOF):
            self.expression()
            
    def expression(self):
        #<constant> ::= <boolean> | <number> | <character> | <string>
        if self.check_token(TokenType.NUMBER):
            print("EXPRESSION-NUMBER")
            self.next_token()
        
        elif self.check_token(TokenType.CHAR):
            print("EXPRESSION-CHAR")
            self.next_token()
            
        elif self.check_token(TokenType.BOOLEAN):
            print("EXPRESSION-BOOLEAN")
            self.next_token()

        elif self.check_token(TokenType.STRING):
            print("EXPRESSION-STRING")
            self.next_token()
        
        elif self.check_token(TokenType.IDENTIFIER):
            print("EXPRESSION-VARIABLE")
            self.next_token()
                    
        elif self.check_token(TokenType.QUOTE_SYMBOL):
            print("EXPRESSION-QUOTE-SYMBOL")
            self.next_token()
            self.datnum()
            
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
            
            #Procedure call grammar rule will be the last one implemented here
                
            else:
                self.abort("Token " + str(self.cur_token.text) + " is not an operator")
                
        else:
            self.abort("Token " + self.cur_token.text + " is not a valid expression")
                
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
        self.datnum()        
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
            self.datnum()
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
    #mapping the variable to the evaluation of the expression will be handled in the emitter
    def definition_exp(self):
        print("EXPRESSION-DEFINE")
        num_parens = len(self.parens) - 1
        if self.check_token(TokenType.IDENTIFIER):
            print("VARIABLE")
            self.next_token()
            self.expression()
        elif self.check_token(TokenType.EXPR_START):
            self.call_pattern()# here add the call pattern and body methods
            self.body()
        else:
            self.abort("Incorrect syntax in definition expression")
            
        self.match(TokenType.EXPR_END)
        if len(self.parens) != 1 + num_parens:
            self.abort("Parentheses are not well formed.")
        self.parens.pop()
    
      # <call pattern> ::= (<pattern> <variable>*) | (<pattern> <variable>* . <variable>), where pattern ::= variable | <call pattern>
    def call_pattern(self):
        print("CALL_PATTERN")
        num_parens = len(self.parens)
        self.parens.append(self.cur_token.text)
        self.next_token()
        if self.check_token(TokenType.IDENTIFIER):
            print("PATTERN")
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
        
     
     # the definition are the local variables declared which will be usable in the sequence. This is the equivalent of creating a variable inside of a function in other programming languages.
     # <body> ::= <definition>* <sequence>   
    def body(self):
        print("BODY")
        #Process all definitions first. then process sequence with self.expression()
        while self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.DEFINE):    
            self.parens.append(self.cur_token.text)
            self.next_token()
            self.next_token()
            self.definition_exp()
        self.expression()
            
    def is_constant(self):
        return self.is_token_any(self.cur_token.type,[TokenType.BOOLEAN,TokenType.NUMBER,TokenType.CHAR,TokenType.STRING])
        
    # starts from parens
    # <list> ::= ( <datum>* ) | ( <datum>+ . <datum> )
    def list(self):
        #since this is not an expression, a list could potentially be deep within an exp, therefore store current amount of parens before processing the list
        print("LIST")
        num_parens = len(self.parens)
        self.parens.append(self.cur_token.text)
        token_count = 0
        self.next_token()

        while not self.check_token(TokenType.EXPR_END):
            if self.check_token(TokenType.DOT):
                print("DOT")
                if token_count < 1:
                    self.abort(" Creating a pair requires one or more datnums before the " + self.cur_token.text + " token.")
                self.next_token()
                self.datnum()
                if not self.check_token(TokenType.EXPR_END):
                    self.abort("Incorrect syntax for making pairs.")
                break
                
            else:
                self.datnum()
                token_count += 1
            

        if len(self.parens) != 1 + num_parens:
            self.abort("Parentheses in list are not well formed.")
        self.parens.pop()
        self.next_token()
    
    # <vector> ::= #( <datum>* ), starts from (
    def vector(self):
        if not self.check_token(TokenType.EXPR_START):
            self.abort("Incorrect syntax for vector.")
        print("VECTOR")
        num_parens = len(self.parens)
        self.parens.append(self.cur_token.text)
        self.next_token()
        
        while not self.check_token(TokenType.EXPR_END):
            self.datnum()
        
        if len(self.parens) != 1 + num_parens:
            self.abort("Parentheses in list are not well formed.")
        self.parens.pop()
        self.next_token()
        

    #<datum> ::= <constant> | <symbol> | <list> | <vector>
    def datnum(self):
        print("DATNUM")
        if self.is_constant():
            print("CONSTANT")
            self.next_token()
            
        elif self.check_token(TokenType.IDENTIFIER):
            print("SYMBOL")
            self.next_token()
        
        elif self.check_token(TokenType.EXPR_START):
            self.list()
            
        elif self.check_token(TokenType.HASH):
            self.next_token()
            self.vector()
        
        else:
            self.abort(self.cur_token.text + " Is not a valid datnum.")