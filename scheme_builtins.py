#where all the builtin function objects will live. Identifier expression and
# function calling should search for builtins here.

#builtins will be treated as global functions

#Also, user cannot define functions with names that are in here
from function import *
BUILTINS = {
    "display": Function().set("display",["item"],{},1,False),
}
