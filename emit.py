# Emitter object keeps track of the generated code and outputs it.
class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.header = ""
        self.code = ""

    def emit(self, code):
        self.code += code

    def emitLine(self, code):
        self.code += code + '\n'

    def headerLine(self, code):
        self.header += code + '\n'

    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            outputFile.write(self.header + self.code)
            
            
            
class Environment:
    def __init__(self):
        #environment is global scope. New environments will be nested dictionaries. This way you have a way to traverse back in scope(i.e. use a global variable from a function's scope). Any variables that are more deeply nested than the current environment will be out of scope and thus not checked.
        #Best approach may be to implement a spaghetti stack, with each node having a dictionary of variables declared in that scope. 
        self.environment = {}
        
        def add_node(self,parent):
            pass
        
        def find_ancestor(self,node):
            pass
    

