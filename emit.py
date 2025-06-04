from environment import *
from enum import Enum
import sys
# Emitter object keeps track of the generated main_code and outputs it.
#If i run into performance issues modify functions to use less concatenations or 
# to concat by putting strs in a list and calling .join
LINUX_CALLING_CONVENTION = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
#for control flow
CONDITIONS = {
    ">=" : "jge",
    ">" : "jg",
    "<" : "jl",
    "<=" : "jle",
    "=" : "je",
    "!=" : "jne"     
}
class Emitter:
    def __init__(self, fullPath):
        self.fullPath = fullPath
        self.includes = {f'%include "place_args.inc"'}
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
        
        # if not None, holds first global identifier as string. This is used to get
        #the start of bss section
        self.first_global_def = None
        self.ctrl_flow_label_count = 0 #to generate local control flow labels
        self.lambda_label_count = 0 # for generating lambda labels
        
        self.CALL_GC = True
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
        self.emit_function(f"..@{label}:")
        
    def set_first_global_def(self,ident_name):
        self.first_global_def = ident_name

    def move_stack_def_to_rax(self,offset,is_global):
        self.emit_to_section(
        f"\tmov rax, QWORD [rbp{offset:+}]",is_global)
        
    def emit_function_prolog(self):
        self.emit_function(f"\tpush rbp\n\tmov rbp, rsp")
    
    def create_new_ctrl_label(self):
        self.ctrl_flow_label_count += 1
        return f".L{self.ctrl_flow_label_count}"
    
    def create_lambda_name(self):
        self.lambda_label_count += 1
        return f"LA{self.lambda_label_count}"
    
    #emits a jump instruction depending on the condition
    def emit_conditional_jump(self,condition,is_global,label = None):
        if label is None:
            label = self.create_new_ctrl_label()
        self.emit_to_section(f"\t{CONDITIONS[condition]} {label}",is_global)
        return label
    
    def emit_jump(self,is_global, label = None):
        if label is None:
                label = self.create_new_ctrl_label()
        self.emit_to_section(f"\tjmp {label}",is_global)
        return label
    
    def emit_ctrl_label(self,is_global,label = None):
        if label is None:
            label = self.create_new_ctrl_label()
        self.emit_to_section(f"{label}:",is_global)
        return label
    
    def set_rax_false(self,is_global):
        self.emit_to_section("\tmov rax, FALSE",is_global)
    
    def set_rax_true(self,is_global):
        self.emit_to_section("\tmov rax, TRUE",is_global)
        
    #given an offset, will set rax to whats on the stack at that offset
    def set_rax_to_local_def(self,is_global,offset):
        self.emit_to_section(
        f"\tmov rax, QWORD [rbp{offset:+}];setting rax to be self closure",is_global)
    
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
    def compile_identifier(self,ident_obj,cur_environment):
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
                if len(ident_obj.value) == 0:
                    self.add_extern("make_empty_list")
                    asm_code.append("\tcall make_empty_list")
                    return '\n'.join(asm_code)
                asm_code.append(self.compile_list(ident_obj,cur_environment))
                asm_code.append("\tmov rdi, rsi\n\tcall make_value_pair")                
                # self.add_extern("print_list")
                # asm_code.append("\tmov rdi,rax\n\tcall print_list")
                return '\n'.join(asm_code)
            case IdentifierType.VECTOR:
                self.add_extern("make_value_vector")
                asm_code = []
                asm_code.append(self.compile_vector(ident_obj,cur_environment))
                asm_code.append(f"\tmov rdi,rsi\n\tmov rsi,{len(ident_obj.value)}")
                asm_code.append("\tcall make_value_vector")
                # self.add_extern("print_vector")
                # asm_code.append("\tmov rdi,rax\n\tcall print_vector")
                return '\n'.join(asm_code)
            case IdentifierType.FUNCTION:
                if ident_obj.value.name in BUILTINS:
                    self.add_extern(ident_obj.value.name)
                    return f"\tmov rax, {ident_obj.value.name}"
                asm_code = []
                self.add_extern("allocate_function")
                self.add_extern("make_value_function")
                func_obj = ident_obj.value
                asm_code.append(f"\tmov rdi, ..@{func_obj.name}")
                asm_code.append(f"\tmov rsi, {'1' if func_obj.is_variadic else '0'}")
                asm_code.append(f"\tmov rdx, {func_obj.arity}\n\tcall allocate_function")
                asm_code.append(f"\tmov rdi, rax\n\tcall make_value_function")
                return '\n'.join(asm_code)
            case IdentifierType.CLOSURE:
                #first compile the function, then the closure.
                asm_code = []
                asm_code.append(self.compile_identifier(ident_obj.value,cur_environment))
                self.add_extern("allocate_closure")
                self.add_extern("make_value_closure")
                asm_code.append("\tmov rdi, rax\n\tcall allocate_closure")
                asm_code.append("\tmov rdi, rax\n\tcall make_value_closure")
                return '\n'.join(asm_code)
            case IdentifierType.SYMBOL:
                self.add_extern("allocate_str")
                self.add_extern("make_value_symbol")
                self.emit_local_label(f"'{ident_obj.value}'")
                return(f"\tmov rdi, main.LC{len(self.local_labels) - 1}\n\t" +
                f"call allocate_str\n\tmov rdi,rax\n\tcall make_value_symbol")
            case _:
                sys.exit(
                "Error, cant compile an identifier since its type is not known.")    
    # emits code for set_ith_value_x. Assumes that the first arg is set in rdi
    def set_ith_value(self,ident_obj,index,cur_environment):
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
            if len(ident_obj.value) == 0:
                self.add_extern("set_ith_value_empty_list")
                asm_code.append(f"\tmov rsi, {index}")
                asm_code.append("\tcall set_ith_value_empty_list")
            else:
                self.add_extern("set_ith_value_pair")
                asm_code.append("\tpush rdi") #store the first arg
                asm_code.append(self.compile_list(ident_obj,cur_environment))
                asm_code.append("\tpop rdi") #pop first arg
                asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_pair")
        elif TYPE == IdentifierType.VECTOR:
            self.add_extern("set_ith_value_vector,allocate_vector")
            #first make the vector object using the output of compile_vector,
            #then call set_ith_value_vector
            asm_code.append("\tpush rdi")
            asm_code.append(self.compile_vector(ident_obj,cur_environment))
            asm_code.append(f"\tmov rdi, rsi\n\tmov rsi, {len(ident_obj.value)}")
            asm_code.append("\tcall allocate_vector\n\tpop rdi\n\tmov rsi, rax")
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_vector")
        elif TYPE == IdentifierType.FUNCTION:
            self.add_extern("set_ith_value_function")
            func_obj = ident_obj.value
            if func_obj.name in BUILTINS:
                self.add_extern(func_obj.name)
                asm_code.append(f"\tmov rax, {func_obj.name}") 
                asm_code.append(f"\tadd rax,8")
                asm_code.append(f"\tmov rsi, QWORD[rax]\n\tmov rdx, {index}")
                asm_code.append("\tcall set_ith_value_function")
            else:
                self.add_extern("allocate_function")
                asm_code.append("\tpush rdi")
                asm_code.append(f"\tmov rdi, ..@{func_obj.name}")
                asm_code.append(f"\tmov rsi, {'1' if func_obj.is_variadic else '0'}")
                asm_code.append(f"\tmov rdx, {func_obj.arity}\n\tcall allocate_function")
                asm_code.append("\tpop rdi")
                asm_code.append(f"\t mov rsi, rax\n\tmov rdx, {index}")
                asm_code.append(f"\tcall set_ith_value_function")
        elif TYPE == IdentifierType.CLOSURE:
            #first make closure obj. to do this need to make function value type
            self.add_extern("allocate_closure")
            self.add_extern("set_ith_value_closure")
            asm_code.append("\tpush rdi")
            asm_code.append(self.compile_identifier(ident_obj.value,cur_environment))
            asm_code.append("\tmov rdi, rax\n\tcall allocate_closure")
            asm_code.append("\tpop rdi")
            asm_code.append("\tmov rsi, rax")
            asm_code.append(f"\tmov rdx, {index}")
            asm_code.append("\tcall set_ith_value_closure")
                
        elif TYPE == IdentifierType.SYMBOL:
            self.add_extern("set_ith_value_symbol")
            self.emit_local_label(f"'{ident_obj.value}'")
            asm_code.append(f"\tmov rsi, main.LC{len(self.local_labels) - 1}")
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_symbol")
        elif TYPE == IdentifierType.PARAM:
            self.add_extern("set_ith_value_unknown")
            definition = cur_environment.find_definition(ident_obj.value)[0]
            offset = Environment().get_offset(definition)
            asm_code.append(f"\tmov rsi, QWORD [rbp{offset:+}]")
            asm_code.append(f"\tmov rdx, {index}\n\tcall set_ith_value_unknown")
        else:
            sys.exit(
            f"Error setting ith value, {ident_obj.typeof} not supported")
        return '\n'.join(asm_code)
    
    #given that current pair addr is at the top of the stack, will get the
    #car addr and put it in rdi.(this is basically preparing the first arg of
    # set_ith_value_x in the runtime)
    def emit_car_ptr(self):
        return ("\tmov rdi, QWORD [rsp]")
    
    def emit_cdr_ptr(self):
        return ("\tmov rdi, QWORD [rsp]\n\tadd rdi, 16")
        

    #this function creates the pair obj required to call make_value_pair.
    #the ptr to this object will be in rsi. 
    #empty list is denoted by Identifier(IdentifierType.PAIR,[])
    #end of list is denoted by a None at the end. If no None at the end, then
    #it fell in to the DOT branch when evaluating list.
    #Note: None value can ONLY appear at the end
    def compile_list(self,ident_obj,cur_environment):
        asm_code = []
        last_elt_index = len(ident_obj.value) - 1
        self.add_extern("allocate_pair")
        if len(ident_obj.value) == 0: #empty list
            # self.add_extern("make_empty_list")
            return "\tcall allocate_pair\n\tmov rsi,rax"
            # return "\tcall make_empty_list\n\tmov rsi,rax"
        asm_code.append("\tcall allocate_pair\n\tpush rax\n\tpush rax")
        # now build the list
        for i,ident in enumerate(ident_obj.value):
            #set car
            asm_code.append(self.emit_car_ptr())
            asm_code.append(self.set_ith_value(ident,0,cur_environment))
            #now set the cdr
            if i + 1 == last_elt_index:
                if ident_obj.value[last_elt_index] is None:
                    break
                else:
                    #dot notation case, set the cdr to last ident and break
                    asm_code.append(self.emit_cdr_ptr())
                    asm_code.append(
                    self.set_ith_value(
                    ident_obj.value[last_elt_index],0,cur_environment))
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
    def compile_vector(self,ident_obj,cur_environment):
        asm_code = []
        vec_len = len(ident_obj.value)
        if vec_len == 0:
            return "\tmov rsi,0x0"
        self.add_extern("make_tagged_ptr")
        asm_code.append(f"\tmov rdi, {vec_len}\n\tcall make_tagged_ptr")
        asm_code.append("\tpush rax")
        for i,ident in enumerate(ident_obj.value):
            asm_code.append("\tmov rdi, QWORD [rsp]")
            asm_code.append(self.set_ith_value(ident,i,cur_environment))
        asm_code.append("\tpop rsi")
        return '\n'.join(asm_code)
    
    #performs runtime checks against a Value object(the one saved by save_rax) 
    # by first calling check_if_callable, which checks if object is callable 
    # (i.e. function/closure). it then modifies the saved value obj to guarantee
    #that theres a function obj there.
    
    #Then call check_param_function_call, which checks for arity/variadic in the 
    # runtime. the varargs will be in rax if variadic func, else NULL will be there
    def emit_function_check(self,cur_environment,param_offset,arg_count):
        self.add_extern("check_if_callable")
        self.add_extern("check_param_function_call")
        first_arg_offset = cur_environment.depth - 8*arg_count
        is_global = cur_environment.is_global()
        env_depth = abs(cur_environment.depth)
        asm_code = []
        asm_code.append(f"\tmov rdi, QWORD [rbp{param_offset:+}]")
        asm_code.append("\tcall check_if_callable")
        #now set value type saved:
        asm_code.append(f"\tmov QWORD [rbp{param_offset:+}], rax")
        #now call check_param_function_call:
        asm_code.append(f"\tmov rdi, QWORD [rbp{param_offset:+}]")
        asm_code.append(f"\tlea rsi, QWORD [rbp{first_arg_offset:+}]")
        #asm_code.append(f"\tlea rax, QWORD [rbp{first_arg_offset:+}]")
        #asm_code.append("\tmov rsi,rax")
        asm_code.append(f"\tmov rdx, {arg_count}")
        asm_code.append("\tcall check_param_function_call")
        self.subtract_rsp(env_depth + 8*arg_count,is_global)
        self.emit_to_section('\n'.join(asm_code),is_global)
        self.add_rsp(env_depth + 8*arg_count,is_global)
    
    #checks if result of check_param_function_call(which is in rax) is null or not.    
    def emit_zero_check(self,is_global):
        self.emit_to_section("\tcmp rax, 0",is_global)
    
    #checks if rax is false the false object (i.e. the value 2)
    def emit_false_check(self, is_global):
        self.emit_to_section("\tcmp rax, FALSE",is_global)
    
    #be careful with this function
    #saves rax to stack,not tracked by Environment's symbol table but the 
    # environment depth accounts for this value on the stack
    #its purpose is to temporarily store rax for function calling
    #it changes the depth of the environment which has to be manually undone
    #by calling undo_save_rax
    def save_rax(self,cur_environment):
        cur_environment.depth -= 8
        env_depth = cur_environment.depth
        is_global = cur_environment.is_global()
        self.emit_to_section(
        f"\tmov QWORD [rbp{env_depth:+}], rax ;saved rax to stack",is_global)

    # with the depth increased, in the environment's eyes, the last
    #8 bytes of the stack dont belong to it anymore. 
    def undo_save_rax(self,cur_environment):
        cur_environment.depth += 8
    
    #given a stack offset of where the closure object is stored, edits the stack
    #location so that the function value ptr takes its place
    def get_function_from_closure(self,offset,is_global):
        asm_code = []
        asm_code.append(f"\tmov rax, QWORD [rbp{offset:+}]")
        asm_code.append("\tmov rax, QWORD [rax + 8]")
        asm_code.append("\tmov rax, QWORD [rax]")
        asm_code.append(f"\tmov QWORD [rbp{offset:+}], rax")
        self.emit_to_section('\n'.join(asm_code),is_global)
    
    #given that a closure obj is in rax, edits rax to have so that the function obj
    #is there
    def get_function_from_closure_rax(self,is_global):
        asm_code = []
        asm_code.append("\tmov rax, QWORD [rax + 8]")
        asm_code.append("\tmov rax, QWORD [rax]")
        self.emit_to_section('\n'.join(asm_code),is_global)
    
    
    def emit_is_closure(self,env_depth,callable_obj_depth,is_global):
        self.add_extern("is_closure")
        self.subtract_rsp(abs(env_depth),is_global)
        self.emit_to_section(
        f"\tmov rdi, QWORD [rbp{callable_obj_depth:+}]\n\tcall is_closure",is_global)
        self.add_rsp(abs(env_depth),is_global)

        
    #calls add_upvalue. cur_environment is the environment that will do the writing
    #to the child
    def emit_add_upvalue(
    self,cur_environment,inner_function_offset,upvalue_offset,nest_count):
        self.add_extern("add_upvalue")
        env_depth = abs(cur_environment.depth)
        is_global = cur_environment.is_global()
        asm_code = []
        self.emit_function(";adding upvalue")
        asm_code.append(f"\tmov rdi, QWORD [rbp{inner_function_offset:+}]")
        asm_code.append(f"\tmov rsi, QWORD [rbp{upvalue_offset:+}]")
        asm_code.append(f"\tmov rdx, {upvalue_offset:+}")
        asm_code.append(f"\tmov rcx, {nest_count}")
        asm_code.append("\tcall add_upvalue")
        self.subtract_rsp(env_depth,is_global)
        self.emit_function('\n'.join(asm_code))
        self.add_rsp(env_depth,is_global)
        self.emit_function(";done adding upvalue")
    
    #calls add_upvalue to add an upvalue to a lambda/let. Since these arent
    #definitions rdi is not retrieved from the stack like in emit_add_upvalue
    def emit_add_upvalue_anonymous(
    self,cur_environment,upvalue_offset,nest_count):
        self.add_extern("add_upvalue")
        env_depth = abs(cur_environment.depth)
        is_global = cur_environment.is_global()
        asm_code = []
        self.emit_function(";adding upvalue anonymous")
        asm_code.append(f"\tmov rdi, rax")
        asm_code.append(f"\tmov rsi, QWORD [rbp{upvalue_offset:+}]")
        asm_code.append(f"\tmov rdx, {upvalue_offset:+}")
        asm_code.append(f"\tmov rcx, {nest_count}")
        asm_code.append("\tcall add_upvalue")
        self.subtract_rsp(env_depth,is_global)
        self.emit_function('\n'.join(asm_code))
        self.add_rsp(env_depth,is_global)
        self.emit_function(";done adding upvalue anonymous")
    
    def emit_add_upvalue_nonlocal(
    self,cur_environment,inner_function_offset,upvalue_offset,nest_count):
        self.add_extern("add_upvalue_nonlocal")
        env_depth = abs(cur_environment.depth)
        is_global = cur_environment.is_global()
        asm_code = []
        self.emit_function(";adding upvalue nonlocal")
        asm_code.append(f"\tmov rdi, QWORD [rbp{inner_function_offset}]")
        asm_code.append("\tmov rsi, QWORD [rbp-8]")
        asm_code.append(f"\tmov rdx, {upvalue_offset}")
        asm_code.append(f"\tmov rcx, {nest_count}")
        asm_code.append("\tcall add_upvalue_nonlocal")
        self.subtract_rsp(env_depth,is_global)
        self.emit_function('\n'.join(asm_code))
        self.add_rsp(env_depth,is_global)
        self.emit_function(";done adding upvalue nonlocal")
    
    def emit_add_upvalue_nonlocal_anonymous(
    self,cur_environment,upvalue_offset,nest_count):
        self.add_extern("add_upvalue_nonlocal")
        env_depth = abs(cur_environment.depth)
        is_global = cur_environment.is_global()
        asm_code = []
        self.emit_function(";adding upvalue nonlocal anonymous")
        asm_code.append(f"\tmov rdi, rax")
        asm_code.append("\tmov rsi, QWORD [rbp-8]")
        asm_code.append(f"\tmov rdx, {upvalue_offset}")
        asm_code.append(f"\tmov rcx, {nest_count}")
        asm_code.append("\tcall add_upvalue_nonlocal")
        self.subtract_rsp(env_depth,is_global)
        self.emit_function('\n'.join(asm_code))
        self.add_rsp(env_depth,is_global)
        self.emit_function(";done adding upvalue nonlocal anonymous")
        
    def emit_move_local_to_heap(self,upvalue_offset,cur_environment):
        self.add_extern("move_local_to_heap")
        env_depth = abs(cur_environment.depth)
        is_global = cur_environment.is_global()
        self.subtract_rsp(env_depth,is_global)
        self.emit_function(f"\tmov rdi, QWORD [rbp{upvalue_offset:+}]")
        self.emit_function("\tcall move_local_to_heap")
        self.add_rsp(env_depth,is_global)
        self.emit_function(f"\tmov QWORD [rbp{upvalue_offset:+}], rax")

    #calls get_upvalue the closure obj will always be in position rbp - 8.
    def emit_get_upvalue(self,env_depth,offset,nest_count,is_global):
        asm_code = []
        self.emit_to_section(";upvalue stuff",is_global)
        self.add_extern("get_upvalue")
        self.subtract_rsp(abs(env_depth),is_global)
        asm_code.append(
        f"\tmov rdi, QWORD [rbp-8]\n\tmov rsi, {offset}")
        asm_code.append(f"\tmov rdx, {nest_count}\n\tcall get_upvalue")
        self.emit_to_section('\n'.join(asm_code),is_global)
        self.add_rsp(abs(env_depth),is_global)
    
    def emit_setexclam_upvalue(self,offset,nest_count,env_depth,is_global):
        self.add_extern("setexclam_upvalue")
        asm_code = []
        asm_code.append("\tmov rdi, QWORD [rbp-8]")
        asm_code.append("\tmov rsi, rax")
        asm_code.append(f"\tmov rdx, {offset}")
        asm_code.append(f"\tmov rcx, {nest_count}")
        asm_code.append("\tcall setexclam_upvalue")
        self.subtract_rsp(abs(env_depth),is_global)
        self.emit_to_section('\n'.join(asm_code),is_global)
        self.add_rsp(abs(env_depth),is_global)
    
    #used in set! where definition being isnt an upvalue, i.e. its local or global
    def set_definition(self,offset,ident_name,env_depth,is_global):
        self.add_extern("setexclam")
        if offset is None:
            # self.emit_to_section(
            # f"\tmov QWORD [{ident_name}], rax ;set! global",is_global)
            #global case
            asm_code = []
            asm_code.append(f"\tmov rdi, QWORD [{ident_name}]")
            asm_code.append("\tmov rsi, rax")
            asm_code.append("\tcall setexclam")
            self.subtract_rsp(abs(env_depth),is_global)
            self.emit_to_section("\n".join(asm_code),is_global)
            self.add_rsp(abs(env_depth),is_global)
            self.emit_to_section(
            f"\tmov QWORD [{ident_name}], rax ;set! global",is_global)
        else:
            # self.emit_to_section(
            # f"\tmov QWORD [rbp{offset:+}], rax ;set! local",is_global)
            asm_code = []
            asm_code.append(f"\tmov rdi, QWORD [rbp{offset:+}]")
            asm_code.append("\tmov rsi, rax")
            asm_code.append("\tcall setexclam")
            self.subtract_rsp(abs(env_depth),is_global)
            self.emit_to_section("\n".join(asm_code),is_global)
            self.add_rsp(abs(env_depth),is_global)
            self.emit_to_section(
            f"\tmov QWORD [rbp{offset:+}], rax ;set! local",is_global)
            

    #used to satisfy criteria of macro in place_args. rbx holds arity and 
    # r10 holds min_args
    def get_arity_in_runtime(self,param_offset):
        asm_code = []
        asm_code.append(f"\tmov rbx, QWORD [rbp{param_offset:+}]")
        asm_code.append(f"\tmov rbx, QWORD [rbx + 8]")
        asm_code.append("\tmov ebx, DWORD [rbx + 12]")
        asm_code.append("\tmov r10, rbx\n\tdec r10")
        return '\n'.join(asm_code)
    
    #emits code for variadic call. assumes the vararg array is in rax.
    #calls macro in place_args.inc to place args.
    
    #The macro requires the following:
    #the function arity in rbx,min_args in r10,env_depth in first arg,
    #r11 is seventh arg offset, r12 is preserved for counting args, 
    # which has to be initialized to 0
    #and r13 holds the old value of r15
    def emit_param_variadic_call(self,label,param_offset,env_depth,is_global):
        asm_code = []
        asm_code.append(f"{label}:")
        asm_code.append(self.get_arity_in_runtime(param_offset))
        asm_code.append("\txor r12, r12")
        #now r11
        asm_code.append("\tmov r11,rbx\n\tsub r11, 6\n\timul r11, 8")
        asm_code.append(f"\tadd r11, {abs(env_depth)}\n\tand r11, 0xf")
        env_depth_aligned = abs(env_depth)
        if env_depth_aligned % 16 != 0:
            env_depth_aligned += 8
        asm_code.append(
        f"\tplace_args {abs(env_depth)}, {abs(param_offset)}, {env_depth_aligned}")
        self.emit_to_section('\n'.join(asm_code),is_global)
        
    #to be used in variadic_function_call. In this case min_args is known at
    #compile time
    def emit_make_arg_list(self,min_args,arity,arg_count,old_env_depth,is_global):
        self.add_extern("make_arg_list_min_args")
        cur_env_depth = abs(old_env_depth - (8 * arg_count))
        self.subtract_rsp(cur_env_depth,is_global)
        asm_code = []
        asm_code.append(f"\tmov rdi, {min_args}")
        asm_code.append(f"\tlea rsi, QWORD [rbp-{cur_env_depth}]")
        asm_code.append(f"\tmov rdx, {arg_count}")
        asm_code.append("\tcall make_arg_list_min_args")
        #now place varargs list:
        asm_code.append(f"\tmov QWORD [rbp{old_env_depth - (8 * arity):+}],rax")
        self.emit_to_section('\n'.join(asm_code),is_global)
        self.add_rsp(cur_env_depth,is_global)
    
    def inc_global_var_count(self,cur_environment):
        is_global = cur_environment.is_global()
        self.add_extern("global_var_count")
        self.emit_to_section("\tinc QWORD [global_var_count]",is_global)
        
        
    
    #given ident_obj and the current environment, emit in the corresponding place
    def emit_identifier_to_section(self,ident_obj,cur_environment):
        is_global = cur_environment.is_global()
        env_depth = abs(cur_environment.depth)
        if self.CALL_GC:    
            #call collect_garbage
            self.subtract_rsp(env_depth,is_global)
            self.add_extern("collect_garbage")
            self.add_extern("global_var_count")
            asm_code = []
            asm_code.append(
            f"\tmov rdi, QWORD {0 if self.first_global_def is None else self.first_global_def}")
            asm_code.append("\tmov rsi, QWORD [global_var_count]")
            asm_code.append(f"\tmov rdx, {0 if is_global else "QWORD [rbp-8]"}")
            asm_code.append("\tcall collect_garbage")
            self.emit_to_section('\n'.join(asm_code),is_global)
            self.add_rsp(env_depth,is_global)
        
        self.subtract_rsp(env_depth,is_global)
        self.emit_to_section(
        self.compile_identifier(ident_obj,cur_environment),is_global)
        self.add_rsp(env_depth,is_global)
    
    #emits asm code to corresponding section depending on the environment
    def emit_to_section(self,asm_code,is_global):
        if is_global:
            self.emit_main_section(asm_code)
        else:
            self.emit_function(asm_code)
            
    #emits_definition to corresponding place.
    def emit_definition(self,ident_name,cur_environment,offset = None):
        is_global = cur_environment.is_global()
        env_depth = cur_environment.depth
        if is_global:
            if offset is not None:
                sys.exit(
                f"Error emitting definition {ident_name}. emit_definition in " + 
                "global scope doesn't use an offset.")
            self.emit_main_section(f"\tmov QWORD [{ident_name}],rax")
        elif offset is not None:
            self.emit_function(f"\tmov QWORD [rbp{offset:+}], rax")
            self.subtract_rsp(abs(env_depth),is_global)
            self.emit_push_live_local(is_global)
            self.add_rsp(abs(env_depth),is_global)
        else:
            sys.exit("Error, must pass an offset when emitting local definition.")
        
    #emits identifier exp to main section. Assumes var is already in rax
    def emit_var_to_global(self,ident_name,symbol_table_arr):
        if Environment.get_offset(symbol_table_arr) is not None:
            sys.exit("Shouldnt get here. Cant emit a local var in global scope")
        self.emit_main_section(f"\tmov rax, QWORD [{ident_name}]")
    
    #emits identifier exp to function section
    def emit_var_to_local(self,ident_name,offset,ident_obj,is_captured,env_depth,is_global):
        if offset is None: #var to emit is global
            self.emit_function(f"\tmov rax, QWORD [{ident_name}]")
            return
        
        self.emit_function(f"\tmov rax, QWORD [rbp{offset:+}]")
        if is_captured:
            if ident_obj.is_type_known():
                if ident_obj.is_non_ptr_type():
                    #emit asm to turn to non ptr type
                    self.emit_function(
                    "\tmov rax,QWORD [rax + 8] ;turn back to val type")
            else:
                #have to do runtime check since its param or function call.
                #leave result in rax
                self.add_extern("turn_to_non_ptr_type")
                self.subtract_rsp(abs(env_depth),is_global)
                self.emit_function("\tmov rdi, rax\n\tcall turn_to_non_ptr_type")
                self.add_rsp(abs(env_depth),is_global)
                
    #for creating function definition
    def emit_register_param(self,arg_num):
        self.emit_function(
        f"\tmov QWORD [rbp-{arg_num * 8}],{LINUX_CALLING_CONVENTION[arg_num -1]}")
    
    #for setting up a function call. sets the args. If arity is None, an arg
    # is being used as function object. Since arity is not yet known the
    # calculation is different
    def emit_register_arg(self,arg_num,env_depth,is_global,arity = None):
        if arity is None:
            self.emit_to_section(
            f"\tmov {LINUX_CALLING_CONVENTION[arg_num]}," + 
            f"QWORD [rbp{env_depth - (8*(arg_num + 1)):+}]",is_global)
            return
        self.emit_to_section(
        f"\tmov {LINUX_CALLING_CONVENTION[arg_num]}, " +
        f"QWORD [rbp{env_depth - ((arity - arg_num) * 8):+}]",is_global)
    
    #for putting args 7 and further to the stack
    #rbx used for temporary storage
    def emit_arg_to_stack(self,arg_num,env_depth,is_global,arity,align_needed = False):
        
        self.emit_to_section(
        f"\tmov rbx, QWORD [rbp{env_depth - (8*(arg_num + 1)):+}]",is_global)
        if align_needed:
            env_depth -= 8
        self.emit_to_section(
        f"\tmov QWORD [rbp{env_depth - ((arity - arg_num)*8)}],rbx",is_global)
        
    
    #push the arg to the stack so that its stored while evaluating each arg
    #if arity is None you are pushing args for arg thats being used a function
    def push_arg(self,arg_num,cur_env,env_depth,is_global,arity = None):
        if arity is None:
            offset = env_depth - (8*arg_num)
            self.emit_to_section(
            f"\tmov QWORD [rbp{offset:+}],rax",is_global)
            cur_env.save_arg_offset(offset)
            return offset
        #since arity is known, push arguments backwards
        offset = env_depth - ((arity-(arg_num - 1))*8)
        self.emit_to_section(
        f"\tmov QWORD [rbp{offset:+}], rax",is_global)
        cur_env.save_arg_offset(offset)
        return offset
    
    def emit_pass_by_value(self,env_depth,is_global):
        self.add_extern("pass_by_value")
        asm_code = []
        asm_code.append("\tmov rdi, rax\n\tcall pass_by_value")
        self.subtract_rsp(abs(env_depth),is_global)
        self.emit_to_section('\n'.join(asm_code),is_global)
        self.add_rsp(abs(env_depth),is_global)
    
    #for adjusting rsp after setting up args for a function. accounts for stack alignment
    def subtract_rsp(self,amount,is_global):
        if amount == 0:
            print("Subtracting rsp with 0 amount")
            return
        #accounting for stack alignment:
        bytes_misaligned = amount % 16
        if bytes_misaligned == 0:
            self.emit_to_section(f"\tsub rsp, {amount} ;aligned",is_global)
        else:
            self.emit_to_section(
            f"\tsub rsp, {amount + bytes_misaligned} ;aligned",is_global)
        
    
    def add_rsp(self,amount,is_global):
        if amount == 0:
            print("Adding rsp with 0 amount")
            return
        #accounting for stack alignment:
        bytes_misaligned = amount % 16
        if bytes_misaligned == 0:    
            self.emit_to_section(f"\tadd rsp, {amount} ;aligned",is_global)
        else:
            self.emit_to_section(
            f"\tadd rsp, {amount + bytes_misaligned} ;aligned",is_global)
    
    #these two methods subtract/add rsp without considering stack alignment
    def subtract_rsp_absolute(self,amount,is_global):
        if amount == 0:
            print("Adding rsp with 0 amount")
            return
        self.emit_to_section(f"\tsub rsp, {amount} ;not aligned",is_global)
    
    def add_rsp_absolute(self,amount,is_global):
        if amount == 0:
            print("Adding rsp with 0 amount")
            return
        self.emit_to_section(f"\tadd rsp, {amount} ;not aligned",is_global)
    
    #given arity, subtract rsp so it points to the correct spot:
    def subtract_rsp_given_arity(self,function_arity,env_depth,is_global,align_needed = False):
        if function_arity > 6:
            if align_needed:
                env_depth -= 8
            self.subtract_rsp_absolute(
            abs(env_depth - (function_arity - 6)*8),is_global)
        else:
            self.subtract_rsp(abs(env_depth),is_global)
            
    #adds back to the rsp after a function call. undoes subtract_rsp_given_arity
    def add_rsp_given_arity(self,function_arity,env_depth,is_global,align_needed = False):
        if function_arity > 6:
            if align_needed:
                env_depth -= 8
            self.add_rsp_absolute(
            abs(env_depth - (function_arity - 6)*8),is_global)
        else:
            self.add_rsp(abs(env_depth),is_global)
    
    #emits asm for evaluating a builtin closure(just the name as an exp)
    def emit_builtin_closure(self,builtin_name,is_global):
        self.emit_to_section(f"\tmov rax, {builtin_name}",is_global)
    
    #check if value in rax is a value object of type function
    def emit_is_function(self,cur_environment):
        is_global = cur_environment.is_global()
        env_depth = abs(cur_environment.depth)
        self.add_extern("is_function")
        self.subtract_rsp(env_depth,is_global)
        self.emit_to_section(
        f"\tmov rdi,rax\n\tcall is_function",is_global)
        self.add_rsp(env_depth,is_global)

    #emits asm for calling builtin function
    def emit_builtin_call(self,builtin_name,is_global):
        self.add_extern(builtin_name)
        self.emit_to_section(
        f"\tmov rax, {builtin_name}\n\t" + 
        f"add rax, 8\n\tmov rax, QWORD[rax]\n\tcall QWORD [rax]",is_global)
    
    #calls function (function obj must be on the stack) given its offset on the 
    #stack
    def emit_function_call(self,func_offset,is_global):
        self.emit_to_section(f"\tmov rax,QWORD[rbp{func_offset:+}]\n\t" + 
        f"add rax, 8\n\tmov rax, QWORD [rax]\n\tcall QWORD [rax]",is_global)
    
    #call function given the function object is already in rax.
    def emit_function_call_in_rax(self,is_global):
        self.emit_to_section( 
        f"\tadd rax, 8\n\tmov rax, QWORD [rax]\n\tcall QWORD [rax]",is_global)
    
    #if an offset is given, will first move what is in that offset to rax and then
    #push to live_local
    def emit_push_live_local(self,is_global,offset = None):
        # if is_global:
        #     sys.exit("cant push_live_local in global scope.")
        self.add_extern("push_to_live_local")
        if offset is not None:
            self.emit_to_section(f"\tmov rax, QWORD [rbp{offset:+}]",is_global)
        self.emit_to_section("\tmov rdi, rax\n\tcall push_to_live_local",is_global)
    
    
    def push_args_to_live_locals(self,arity,cur_environment):
        is_global = cur_environment.is_global()
        env_depth = cur_environment.depth
        self.emit_to_section(";adding args to live_locals", is_global)
        self.subtract_rsp(abs(env_depth),is_global)
        for i in range(arity):
            if i > 5:
                #for args 7 and on, that are on the other side of the stack
                self.emit_to_section(f"\tmov rax, QWORD [rbp+{(i - 4)*8}]",is_global)
            else:
                self.emit_to_section(f"\tmov rax, QWORD [rbp{-(i + 1)*8}]",is_global)
            self.emit_push_live_local(is_global)
        self.add_rsp(abs(env_depth),is_global)
        self.emit_to_section(";done adding args to live_locals", is_global)
    
    #pops_from live_locals. if restore_rax is true, will save rax and restore it
    #to what it was before the call to pop_n_locals. restore_rax should always be
    #true when exiting function calls
    def pop_live_locals(self,cur_environment,amount_to_pop,restore_rax = True):
        is_global = cur_environment.is_global()
        env_depth = cur_environment.depth
        self.add_extern("pop_n_locals")
        if restore_rax:
            #since at this point the function finished executing so rbp-8 can be overwritten
            self.emit_to_section("\tmov QWORD [rbp - 8],rax; store result",is_global)
        self.subtract_rsp(abs(env_depth),is_global)
        self.emit_to_section(f"\tmov rdi, {amount_to_pop}\n\tcall pop_n_locals",is_global)
        self.add_rsp(abs(env_depth),is_global)
        if restore_rax:
            self.emit_to_section("\tmov rax,QWORD [rbp - 8]; restore result",is_global)
        
    #to declare functions defined in runtime
    def emit_externs(self):
        self.emit_text_section("" if len(self.externs) == 0 
        else f"extern {','.join(list(self.externs))}\n")
    
    def get_includes(self):
        return '\n'.join(self.includes) + '\n'
    def writeFile(self):
        with open(self.fullPath, 'w') as outputFile:
            self.emit_externs()
            outputFile.write(self.get_includes() + 
            self.bss_section + self.text_section 
            + ''.join(self.functions.values()) + self.main_code 
            +'\n'.join(self.local_labels))