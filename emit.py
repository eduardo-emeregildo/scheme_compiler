from environment import *
# Emitter object keeps track of the generated start_code and outputs it.
#footer might be needed for the data segment
#If i run into performance issues modify functions to use less concatenations or to concat by putting strs in a list and calling .join

ident_type_to_word = {
    IdentifierType.INT : "dq",
    IdentifierType.FLOAT : "dq",
    IdentifierType.STR : "db",
    IdentifierType.SYMBOL: "db",
    IdentifierType.CHAR: "db",
    IdentifierType.BOOLEAN: "db" 
}

class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.data_section = "section .data\n"
        self.text_section = "section .text\nglobal _start\n"
        self.start_code = "_start:\n"
        self.functions = ""
        
        
    def emit_data_section(self,code):
        self.data_section += code + '\n'
    
    
    def emit_data_label(self,label):
        self.emit_data_section(label + ":")
    
    #if ident_name is "", will omit the label and just output for example dq 10, instead of x:\n\tdq 10. Think of it as an anonymous var
    def global_const_asm(self,ident_obj,ident_name = ""):

        ident_type = ident_obj.typeof
        if ident_type == IdentifierType.INT or ident_type == IdentifierType.FLOAT:
            return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}dq {ident_obj.value}"
        elif ident_type == IdentifierType.CHAR:
            return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}db '{ident_obj.value[-1]}'"
        elif ident_type == IdentifierType.STR:
            return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}db {ident_obj.value}, 0"
        elif ident_type == IdentifierType.SYMBOL:
            return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}db '{ident_obj.value}', 0"
        elif ident_type == IdentifierType.BOOLEAN:
            return f"{f'{ident_name}:\n\t' if len(ident_name) != 0 else "\t"}db {'1' if ident_obj.value =='#t' else '0'}"
    
    def global_vector_body_asm(self,label,vector_obj):
        emitted_elts = []
        offset = 0
        for ident_obj in vector_obj:
            if ident_obj.typeof == IdentifierType.PAIR:
                emitted_elts.append(self.global_pair_body_asm(label,ident_obj.value,offset))
            elif ident_obj.typeof == IdentifierType.VECTOR:
                emitted_elts.append(self.global_vector_body_asm(label,ident_obj.value))
            else:
                emitted_elts.append(self.global_const_asm(ident_obj))
                
            offset += ident_obj.get_size()
        return '\n'.join(emitted_elts)
            
    #offset is how many bytes from label the pair will be written at  
    def global_pair_body_asm(self,label,pair_obj,offset = 0):
        emitted_elts = []
        #the pair_obj represents the empty list. both the car and cdr are set to 0x0
        # if pair_obj.car is None and pair_obj.cdr is None:
        if pair_obj.is_empty_list():
            return "\tdb 0x0\n\tdb 0x0\n"
        #the car of the pair_obj is the empty list
        if pair_obj.car is None:
            emitted_elts.append("db 0x0")
        elif pair_obj.car.typeof == IdentifierType.PAIR:
            emitted_elts.append(self.global_pair_body_asm(label,pair_obj.car.value,offset))
        elif pair_obj.car.typeof == IdentifierType.VECTOR:
            emitted_elts.append(self.global_vector_body_asm(label,pair_obj.car.value))
        else:
            #list elt is a constant
            emitted_elts.append(self.global_const_asm(pair_obj.car))
            
        #now handle the cdr
        if pair_obj.cdr is None:
            emitted_elts.append("\tdb 0x0")
        elif pair_obj.cdr.typeof == IdentifierType.PAIR:
            #dealing with a list. write asm for the ptr to cdr, and asm for the cdr itself
            next_pair_offset = pair_obj.car.get_size() + offset + 8
            emitted_elts.append(f"\tdq {label} + {str(next_pair_offset)}")
            emitted_elts.append(self.global_pair_body_asm(label,pair_obj.cdr.value,next_pair_offset))
        elif pair_obj.car.typeof == IdentifierType.VECTOR:
            emitted_elts.append(self.global_vector_body_asm(label,pair_obj.car.value))
        else:
            emitted_elts.append(self.global_const_asm(pair_obj.cdr))
        return '\n'.join(emitted_elts)
            
            
    def emit_global_pair(self,label,pair_obj):
        self.emit_data_label(label)
        self.emit_data_section(self.global_pair_body_asm(label,pair_obj))
        
    def emit_global_vector(self,label,vector_obj):
        self.emit_data_label(label)
        self.emit_data_section(self.global_vector_body_asm(label,vector_obj))
        
    def emit_global_definitions(self,def_dict):
        emitted_definitions = []
        for ident_name in def_dict:
            ident_type = def_dict[ident_name].typeof
            if ident_type in ident_type_to_word:
                emitted_definitions.append(self.global_const_asm(def_dict[ident_name],ident_name))
            elif ident_type == IdentifierType.PAIR:
                self.emit_global_pair(ident_name,def_dict[ident_name].value)
            elif ident_type == IdentifierType.VECTOR:
                self.emit_global_vector(ident_name,def_dict[ident_name].value)             
        # symbol type is currently being emitted, this could be subject to change
        self.emit_data_section('\n'.join(emitted_definitions))

            
    
    def emit_start_section(self,code):
        self.start_code += code + '\n'
    
    def emit_function(self,code):
        self.functions += code + '\n'    
        
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            outputFile.write(self.data_section + self.text_section + self.start_code + self.functions)
            
            

        
    

