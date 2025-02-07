#where all the builtin function objects for the parser will live. 
#builtins will be treated as global functions
from function import *
BUILTINS = {
    "DISPLAY": Function().set("DISPLAY",["item"],1,False),
    "ADDITION": Function().set("ADDITION",["args"],1,True),
    "SUBTRACTION": Function().set("SUBTRACTION",["minuend","varargs"],2,True),
    "MULT": Function().set("MULT",["param_list"],1,True),
    "DIVISION": Function().set("DIVISION",["dividend","varargs"],2,True),
    "EQUAL_SIGN": Function().set("EQUAL_SIGN",["value1","value2"],2,False),
    "GREATER": Function().set("GREATER",["value1","value2"],2,False),
    "GREATER_EQUAL": Function().set("GREATER_EQUAL",["value1","value2"],2,False),
    "LESS": Function().set("LESS",["value1","value2"],2,False),
    "LESS_EQUAL": Function().set("LESS_EQUAL",["value1","value2"],2,False),
    "CAR": Function().set("CAR",["type"],1,False),
    "CDR": Function().set("CDR",["type"],1,False),
    "NULLQ": Function().set("NULLQ",["type"],1,False),
    "EQ": Function().set("EQ",["value1","value2"],2,False),
    "EQV": Function().set("EQ",["value1","value2"],2,False),
    "EQUAL": Function().set("EQUAL",["value1","value2"],2,False),
    "APPEND": Function().set("APPEND",["varargs"],1,True),
    "MAKE_VECTOR": Function().set("MAKE_VECTOR",["size","init_value"],2,False),
    "VECTOR_REF": Function().set("VECTOR_REF",["vector","position"],2,False),
    "VECTOR_LENGTH": Function().set("VECTOR_LENGTH",["vector"],1,False),
}