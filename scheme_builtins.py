#where all the builtin function objects for the parser will live. 
#builtins will be treated as global functions
from function import *
BUILTINS = {
    "display": Function().set("display",["item"],{},1,False),
    "add": Function().set("add",["args"],{},1,True),
}
