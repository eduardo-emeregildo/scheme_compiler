import sys
from enum import Enum
class IdentifierType(Enum):
    CHAR = 0
    STR = 1
    INT = 2
    FLOAT = 3
    BOOLEAN = 4
    PAIR = 5
    VECTOR = 6
    FUNCTION = 7
    #an identifier that you dont evaluate. Ex would be if you do 'x, x is a symbol and we dont eval. an Identifier of this type would have the symbol name as the value
    SYMBOL = 8


class Identifier:
    #might need to add a third field which is offset from the stack. Since local vars will be on the stack, the offset amt is needed
    def __init__(self,typeof,value):
        self.typeof = typeof
        self.value = value
    
    def update(self,new_type,new_value):
        self.typeof = new_type
        self.value = new_value
        
    def is_compound_type(self):
        return self.typeof == IdentifierType.PAIR or self.typeof == IdentifierType.VECTOR
    
    #returns size in bytes that value will take up in memory.
    #at the very least has to get rewritten since im not using pair ds anymore.
    #probably just needs to get removeed
    def get_size(self):
        if self.typeof == IdentifierType.INT or self.typeof == IdentifierType.FLOAT:
            return 8
        elif self.typeof == IdentifierType.STR:
            return len(self.value) - 1
        elif self.typeof == IdentifierType.BOOLEAN or self.typeof == IdentifierType.CHAR:
            return 1
        elif self.typeof == IdentifierType.SYMBOL or self.typeof == IdentifierType.FUNCTION:
            return len(self.value) + 1
        elif self.typeof == IdentifierType.PAIR:
            sum = 0
            if self.value.is_empty_list():
                return 2
            if self.value.car is None:
                sum += 1
            else:
                sum += self.value.car.get_size()
            # now handle cdr
            if self.value.cdr is None:
                sum += 1
            else:
                if self.value.cdr.typeof == IdentifierType.PAIR:
                    #for pointer to next
                    sum += 8
                sum += self.value.cdr.get_size()
            return sum
        elif self.typeof == IdentifierType.VECTOR:
            sum = 0
            for ident in self.value:
                sum += ident.get_size()
            return sum

#Below This is how lexical scoping will be handled. symbol_table is a dictionary
#which has the identifier name as the key,
#each key will store a 2 elt aray, first elt is the offset, second elt is the
#Identifier object, detailing what type it is ands its value.
#global vars will have an offset of None, since they will be retrieved 
#differently (from the bss section)
# Parent will hold its parent Environment. The global environment is the 
# environment with None parent
#the depth is the sum of all the offsets. since global env doesnt save on stack,
#the global env will always have depth = 0
class Environment:
    def __init__(self,parent = None):
        self.symbol_table = {}
        self.parent = parent
        self.depth = 0
        
    def add_definition(self,ident_name,identifier_obj):
        if self.parent is None:
            self.symbol_table[ident_name] = [None,identifier_obj]
            return
        self.depth += 8
        self.symbol_table[ident_name] = [self.depth,identifier_obj]
        
    # def get_offset(self,ident_name):
    #     return self.symbol_table[ident_name][0]
    
    # def get_ident_object(self,ident_name):
    #     return self.symbol_table[ident_name][1]

    def remove_definition(self,ident_name):
        del self.symbol_table[ident_name]
        if self.parent is not None:
            self.depth -= 8
    
    def is_global(self):
        return self.parent is None
        
    def find_definition(self,ident_name):  
        if ident_name in self.symbol_table:
            return self.symbol_table[ident_name]
        if self.parent == None:
            sys.exit("Error, " + "Identifier " + ident_name + "Not defined.")
        return self.parent.find_definition(ident_name)
    #caller will be parent env of new env
    def create_local_env(self):
        return Environment(self)
    
    @staticmethod
    def get_offset(definition_arr):
        return definition_arr[0]
    
    @staticmethod
    def get_ident_obj(definition_arr):
        return definition_arr[1]