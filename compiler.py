from lex import *
from parse import *
from emit import *
import sys

def main():
    if len(sys.argv) != 2:
        print("Incorrect number of arguments. The correct usage is: python compiler.py <filePath> or just the file name if the file is in the same directory")
    f = open(sys.argv[1],"r")
    source = f.read()
    f.close()


    #lexer driver code    
    # # print(lexer.source_len)
    # token = lexer.get_token()
    # while token.type != TokenType.EOF:
    #     # print(lexer.cur_char, " at position ", lexer.cur_pos)
    #     print(token.type,token.text)
    #     # lexer.next_char()
    #     token = lexer.get_token()
    
    #parser driver code
    # lexer = Lexer(source)
    # parser = Parser(lexer)
    # parser.program()
    # print("Parsing finished")
    
    #emitter driver code
    lexer = Lexer(source)
    emitter = Emitter("out.asm")
    parser = Parser(lexer, emitter)

    parser.program() # Start the parser.
    emitter.writeFile() # Write the output to file.
    print("Compiling completed.")
    

            
main()