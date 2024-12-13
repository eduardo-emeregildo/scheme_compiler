# from environment import *
import sys
#class used to represent functions. for Identifier objs with 
# typeof = IdentifierType.FUNCTION, its value will be this function object

#param_list is a python list of param names

# local_definitions is for local define exps in the body of the function. the 
# values are identifier objects

#arity  is number of args the function accepts
#is_variadic indicates if function was defined with dot notation in call pattrn
#if the function is variadic, arity - 1 represents the minimum amt of args required

#if procedure has more than six args, they'll be on the stack

#params_as_functions are for params that are being used as functions in the body.
#the key will be the param number, with the value being the arity
class Function():
    def __init__(self):
        self.name = ""
        self.param_list = []
        self.local_definitions = {}
        self.arity = 0
        self.is_variadic = False
        self.params_as_functions = {}
    
    def add_param(self,param:str):
        if param in self.param_list:
            sys.exit("Error. Duplicate argument name in " + param)
        self.param_list.append(param)
        self.arity += 1
    
    def add_local_definition(self,ident_name,ident_obj):
        self.local_definitions[ident_name] = ident_obj
    
    def set_body(self,body):
        self.body = self.body + body
    
    def set_name(self,name : str):
        self.name = name
        
    def get_name(self):
        return self.name
    
    def set_variadic(self):
        self.is_variadic = True
        
    def add_function_param(self,param_number,function_arity):
        if param_number not in self.params_as_functions:
            self.params_as_functions[param_number] = function_arity
            return
        print("Redifing a value in Function.params_as_functions")
        self.param_as_functions[param_number] = min(function_arity,
        self.param_as_functions[param_number])
    
    #should only be used for builtin functions
    def set(self,name,param_list,local_defs,arity,is_variadic):
        self.name = name
        self.param_list = param_list
        self.local_defs = local_defs
        self.arity = arity
        self.is_variadic = is_variadic
        return self