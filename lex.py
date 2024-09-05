from enum import Enum

class Lexer:
    def __init__(self,source) -> None:
        self.source = source + '\n'
        self.cur_char = ''
        self.cur_pos = -1
        self.source_len = len(source)
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
        pass
		
    # Skip whitespace except newlines, which we will use to indicate the end of a statement.
    def skip_whitespace(self):
        if self.cur_char == '\n' or self.cur_char == '\t' or self.cur_char == '\r':
            self.next_char()
		
    # Skip comments in the code.
    def skip_comment(self):
        pass

    # Return the next token.
    def get_token(self):
        pass

class TokenType(Enum):
    EOF = -1
    NEWLINE = 0
    IDENTIFIER = 1
    EXP_START = 2
    EXP_END = 3
    
    #Operators
    PLUS = 201
    MINUS = 202
    ASTERISK = 203
    SLASH = 204
    CAR = 205
    CDR = 206
    CONS = 207
    LIST_WORD = 208
    DEF = 209
    SET = 210
    
    #OPERANDS
    BOOLEAN = 301
    CHAR = 302
    SYMBOL = 303
    NUMBER = 304
    LIST = 305
    VECTOR = 306
    BYTEVECTOR = 307


class Token:
    def __init__(self,token_text,token_type) -> None:
        self.text = token_text
        self.type = token_type
        
        
    