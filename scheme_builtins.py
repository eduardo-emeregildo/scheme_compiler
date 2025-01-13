#where all the builtin function objects for the parser will live. 
#builtins will be treated as global functions
from function import *
BUILTINS = {
    "display": Function().set("display",["item"],1,False),
    "addition": Function().set("addition",["args"],1,True),
    "subtraction": Function().set("subtraction",["minuend,varargs"],2,True),
    "equal_sign": Function().set("equal_sign",["value1,value2"],2,False),
    "greater": Function().set("greater",["value1,value2"],2,False),
    "greater_equal": Function().set("greater_equal",["value1,value2"],2,False),
    "less": Function().set("less",["value1,value2"],2,False),
    "less_equal": Function().set("less_equal",["value1,value2"],2,False),
}
