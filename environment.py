import sys
from enum import Enum
from function import *
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
    #an identifier that you dont evaluate. Ex would be if you do 'x, x is a symbol and we dont eval. an Identifier of this type would have the symbol name as the value
    SYMBOL = 8
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

#when adding register args to symbol_table, they will have the identifier obj
#sent to None since it is not known what the type is.
# (type checking at runtime is done in the actual function)


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
        self.symbol_table[ident_name] = [offset,None]
    
    def is_defined(self,ident_name):
        return ident_name in self.symbol_table
        
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
    
    #creates a local environment given a function, for a function to run in
    # the caller of this method will be the parent environment
    def create_function_env(self,function):
        env = self.create_local_env()
        #first add arguments to symbol table
        for i,param in enumerate(function.param_list):
            if i < 6:
                env.add_definition(param,None)
            else:
                #params 7th and higher will be on: (rsp + x)
                env.add_stack_definition(param,(i-4)*8)
        #now local definitions
        for definition in function.local_definitions:
            env.add_definition(definition,function.local_definitions[definition])
        return env

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