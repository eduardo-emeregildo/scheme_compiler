from environment import *
from generation import *
import sys
# Emitter object keeps track of the generated main_code and outputs it.
#If i run into performance issues modify functions to use less concatenations or 
# to concat by putting strs in a list and calling .join
LINUX_CALLING_CONVENTION = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.externs = set() #for tracking which externs need to be added
        self.local_labels = [] #for creating character arrays. will go under
        #main section. if i wanna add string interning this is where i would have to look
        self.bss_section = "section .bss\n"
        self.text_section = "section .text\nglobal main\n"
        self.main_code = "main:\n\tpush rbp\n\tmov rbp,rsp\n"
        #each function will have its dedicated slot to write to in self.functions
        self.functions = {}
        #holds the current function name(str) to write to, which is a key in 
        #self.functions
        self.cur_function = None
    def emit_bss_section(self,code):
        self.bss_section += code + '\n'

    def emit_function(self,code):
        if self.cur_function is None:
            sys.exit("Error in emit_function. cur_function is None.")
        if self.cur_function not in self.functions:
            self.functions[self.cur_function] = code + '\n'
        else:
            self.functions[self.cur_function] += code + '\n'
            
    def set_current_function(self,func_name):
        self.cur_function = func_name
    
    def emit_function_label(self,label):
        self.emit_function(f"{label}:")
    
    def emit_function_prolog(self):
        self.emit_function(f"\tpush rbp\n\tmov rbp, rsp")
    
    def emit_function_epilog(self):
        self.emit_function(f"\tpop rbp\n\tret")
                
    def emit_main_section(self,code):
        self.main_code += code + '\n'
        
    def emit_text_section(self,code):
        self.text_section += code + '\n'
    
    def add_extern(self,extern_str):
        self.externs.add(extern_str)
    
    def emit_local_label(self,string):
        self.local_labels.append(f".LC{len(self.local_labels)}: db {string},0")
    
    #given an Identifier obj, will return the corresponding asm. 
    # The result will be a value ptr, located in rax
    def compile_identifier(self,ident_obj):
        match ident_obj.typeof:
            case IdentifierType.CHAR:
                self.add_extern("make_tagged_char")
                return f"\tmov rdi, '{ident_obj.value}'\n\tcall make_tagged_char"
            case IdentifierType.STR:
                self.add_extern("allocate_str")
                self.add_extern("make_value_string")
                self.emit_local_label(ident_obj.value)
                return (f"\tmov rdi, main.LC{len(self.local_labels) - 1}\n\t" +
                f"call allocate_str\n\tmov rdi,rax\n\tcall make_value_string")
            case IdentifierType.INT:
                self.add_extern("make_tagged_int")
                return f"\tmov rdi, {ident_obj.value}\n\tcall make_tagged_int"
            case IdentifierType.FLOAT:
                self.add_extern("make_value_double")
                return (f"\tmov rax, __?float64?__(" +
                f"{ident_obj.value})\n\tmovq xmm0, rax\n\t" +
                f"call make_value_double")
            case IdentifierType.BOOLEAN:
                self.add_extern("make_tagged_bool")
                return (f"\tmov rdi, {'0x1' if ident_obj.value == '#t' else '0x0'}"
                + f"\n\tcall make_tagged_bool")
            case IdentifierType.PAIR:    
                self.add_extern("make_value_pair")
                asm_code = []
                asm_code.append(self.compile_list(ident_obj))
                asm_code.append("\tmov rdi, rsi\n\tcall make_value_pair")                
                # self.add_extern("print_list")
                # asm_code.append("\tmov rdi,rax\n\tcall print_list")
                return '\n'.join(asm_code)
            case IdentifierType.VECTOR:
                self.add_extern("make_value_vector")
                asm_code = []
                asm_code.append(self.compile_vector(ident_obj))
                asm_code.append(f"\tmov rdi,rsi\n\tmov rsi,{len(ident_obj.value)}")
                asm_code.append("\tcall make_value_vector")
                # self.add_extern("print_vector")
                # asm_code.append("\tmov rdi,rax\n\tcall print_vector")
                return '\n'.join(asm_code)
            case IdentifierType.FUNCTION:
                self.add_extern("make_value_function")
                function_name = ident_obj.value.name
                return f"\tmov rdi, ..@{function_name}\n\tcall make_value_function"
            case IdentifierType.SYMBOL:
                self.add_extern("allocate_str")
                self.add_extern("make_value_symbol")
                self.emit_local_label(f"'{ident_obj.value}'")
                return(f"\tmov rdi, main.LC{len(self.local_labels) - 1}\n\t" +
                f"call allocate_str\n\tmov rdi,rax\n\tcall make_value_symbol")
    
    # emits code for set_ith_value_x. Assumes that the first arg is set in rdi
    def set_ith_value(self,ident_obj,index):
        asm_code = []
        TYPE = ident_obj.typeof
        if TYPE == IdentifierType.CHAR:
            self.add_extern("set_ith_value_char")
            asm_code.append(f"\tmov rsi, '{ident_obj.value}'\n\tmov rdx, {index}")
            asm_code.append("call set_ith_value_char")
        elif TYPE == IdentifierType.STR:
            self.add_extern("set_ith_value_str")
            self.emit_local_label(ident_obj.value)
            asm_code.append(f"\tmov rsi, main.LC{len(self.local_labels) - 1}")
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_str")
        elif TYPE == IdentifierType.INT:
            self.add_extern("set_ith_value_int")
            asm_code.append(f"\tmov rsi, {ident_obj.value}")
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_int")
        elif TYPE == IdentifierType.FLOAT:
            self.add_extern("set_ith_value_dbl")
            asm_code.append(f"\tmov rax, __?float64?__({ident_obj.value})")
            asm_code.append("\tmovq xmm0, rax")
            asm_code.append(f"\tmov rsi, {index}\n\tcall set_ith_value_dbl")
        elif TYPE == IdentifierType.BOOLEAN:
            self.add_extern("set_ith_value_bool")
            asm_code.append(f"\tmov rsi, {'0x1' if ident_obj.value == '#t' else '0x0'}")
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_bool")
        elif TYPE == IdentifierType.PAIR:
            self.add_extern("set_ith_value_pair")
            asm_code.append("\tpush rdi") #store the first arg
            asm_code.append(self.compile_list(ident_obj))
            asm_code.append("\tpop rdi") #pop first arg
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_pair")
        elif TYPE == IdentifierType.VECTOR:
            self.add_extern("set_ith_value_vector,allocate_vector")
            #first make the vector object using the output of compile_vector,
            #then call set_ith_value_vector
            asm_code.append("\tpush rdi")
            asm_code.append(self.compile_vector(ident_obj))
            asm_code.append(f"\tmov rdi, rsi\n\tmov rsi, {len(ident_obj.value)}")
            asm_code.append("\tcall allocate_vector\n\tpop rdi\n\tmov rsi,rax")
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_vector")
        elif TYPE == IdentifierType.FUNCTION:
            self.add_extern("set_ith_value_function")
            function_name = ident_obj.value.name
            asm_code.append(f"\tmov rsi, ..@{function_name}\n\tmov rdx, {index}")
            asm_code.append("\tcall set_ith_value_function")
        elif TYPE == IdentifierType.SYMBOL:
            self.add_extern("set_ith_value_symbol")
            self.emit_local_label(f"'{ident_obj.value}'")
            asm_code.append(f"\tmov rsi, main.LC{len(self.local_labels) - 1}")
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_symbol")
        return '\n'.join(asm_code)
    
    #given that current pair addr is at the top of the stack, will get the
    #car addr and put it in rdi.(this is basically preparing the first arg of
    # set_ith_value_x in the runtime)
    def emit_car_ptr(self):
        return ("\tmov rdi, QWORD [rsp]")
    
    def emit_cdr_ptr(self):
        return ("\tmov rdi, QWORD [rsp]\n\tlea rdi, QWORD [rdi + 16]")
        

    #this function creates the pair obj required to call make_value_pair.
    #the ptr to this object will be in rsi. 
    #empty list is denoted by Identifier(IdentifierType.PAIR,[])
    #end of list is denoted by a None at the end. If no None at the end, then
    #it fell in to the DOT branch when evaluating list.
    #Note: None value can ONLY appear at the end
    def compile_list(self,ident_obj):
        asm_code = []
        last_elt_index = len(ident_obj.value) - 1
        self.add_extern("allocate_pair")
        if len(ident_obj.value) == 0: #empty list
            return "\tcall allocate_pair\n\t mov rsi,rax"
        asm_code.append("\tcall allocate_pair\n\tpush rax\n\tpush rax")
        # now build the list
        for i,ident in enumerate(ident_obj.value):
            #set car
            asm_code.append(self.emit_car_ptr())
            asm_code.append(self.set_ith_value(ident,0))
            #now set the cdr
            if i + 1 == last_elt_index:
                if ident_obj.value[last_elt_index] == None:
                    break
                else:
                    #dot notation case, set the cdr to last ident and break
                    asm_code.append(self.emit_cdr_ptr())
                    asm_code.append(
                    self.set_ith_value(ident_obj.value[last_elt_index],0))
                    break
                    
            else:
                self.add_extern("set_ith_value_pair")
                #set cdr to empty pair
                asm_code.append(self.emit_cdr_ptr())
                #perhaps the commented line below can be used instead of pushing
                # and popping since allocate_pair takes no args
                # asm_code.append("\tmov rdi, rax\n\tcall allocate_pair")
                asm_code.append("\tpush rdi\n\tcall allocate_pair")
                asm_code.append("\tpop rdi\n\tmov rsi,rax\n\tmov rdx,0")
                asm_code.append("\tcall set_ith_value_pair")
                #now advance cur pair,which is top of the stack(i.e. QWORD [rsp])                
                asm_code.append(self.emit_cdr_ptr())
                asm_code.append("\tmov rax,QWORD [rdi + 8]")
                asm_code.append("\tmov QWORD [rsp], rax")
        asm_code.append("\tpop rax\n\tpop rsi")
        return '\n'.join(asm_code)
            
    #this function creates the value obj array required for make_value_vector.
    #the ptr to this array will be in rsi. 
    def compile_vector(self,ident_obj):
        asm_code = []
        vec_len = len(ident_obj.value)
        if vec_len == 0:
            return "\tmov rsi,0x0"
        self.add_extern("make_tagged_ptr")
        asm_code.append(f"\tmov rdi, {vec_len}\n\tcall make_tagged_ptr")
        asm_code.append("\tpush rax")
        for i,ident in enumerate(ident_obj.value):
            asm_code.append("\tmov rdi, QWORD [rsp]")
            asm_code.append(self.set_ith_value(ident,i))
        asm_code.append("\tpop rsi")
        return '\n'.join(asm_code)
    
    #given ident_obj and a bool determining whether to emit to main or a label,
    #emit in the corresponding place
    def emit_identifier_to_section(self,ident_obj,is_global):
        if is_global:
            self.emit_main_section(self.compile_identifier(ident_obj))
        else:
            self.emit_function(self.compile_identifier(ident_obj))
    
    #emits asm code to corresponding section depending on the environment
    def emit_to_section(self,asm_code,is_global):
        if is_global:
            self.emit_main_section(asm_code)
        else:
            self.emit_function(asm_code)
            
    #emits_definition to corresponding place. this definitely needs to be
    #revisited to implement closures
    #offset used for local_definitions b/c they have to go on the stack
    def emit_definition(self,ident_name,is_global,offset = None):
        if is_global:
            self.emit_main_section(f"\tmov QWORD [{ident_name}],rax")
        else:
            self.emit_function(f"\tmov QWORD [rbp{offset:+}], rax")
        
    #emits identifier exp to main section. Assumes var is already in rax
    def emit_var_to_global(self,ident_name,symbol_table_arr):
        if Environment.get_offset(symbol_table_arr) is not None:
            sys.exit("Shouldnt get here. Cant emit a local var in global scope")
        self.emit_main_section(f"\tmov rax, QWORD [{ident_name}]")
    
    #emits identifier exp to function section
    def emit_var_to_local(self,ident_name,symbol_table_arr):
        offset = Environment.get_offset(symbol_table_arr)
        if offset is None: #var to emit is global
            self.emit_function(f"\tmov rax, QWORD [{ident_name}]")
        else:
            self.emit_function(f"\tmov rax, QWORD [rbp{offset:+}]")
            
            
    #for creating function definition
    def emit_register_param(self,arg_num):
        self.emit_function(
        f"\tmov QWORD [rbp-{arg_num * 8}],{LINUX_CALLING_CONVENTION[arg_num -1]}")
    
    #for setting up a function call. sets the args
    def emit_register_arg(self,arg_num,arity,env_depth,is_global):
        if is_global:
            self.emit_main_section(
            f"\tmov {LINUX_CALLING_CONVENTION[arg_num]}, " +
            f"QWORD [rbp{env_depth - ((arity - arg_num) * 8):+}]")
        else:
            self.emit_function(
            f"\tmov {LINUX_CALLING_CONVENTION[arg_num]}, " +
            f"QWORD [rbp{env_depth - ((arity - arg_num) * 8):+}]")
        
    def push_arg(self,arg_num,arity,env_depth,is_global):
        if is_global:
            # self.emit_main_section("\tpush rax")
            self.emit_main_section(
            f"\tmov QWORD [rbp{env_depth - ((arity-(arg_num - 1))*8):+}], rax")
        else:
            #self.emit_function("\tpush rax")
            self.emit_function(
            f"\tmov QWORD [rbp{env_depth - ((arity-(arg_num - 1))*8):+}], rax")
    
    #for adjusting rsp after setting up args for a function
    def subtract_rsp(self,amount,is_global):
        if is_global:
            self.emit_main_section(f"\tsub rsp, {amount}")
        else:
            self.emit_function(f"\tsub rsp, {amount}")
            
    def add_rsp(self,amount,is_global):
        if is_global:
            self.emit_main_section(f"\tadd rsp, {amount}")
        else:
            self.emit_function(f"\tadd rsp, {amount}")
            
    #to declare functions defined in runtime
    def emit_externs(self):
        self.emit_text_section("" if len(self.externs) == 0 
        else f"extern {','.join(list(self.externs))}\n")
    
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            self.emit_externs()
            outputFile.write(self.bss_section + self.text_section 
            + ''.join(self.functions.values()) + self.main_code 
            +'\n'.join(self.local_labels))