from enum import Enum
from scheme_builtins import BUILTINS
import sys

class Lexer:
    def __init__(self,source) -> None:
        self.source = source + '\n'
        self.cur_char = ''
        self.cur_pos = -1
        self.source_len = len(source)
        #for the keywords that have special characters in them, 
        # since enum wont accept them as names. val is array, arr[0] is its internal
        #name, arr[1] is the corresponding token
        self.special_chars = {
            "LET*": ["LET_STAR",TokenType.LETSTAR],
            "EQV?": ["EQV",TokenType.BUILTIN],
            "EQUAL?" : ["EQUAL",TokenType.BUILTIN],
            "EQ?" : ["EQ",TokenType.BUILTIN],
            "SET!": ["SETE",TokenType.SETEXCLAM],
            "UNQUOTE-SPLICING" : ["UNQUOTESPL",TokenType.UNQUOTESPLICING],
            "NULL?": ["NULLQ",TokenType.BUILTIN],
        }
        self.next_char()
        
     # go to next char in string.
    def next_char(self) -> None:
        self.cur_pos += 1
        if self.cur_pos >= self.source_len:
            self.cur_char = "\0" #eof
        else:
            self.cur_char = self.source[self.cur_pos]

    # Return the lookahead character.
    def peek(self) -> str:
        if self.cur_pos + 1 >= self.source_len:
            return "\0"
        else:
            return self.source[self.cur_pos + 1]

    # Invalid token found, print error message and exit.
    def abort(self, message):
        sys.exit(message)
		
    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skip_whitespace(self):
        while self.cur_char == "\n" or self.cur_char == "\t" or self.cur_char == "\r" or self.cur_char == " " :
            self.next_char()
		
    # Skip comments in the code.
    def skip_comment(self):
        if self.cur_char == ";":
            while self.cur_char != "\n" and self.cur_pos < self.source_len:
                self.next_char()

    # Return the token of the current char.
    def get_token(self) -> Enum:
        self.skip_whitespace()
        self.skip_comment()
        token = None
        
        #tokens of length 1
        if self.cur_char == "(":
            token = Token(self.cur_char,TokenType.EXPR_START)
        elif self.cur_char == ")":
            token = Token(self.cur_char,TokenType.EXPR_END)
        elif self.cur_char == "\n":
            token = Token(self.cur_char,TokenType.NEWLINE)
        elif self.cur_char == "\0":
            token = Token(self.cur_char,TokenType.EOF)
        elif self.cur_char == "." and (self.peek() == " " or self.peek() == "\n" or self.peek() == "\t" or self.peek() == "\r"):
            token = Token(self.cur_char,TokenType.DOT)
        elif self.cur_char == "+" and (not self.peek().isdigit()) and (self.peek() != "."):
            token = Token("ADDITION",TokenType.BUILTIN)
        elif self.cur_char == "-" and (not self.peek().isdigit()) and (self.peek() != "."):
            #token = Token(self.cur_char,TokenType.MINUS)
            token = Token("SUBTRACTION",TokenType.BUILTIN)
        elif self.cur_char == "*":
            #token = Token(self.cur_char,TokenType.ASTERISK)
            token = Token("MULT",TokenType.BUILTIN)
        elif self.cur_char == "/":
            #token = Token(self.cur_char,TokenType.SLASH)
            token = Token("DIVISION",TokenType.BUILTIN)
        elif self.cur_char == "=":
            # token = Token(self.cur_char,TokenType.EQUAL_SIGN)
            token = Token("EQUAL_SIGN",TokenType.BUILTIN)
        elif self.cur_char == "'":
            token = Token(self.cur_char,TokenType.QUOTE_SYMBOL)
        elif self.cur_char == "<":
            if self.peek() == "=":
                last = self.cur_char
                self.next_char()
                # token = Token(last + self.cur_char,TokenType.LEQ)
                token = Token("LESS_EQUAL",TokenType.BUILTIN)
            else:
                # token = Token(self.cur_char,TokenType.LESS)
                token = Token("LESS",TokenType.BUILTIN)

        elif self.cur_char == ">":
            if self.peek() == "=":
                last = self.cur_char
                self.next_char()
                # token = Token(last + self.cur_char,TokenType.GEQ)
                token = Token("GREATER_EQUAL",TokenType.BUILTIN)
            else:
                # token = Token(self.cur_char,TokenType.GREATER)
                token = Token("GREATER",TokenType.BUILTIN)
        #Now the datatypes
        elif self.cur_char == "#":
            if self.peek() == "t" or self.peek() == "T" or self.peek() == "f" or self.peek() == "F":
                last = self.cur_char
                self.next_char()
                token = Token(last + self.cur_char.lower(),TokenType.BOOLEAN)
            elif self.peek() == "\\":
                self.next_char()
                #this is suspect, might need to be more restrictive with which characters are valid
                if self.peek() != "\0":
                    self.next_char()
                    token = Token(self.cur_char,TokenType.CHAR)
                else:
                    self.abort("Cannot set a character to \0.")
            elif self.peek() == "(":
                token = Token(self.cur_char,TokenType.HASH)
            else: 
                self.abort("Illegal character after the #." + self.peek())
        #numbers
        elif self.cur_char == "." or self.cur_char.isdigit() or self.cur_char == "+" or self.cur_char == "-":
            start = self.cur_pos
            peek = self.peek()
            while peek != "\0" and (peek == "." or peek.isdigit()):
                self.next_char()
                peek = self.peek()
            text = self.source[start : self.cur_pos + 1]
            try:
                token = Token(int(text),TokenType.NUMBER)
            except:
                try:
                    token = Token(float(text),TokenType.NUMBER)
                except:
                    self.abort("Error: Invalid number.")
        #strings
        elif self.cur_char == '"':
            start = self.cur_pos
            found = False
            peek = self.peek()
            while peek != "\0" and not found:
                if peek == '"':
                    found = True
                self.next_char()
                peek = self.peek()
            if found:
                token = Token(self.source[start:self.cur_pos + 1],TokenType.STRING)
            else:
                self.abort("Error: Invalid string")
                
        #keywords/identifiers. characters like _,-,>,< are acceptable for the start of an identifier
        elif self.cur_char != "\n" and self.cur_char != "\t" and self.cur_char != "\r" and self.cur_char != " ":
            start = self.cur_pos
            peek = self.peek()
            while peek != "\0" and peek != "\n" and peek != "\t" and peek != "\r" and peek != " " and peek != "(" and peek != ")":
                if peek == '"' or peek == "'":
                    self.abort("Invalid identifier name.")
                self.next_char()
                peek = self.peek()                
            token_text = self.source[start : self.cur_pos + 1]
            token_text_upper = token_text.upper()
            if token_text_upper in BUILTINS:
                token = Token(token_text_upper,TokenType.BUILTIN)
            elif token_text_upper in self.special_chars:
                special_char_info = self.special_chars[token_text_upper]
                internal_name = special_char_info[0]
                char_token = special_char_info[1]
                token = Token(internal_name,char_token)
            else:
                keyword = Token.check_if_keyword(token_text_upper)
                if keyword == None:
                    token = Token(token_text,TokenType.IDENTIFIER)
                else:
                    token = Token(token_text_upper,keyword)
            
        else:
            self.abort("Unknown Token: " + self.cur_char)
        self.next_char()
        return token
        
