from environment import *
from generation import *
# Emitter object keeps track of the generated main_code and outputs it.
#If i run into performance issues modify functions to use less concatenations or to concat by putting strs in a list and calling .join

class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.externs = set() #for tracking which externs need to be added
        self.local_labels = [] #for creating character arrays. will go under
        #main section. if i wanna add string interning this is where i would have to look
        self.bss_section = "section .bss\n"
        self.text_section = "section .text\n"
        self.main_code = "global main\nmain:\n\tpush rbp\n\tmov rbp,rsp\n"
        self.functions = ""
        
    def emit_data_label(self,label):
        self.emit_bss_section(label + ":")
        
    def emit_bss_section(self,code):
        self.bss_section += code + '\n'

    def emit_function(self,code):
        self.functions += code + '\n'
        
    def emit_global_definitions(self,def_dict):
        emitted_definitions = []
        factory = GeneratorFactory()
        for ident_name in def_dict:
            type_generator = factory.create_generator(def_dict[ident_name],0,ident_name)
            emitted_definitions.append(f"{ident_name}:")
            emitted_definitions.append(type_generator.generate_global_var())
        self.emit_bss_section('\n'.join(emitted_definitions))
            
    def emit_main_section(self,code):
        self.main_code += code + '\n'
        
    def emit_text_section(self,code):
        self.text_section += code + '\n'
    
    def emit_extern(self,extern_str):
        self.externs.add(extern_str)
    
    def emit_local_label(self,string):
        self.local_labels.append(f".LC{len(self.local_labels)}: db {string}")
    
    #given an Identifier obj, will emit the corresponding asm. The result will be in rax
    # def emit_identifier(self,ident_obj):
    #     match ident_obj.typeof:
    #         case
    
    def emit_externs(self):
        self.emit_text_section("" if len(self.externs) == 0 else f"extern {','.join(list(self.externs))}\n")
        
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            self.emit_externs()
            outputFile.write(self.bss_section + self.text_section + 
            self.main_code +'\n'.join(self.local_labels) + self.functions)