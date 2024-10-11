from environment import *
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
        
    def emit_global_definitions(self,def_dict):
        for ident_name in def_dict:
            ident_type = def_dict[ident_name].typeof
            if ident_type == IdentifierType.INT:
                self.emit_data_section(ident_name+ ":\n" + "dq " + def_dict[ident_name].value)
            elif ident_type == IdentifierType.FLOAT:
                self.emit_data_section(ident_name+ ":\n" + "dq " + def_dict[ident_name].value)
            elif ident_type == IdentifierType.CHAR:
                self.emit_data_section(ident_name+ ":\n" + "db '" + def_dict[ident_name].value[-1] + "'")
            elif ident_type == IdentifierType.STR:
                self.emit_data_section(ident_name+ ":\n" + "db " + def_dict[ident_name].value + ", 0")
            elif ident_type == IdentifierType.BOOLEAN:
                self.emit_data_section(ident_name+ ":\n" + "db " + '1' if def_dict[ident_name].value == '#t' else '0')
        # this will eventually accept list and vector (dont think symbol should emit anything since it doesnt evaluate, idk though )

            
    
    def emit_start_section(self,code):
        self.start_code += code + '\n'
    
    def emit_function(self,code):
        self.functions += code + '\n'    
        
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            outputFile.write(self.data_section + self.text_section + self.start_code + self.functions)
            
            

        
    