TokenType = Enum(
    value = "TokenType",
    names = [
        ("EOF" , -1),
        ("NEWLINE" , 0),
        ("IDENTIFIER" , 1),
        ("EXPR_START" , 2),
        ("EXPR_END" , 3),
        #for making pairs
        ("DOT" , 4),
        #for vector purposes
        ("HASH",5),
        
        #Operators
        # ("PLUS" , 201),
        # ("MINUS" , 202),
        #("ASTERISK" , 203),
        #("SLASH" , 204),
        # ("EQUAL_SIGN" , 205),
        ("QUOTE_SYMBOL" , 206),
        # ("LESS" , 207),
        # ("GREATER" , 208),
        #Operators longer than 1
        # ("LEQ" , 209),
        # ("GEQ" , 210),
        #KeyWord Operators
        #("CAR" , 301),
        #("CDR" , 302),
        ("CADR" , 303),
        ("CONS" , 304),
        ("LIST" , 305),
        ("DEFINE" , 306),
        ("SET" , 307),
        ("SQRT" , 308),
        ("ABS" , 309),
        ("QUOTE" , 310),
        ("AND" , 311),
        ("OR" , 312),
        ("NOT" , 313),
        ("EQ" , 314),
        ("EQV" , 315),
        ("EQUAL" , 316),
        ("LAMBDA", 317),
        ("LET", 318),
        ("IF",319),
        ("COND", 320),
        ("ELSE", 321),
        ("CASE", 322),
        ("LETSTAR",323),
        ("LETREC", 324),
        ("REC",325),
        ("SETEXCLAM",326),
        ("BEGIN",327),
        ("DELAY",328),
        ("DO",329),
        ("QUASIQUOTE",330),
        ("UNQUOTE", 331),
        ("UNQUOTESPLICING",332),
        #OPERANDS/Datatypes
        ("BOOLEAN" , 401),
        ("CHAR" , 402),
        ("STRING" , 403),
        ("NUMBER" , 404),
        # LIST = 405
        # VECTOR = 406
        # BYTEVECTOR = 407
        #type for all builtin functions. the text will how the builtin is
        #referenced in the runtime
        ("BUILTIN", 501),
    ]
)
    
class Token:
    def __init__(self,token_text,token_type) -> None:
        self.text = token_text
        self.type = token_type
    
    @staticmethod
    def check_if_keyword(token_text):
        for type in TokenType:
            if type.value >= 300 and type.value < 400 and type.name == token_text:
                return type
        return None