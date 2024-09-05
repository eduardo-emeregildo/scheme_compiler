from lex import *
import sys

def main():
    if len(sys.argv) != 2:
        print("Incorrect number of arguments. The correct usage is: python compiler.py <filePath> or just the file name if the file is in the same directory")
    f = open(sys.argv[1],"r")
    source = f.read()
    f.close()
    
    lexer = Lexer(source)
    while lexer.cur_char != "\0":
        print(lexer.cur_char, " at position ", lexer.cur_pos)
        lexer.next_char()

main()