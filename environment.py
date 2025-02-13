import sys
from enum import Enum
from function import *
from scheme_builtins import BUILTINS
LINUX_CALLING_CONVENTION = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
class IdentifierType(Enum):
    CHAR = 0
    STR = 1
    INT = 2
    FLOAT = 3
    BOOLEAN = 4
    PAIR = 5
    VECTOR = 6
    FUNCTION = 7
    SYMBOL = 8
    CLOSURE = 9 #closures will have a Function obj as Identifier.value
    
    #signifies the evaluation of an arg. since type is not known the value
    #is just the name of the arg
    PARAM = 10
    # if last exp was a function call, the value of identifier will be the name of function
    #(Maybe add this)if function call was from a param, the value is ""
    FUNCTION_CALL = 11
class Identifier:
    def __init__(self,typeof,value):
        self.typeof = typeof
        self.value = value
    
    def update(self,new_type,new_value):
        self.typeof = new_type
        self.value = new_value
        
    def is_compound_type(self):
        return self.typeof == IdentifierType.PAIR or self.typeof == IdentifierType.VECTOR
    

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
            #global var
            self.symbol_table[ident_name] = [None,identifier_obj]
            return                
        self.depth -= 8
        self.symbol_table[ident_name] = [self.depth,identifier_obj]
    
    #for adding arguments 7 and on. They'll already be on the stack
    def add_stack_definition(self,ident_name,offset):
        self.symbol_table[ident_name] = [offset,
        Identifier(IdentifierType.PARAM,ident_name)]
    
    def is_defined(self,ident_name):
        return ident_name in self.symbol_table
    
    #useful for removing the item thats on top of the stack
    def remove_definition(self,ident_name):
        del self.symbol_table[ident_name]
        if self.parent is not None:
            self.depth += 8
    
    def is_global(self):
        return self.parent is None
        
    def find_definition(self,ident_name):
        if ident_name in self.symbol_table:
            return self.symbol_table[ident_name]
        if self.parent is None:
            sys.exit("Error, " + "Identifier " + ident_name + " not defined.")
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

    #check if definition_arr represents an argument
    @staticmethod
    def is_arg(definition_arr):
        return definition_arr[1] is None