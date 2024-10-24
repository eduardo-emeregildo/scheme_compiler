from abc import ABC,abstractmethod
from environment import *
from scheme_list import *
import sys
#these clases will handle the generation of asm code for various types depending on scope.
#there is one generator class per IdentifierType
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
        print("generating local int var(stack)")
        
class FloatGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
        
    def generate_global_var(self):
        return f"\tdq {self.ident_obj.value}"

    def generate_local_var(self):
        print("generating local float var(stack)")

class CharGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdb '{self.ident_obj.value[-1]}'"

    def generate_local_var(self):
        print("generating local char var(stack)")
        
class StringGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdb {self.ident_obj.value}, 0"

    def generate_local_var(self):
        print("generating local string var(stack)")

class BooleanGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdb {'1' if self.ident_obj.value =='#t' else '0'}"

    def generate_local_var(self):
        print("generating local boolean var(stack)")

class SymbolGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        return f"\tdb '{self.ident_obj.value}', 0"

    def generate_local_var(self):
        print("generating local symbol var(stack)")

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
        print("generating local pair var(stack)")
        
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
        print("generating local vector var(stack)")

class FunctionGenerator(Generator):
    def __init__(self,ident_obj,offset,ident_name = ""):        
        self.ident_obj = ident_obj
        self.ident_name = ident_name
        self.offset = offset
    
    def generate_global_var(self):
        print("generating global function var")

    def generate_local_var(self):
        print("generating local function var(stack)")