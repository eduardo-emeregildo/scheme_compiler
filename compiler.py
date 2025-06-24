from lex import *
from parse import *
from emit import *
from environment import *
import sys
import os

def main():
    if len(sys.argv) != 2:
        sys.exit("Incorrect number of arguments. The correct usage is:" +  
        " python compiler.py <filePath> or just the file name if the file is in the same directory")
    if sys.argv[1] == "-init":
        os.system("gcc -O3 -c identifier.c")
        os.system("gcc -O3 -c lib.c")
        return
    f = open(sys.argv[1],"r")
    source = f.read()
    f.close()
    #emitter driver code
    lexer = Lexer(source)
    emitter = Emitter("out.asm")
    parser = Parser(lexer, emitter)
    parser.program() # Start the parser.
    emitter.writeFile() # Write the output to file.
    os.system("nasm -f elf64 -g -F dwarf out.asm")
    os.system("gcc -O3 out.o identifier.o lib.o -lm -o out -no-pie -z noexecstack")
    os.system("rm out.asm out.o")
    print("Compiling completed.")
main()