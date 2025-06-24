# Scheme Compiler
A compiler written in Python, C, and x64 assembly that compiles the Scheme
programming language, targeting 64 bit Linux machines.

## Description
The BNF used to parse the Scheme code can be found [here.](https://groups.csail.mit.edu/mac/ftpdir/scheme-mail/HTML/rrrs-1986/msg00080.html) \
This compiler supports all the typical features included with Scheme, such as:
* Dynamic typing
* Lexical scoping
* First-class functions
* Variadic functions
* Closures
* Garbage collection

The garbage collection strategy used is the mark-and-sweep algorithm. This choice
was made because mark-and-sweep handles circular references and doesn't have the space overhead that automatic reference counting does.
## Building and Running
Requires `gcc`,`nasm` and `python3` on a 64 bit Linux operating system, with an x64 processor.

To build, run:
1. `git clone https://github.com/eduardo-emeregildo/scheme_compiler`
2. `cd scheme_compiler`
3. `python3 compiler.py -init`

To compile a Scheme file and run the executable, run:
1. `python3 compiler.py /path/of/file.scm`
2. `./out`
