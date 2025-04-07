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
    
    #checks if ident is known at compile time. PARAM and FUNCTION_CALL cannot 
    # be known at compile time, so for these runtime checks need to be made
    def is_type_known(self):
        if self.typeof == IdentifierType.PARAM or self.typeof == IdentifierType.FUNCTION_CALL:
            return False
        return True
    
    def is_non_ptr_type(self):
        if (self.typeof == IdentifierType.INT or 
            self.typeof == IdentifierType.CHAR or 
            self.typeof == IdentifierType.BOOLEAN):
            return True
        return False

#All the builtins as closures
BUILTINS = {    
    "DISPLAY": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("DISPLAY",["self","item"],2,False))),
    "ADDITION": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("ADDITION",["self","args"],2,True))),
    "SUBTRACTION": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("SUBTRACTION",["self","minuend","varargs"],3,True))),
    "MULT": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("MULT",["self","param_list"],2,True))),
    "DIVISION": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("DIVISION",["self","dividend","varargs"],3,True))),
    "EQUAL_SIGN": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("EQUAL_SIGN",["self","value1","value2"],3,False))),
    "GREATER": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("GREATER",["self","value1","value2"],3,False))),
    "GREATER_EQUAL": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("GREATER_EQUAL",["self","value1","value2"],3,False))),
    "LESS": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("LESS",["self","value1","value2"],3,False))),
    "LESS_EQUAL": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("LESS_EQUAL",["self","value1","value2"],3,False))),
    "CAR": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("CAR",["self","type"],2,False))),
    "CDR": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("CDR",["self","type"],2,False))),
    "NULLQ": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("NULLQ",["self","type"],2,False))),
    "EQ": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("EQ",["self","value1","value2"],3,False))),
    "EQV": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("EQ",["self","value1","value2"],3,False))),
    "EQUAL": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("EQUAL",["self","value1","value2"],3,False))),
    "APPEND": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("APPEND",["self","varargs"],2,True))),
    "MAKE_VECTOR": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("MAKE_VECTOR",["self","size","init_value"],3,False))),
    "VECTOR_REF": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("VECTOR_REF",["self","vector","position"],3,False))),
    "VECTOR_LENGTH": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("VECTOR_LENGTH",["self","vector"],2,False))),
    "VECTOR_SET": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("VECTOR_SET",["self","vector","position","new_val"],4,False))),
    "PAIRQ": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("PAIRQ",["self","val"],2,False))),
    "LISTQ": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("LISTQ",["self","val"],2,False))),
    "VECTORQ": Identifier(
        IdentifierType.CLOSURE,
        Identifier(IdentifierType.FUNCTION,Function().set("VECTORQ",["self","val"],2,False))),
}
    

#Below This is how lexical scoping will be handled. symbol_table is a dictionary
#which has the identifier name as the key,
#each key will store a 3 elt aray, first elt is the offset, second elt is the
#Identifier object, detailing what type it is ands its value.

#Third is is_captured flag. This is used for checking if the definition was captured
#by an inner function

#global vars will have an offset of None, since they will be retrieved 
#differently (from the bss section)

# Parent will hold its parent Environment. The global environment is the 
# environment with None parent
#the depth is the sum of all the offsets. since global env doesnt save on stack,
#the global env will always have depth = 0
class Environment:
    def __init__(self,parent = None):
        self.name = ""
        self.symbol_table = {}
        self.parent = parent
        self.depth = 0
        
    def add_definition(self,ident_name,identifier_obj):
        if self.parent is None:
            #global var
            self.symbol_table[ident_name] = [None,identifier_obj,False]
            return                
        self.depth -= 8
        self.symbol_table[ident_name] = [self.depth,identifier_obj,False]
    
    #for adding arguments 7 and on. They'll already be on the stack
    def add_stack_definition(self,ident_name,offset):
        self.symbol_table[ident_name] = [offset,
        Identifier(IdentifierType.PARAM,ident_name),False]
    
    def set_def_as_captured(self,variable_offset):
        # if ident_name not in self.symbol_table:
        #     sys.exit("Def not found in symbol table, cant set as captued.")
        # self.symbol_table[ident_name][2] = True
        for ident_name in self.symbol_table:
            if self.symbol_table[ident_name][0] == variable_offset:
                self.symbol_table[ident_name][2] = True
                return
        sys_.exit(f"Definition with offset {variable_offset} not found.")
                
                
    
    def is_defined(self,ident_name):
        return ident_name in self.symbol_table
    
    #useful for removing the item thats on top of the stack
    def remove_definition(self,ident_name):
        del self.symbol_table[ident_name]
        if self.parent is not None:
            self.depth += 8
    
    def is_global(self):
        return self.parent is None
    
    def set_env_name(self,name):
        self.name = name    
    #returns definition of identifier if definition is an upvalue and nest count
    def find_definition(self,ident_name,nest_count = 0,is_upvalue = False):
        if self.is_defined(ident_name):
            if self.is_global(): # if found in global scope, no need for upvalue
                is_upvalue = False
            return self.symbol_table[ident_name],is_upvalue,nest_count
        if self.is_global():
            sys.exit("Error, " + "Identifier " + ident_name + " not defined.")
        return self.parent.find_definition(ident_name,nest_count + 1,True)
        
    #caller will be parent env of new env
    def create_local_env(self):
        return Environment(self)
    
    @staticmethod
    def get_offset(definition_arr):
        return definition_arr[0]
    
    @staticmethod
    def get_ident_obj(definition_arr):
        return definition_arr[1]

    @staticmethod
    def get_is_captured_flag(definition_arr):
        return definition_arr[2]

    #check if definition_arr represents an argument
    @staticmethod
    def is_arg(definition_arr):
        return definition_arr[1] is None