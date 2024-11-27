from environment import *
import sys
#class used to represent functions. for Identifier objs with 
# typeof = IdentifierType.FUNCTION, its value will be this function object

#param_list is a python list of param names
# local_definitions is for local define expressions in the body of the function
#arity  is number of args the function accepts
#is_variadic indicates if function was defined with dot notation in call pattrn
#if procedure has more than six args, they'll be on the stack
class Function():
    def __init__(self):
        self.name = ""
        self.param_list = []
        self.local_definitions = {}
        self.arity = 0
        self.is_variadic = False 
    
    def add_param(self,param:str):
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