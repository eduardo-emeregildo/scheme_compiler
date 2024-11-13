from abc import ABC,abstractmethod
from environment import *
from scheme_list import *
import sys
#these clases will handle the generation of asm code for various types of variables 
#depending on scope.
#there is one generator class per IdentifierType

#if procedure has more than six args, they'll be on the stack
LINUX_CALLING_CONVENTION = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
LINUX_FLOATING_POINT_CONVENTION = ["xmm0","xmm1","xmm2","xmm3","xmm4","xmm5",
"xmm6","xmm7"
]

class Generator(ABC):
    @abstractmethod
    def generate_global_var(self):
        pass
    #this method might need an offset arg, since local vars will be on the stack
    @abstractmethod
    def generate_local_var(self):
        pass
        
    def set_ident_name(self,ident_name):
        self.ident_name = ident_name

    def set_offset(self,offset):
        self.offset = offset

#If i need more complex creation of objects then I can have subclasses of GeneratorFactory, i.e. IntGenFactory etc.
class GeneratorFactory():
    def create_generator(self,ident_obj,offset = 0,ident_name=""):
        ident_type = ident_obj.typeof
        gen_obj = None
        if ident_type == IdentifierType.INT:
            gen_obj = IntGenerator(ident_obj,offset,ident_name)
        elif ident_type == IdentifierType.FLOAT:
            gen_obj = FloatGenerator(ident_obj,offset,ident_name)
        elif ident_type == IdentifierType.CHAR:
            gen_obj = CharGenerator(ident_obj,offset,ident_name)
        elif ident_type == IdentifierType.STR:
            gen_obj = StringGenerator(ident_obj,offset,ident_name)
        elif ident_type == IdentifierType.BOOLEAN:
            gen_obj = BooleanGenerator(ident_obj,offset,ident_name)
        elif ident_type == IdentifierType.SYMBOL:
            gen_obj = SymbolGenerator(ident_obj,offset,ident_name)
        elif ident_type == IdentifierType.PAIR:
            gen_obj = PairGenerator(ident_obj,offset,ident_name)
        elif ident_type == IdentifierType.VECTOR:
            gen_obj = VectorGenerator(ident_obj,offset,ident_name)
        elif ident_type == IdentifierType.FUNCTION:
            gen_obj = FunctionGenerator(ident_obj,offset,ident_name)
        return gen_obj
            
class IntGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdq {self.ident_obj.value}"

    def generate_local_var(self):
        return "generating local int var(stack)"
        
class FloatGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
        
    def generate_global_var(self):
        return f"\tdq {self.ident_obj.value}"

    def generate_local_var(self):
        return "generating local float var(stack)"

class CharGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdb '{self.ident_obj.value[-1]}'"

    def generate_local_var(self):
        return "generating local char var(stack)"
        
class StringGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdb {self.ident_obj.value}, 0"

    def generate_local_var(self):
        return "generating local string var(stack)"

class BooleanGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdb {'1' if self.ident_obj.value =='#t' else '0'}"

    def generate_local_var(self):
        return "generating local boolean var(stack)"

class SymbolGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdb '{self.ident_obj.value}', 0"

    def generate_local_var(self):
        return "generating local symbol var(stack)"

class PairGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        asm_instructions = []
        pair_obj = self.ident_obj.value
        factory = GeneratorFactory()
        if pair_obj.is_empty_list():
            return "\tdb 0x0\n\tdb 0x0\n"
        if pair_obj.car is None:
            asm_instructions.append("\tdb 0x0")
        else:
            car_generator = factory.create_generator(pair_obj.car,self.offset)
            #if check for pairs and vecs, so that in case of a pair, one can write the next ptr using the label
            if car_generator.ident_obj.is_compound_type():
                car_generator.set_ident_name(self.ident_name)
            asm_instructions.append(car_generator.generate_global_var())
        #now handle the cdr
        if pair_obj.cdr is None:
            asm_instructions.append("\tdb 0x0")
        else:
            car_size = pair_obj.car.get_size()
            cdr_generator = factory.create_generator(pair_obj.cdr,self.offset + car_size)
            if cdr_generator.ident_obj.is_compound_type():
                cdr_generator.set_ident_name(self.ident_name)
                if cdr_generator.ident_obj.typeof == IdentifierType.PAIR:
                    next_pair_offset = car_size + self.offset + 8
                    cdr_generator.set_offset(next_pair_offset)
                    #write address to next list element:
                    asm_instructions.append(f"\tdq {self.ident_name} + {str(next_pair_offset)}")
            asm_instructions.append(cdr_generator.generate_global_var())
        return '\n'.join(asm_instructions)
            
    def generate_local_var(self):
        return "generating local pair var(stack)"
        
class VectorGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
        
    def generate_global_var(self):
        asm_instructions = []
        vector_obj = self.ident_obj.value
        factory = GeneratorFactory()
        offset = self.offset
        for ident_elt in vector_obj:
            elt_generator = factory.create_generator(ident_elt,offset)
            if elt_generator.ident_obj.is_compound_type():
                elt_generator.set_ident_name(self.ident_name)
            asm_instructions.append(elt_generator.generate_global_var())
            offset += ident_elt.get_size()
        return '\n'.join(asm_instructions)
    
    def generate_local_var(self):
        return "generating local vector var(stack)"

class FunctionGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        asm_instructions = ["\tpush rbp","\tmov rbp,rsp"]
        
        func = self.ident_obj.value
        param_offsets = []
        local_defs_offsets = []
        #first add params to the stack in order
        for i,param in enumerate(func.param_list):
            offset = 0
            if i > 5:
                offset = f"+{(i - 5) * 8}"
                # offset = (i - 5) * 8
                param_offsets.append(offset)
            else:
                offset = f"-{(i + 1) * 8}"
                param_offsets.append(offset) 
                asm_instructions.append(f"\tmov QWORD [rbp{offset}, {LINUX_CALLING_CONVENTION[i]}]")
        print(param_offsets)
        # now add all definitions in body(local_defs) they will continue from where params left off.
        offset = -56 if len(param_offsets) > 5 else -(len(param_offsets) + 1) * 8
        print(offset)
        print(func.local_definitions)
        for definition in func.local_definitions:
            local_defs_offsets.append(f"{offset}")
            #here you have to process the define, aka emit some code to set the define to rax
            # this is where the runtime will come in, call the function in the runtime to set result in rax.
            # fill the args for function in runtime here(after i make it)
            asm_instructions.append(f"\tmov QWORD [rbp{offset}, rax]")
            offset -= 8
        print("Local_def offsets:", local_defs_offsets)
            
            
            
            
        
        
        
        #epilogue
        asm_instructions.append("\tpop rbp\n\tret")
        return '\n'.join(asm_instructions)

    def generate_local_var(self):
        return "generating local function var(stack)"