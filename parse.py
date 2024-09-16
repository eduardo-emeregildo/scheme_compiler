import sys
from lex import *
#Todo0: write logic for lambda expressions

#Todo1: first implement parser, make sure you add the extra grammar(cons,car,cdr etc) to the grammar doc and to the parser. then add syntax analysis. Keep in mind that Scheme is dynamically typed

#somewhere down the line implement special functions in vector/list, such as vector-ref for example
# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.cur_token = None
        self.peek_token = None
        self.definitions = {}
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
            self.abort("Expected " + type.name + ", got " + self.cur_token.type)
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
            if self.cur_token.text in self.definitions:
                print("EXPRESSION-VARIABLE")
                self.next_token()
            else:
                self.abort(self.cur_token.text + " Undefined.")
        
        elif self.check_token(TokenType.EXPR_END):
            if len(self.parens) == 0:
                self.abort("Parentheses are not well formed.")
            self.parens.pop()
            self.next_token()
            
        elif self.check_token(TokenType.EXPR_START):
            self.parens.append(self.cur_token.text)
            self.next_token()
            if self.check_token(TokenType.IF):
                self.next_token()
                self.if_exp()

            elif self.check_token(TokenType.QUOTE):
                self.next_token()
                self.quote_exp()
                
            
            else:
                self.abort("Token " + self.cur_token.text + " is not an operator")
                
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
            if not self.cur_token.text in self.definitions:
                self.abort(self.cur_token.text + " Undefined")
            print("SYMBOL")
            self.next_token()
        
        elif self.check_token(TokenType.EXPR_START):
            self.list()
            
        elif self.check_token(TokenType.HASH):
            self.next_token()
            self.vector()
        
        else:
            self.abort(self.cur_token.text + " Is not a valid datnum.")