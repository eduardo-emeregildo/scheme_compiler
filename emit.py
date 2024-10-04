# Emitter object keeps track of the generated start_code and outputs it.
#footer might be needed for the data segment
class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.data_section = "section .data\n"
        self.text_section = "section .text\nglobal _start\n"
        self.start_code = "_start:\n"
        self.functions = ""
        
        
    def emit_data_section(self,code):
        self.data_section += code + '\n'
    
    def emit_start_section(self,code):
        self.start_code += code + '\n'
    
    def emit_function(self,code):
        self.functions += code + '\n'    
        
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            outputFile.write(self.data_section + self.text_section + self.start_code + self.functions)
            
            
            
class Environment:
    def __init__(self):
        #environment is global scope. New environments will be nested dictionaries. This way you have a way to traverse back in scope(i.e. use a global variable from a function's scope). Any variables that are more deeply nested than the current environment will be out of scope and thus not checked.
        #Best approach may be to implement a spaghetti stack, with each node having a dictionary of variables declared in that scope. 
        self.environment = {}
        
        def add_node(self,parent):
            pass
        
        def find_ancestor(self,node):
            pass
    

