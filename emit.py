from environment import *
from global_var_generator import *
# Emitter object keeps track of the generated start_code and outputs it.
#footer might be needed for the data segment
#If i run into performance issues modify functions to use less concatenations or to concat by putting strs in a list and calling .join

class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.data_section = "section .data\n"
        self.text_section = "section .text\nglobal _start\n"
        self.start_code = "_start:\n"
        self.functions = ""
        
    def emit_data_label(self,label):
        self.emit_data_section(label + ":")
        
    def emit_data_section(self,code):
        self.data_section += code + '\n'

    def emit_function(self,code):
        self.functions += code + '\n'
        
    def emit_global_definitions(self,def_dict):
        emitted_definitions = []
        for ident_name in def_dict:
            ident_type = def_dict[ident_name].typeof
            if ident_type in ident_type_to_word:
                emitted_definitions.append(generate_const(def_dict[ident_name],ident_name))
            elif ident_type == IdentifierType.PAIR:
                emitted_definitions.append(generate_label(ident_name))
                emitted_definitions.append(generate_pair_body(ident_name,def_dict[ident_name].value))
            elif ident_type == IdentifierType.VECTOR:
                emitted_definitions.append(generate_label(ident_name))
                emitted_definitions.append(generate_vector_body(ident_name,def_dict[ident_name].value))        
        # symbol type is currently being emitted, this could be subject to change
        self.emit_data_section('\n'.join(emitted_definitions))
            
    def emit_start_section(self,code):
        self.start_code += code + '\n'
                                       
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            outputFile.write(self.data_section + self.text_section + self.start_code + self.functions)