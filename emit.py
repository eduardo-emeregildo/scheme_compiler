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
        self.local_labels.append(f".LC{len(self.local_labels)}: db {string},0")
    
    #given an Identifier obj, will emit the corresponding asm. The result will be in rax
    def emit_identifier(self,ident_obj):
        match ident_obj.typeof:
            case IdentifierType.CHAR:
                self.emit_extern("make_tagged_char")
                self.emit_main_section(
                f"\tmov rdi, '{ident_obj.value}'\n\tcall make_tagged_char")
            case IdentifierType.STR:
                self.emit_extern("allocate_str")
                self.emit_extern("make_value_string")
                self.emit_local_label(ident_obj.value)
                self.emit_main_section(
                f"\tmov rdi, main.LC{len(self.local_labels) - 1}\n\t"
                f"call allocate_str\n\tmov rdi,rax\n\tcall make_value_string")
            case IdentifierType.INT:
                self.emit_extern("make_tagged_int")
                self.emit_main_section(f"\tmov rdi, {ident_obj.value}\
                \n\tcall make_tagged_int")
            case IdentifierType.FLOAT:
                self.emit_extern("make_value_double")
                self.emit_main_section(f"\tmov rax, __?float64?__("
                f"{ident_obj.value})\n\tmovq xmm0, rax\n\t"
                f"call make_value_double")
            case IdentifierType.BOOLEAN:
                self.emit_extern("make_tagged_bool")
                self.emit_main_section(
                f"\tmov rdi, {'0x1' if ident_obj.value == '#t' else '0x0'}"
                f"\n\tcall make_tagged_bool")
            case IdentifierType.PAIR:
                print("Implement emit_identifier for pair!")
            case IdentifierType.VECTOR:
                print("Implement emit_identifier for vector!")
            case Identifier.FUNCTION:
                print("Implement emit_identifier for function!")
            case IdentifierType.SYMBOL:
                self.emit_extern("allocate_str")
                self.emit_extern("make_value_symbol")
                #not sure if quotes included for symbols, i dont think so
                self.emit_local_label(f"'{ident_obj.value}'")
                self.emit_main_section(
                f"\tmov rdi, main.LC{len(self.local_labels) - 1}\n\t"
                f"call allocate_str\n\tmov rdi,rax\n\tcall make_value_symbol")
                
                
    
    def emit_externs(self):
        self.emit_text_section("" if len(self.externs) == 0 else f"extern {','.join(list(self.externs))}\n")
        
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            self.emit_externs()
            outputFile.write(self.bss_section + self.text_section + 
            self.main_code +'\n'.join(self.local_labels) + self.functions)