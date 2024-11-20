from environment import *
import sys
#class used to represent functions. for Identifier objs with 
# typeof = IdentifierType.FUNCTION, its value will be this function object

#param_list is a python list of param names
#arity  is number of args the function accepts
#body is the asm instructions for the function

#if procedure has more than six args, they'll be on the stack
LINUX_CALLING_CONVENTION = ["rdi", "rsi", "rdx", "rcx", "r8", "r9"]
LINUX_FLOATING_POINT_CONVENTION = ["xmm0","xmm1","xmm2","xmm3","xmm4","xmm5",
"xmm6","xmm7"
]

class Function():
    def __init__(self):
        self.name = ""
        self.param_list = []
        #for local define expressions in the body of the function
        self.local_definitions = {}
        self.arity = 0
        self.body = ""
    
    def add_param(self,param:str):
        self.param_list.append(param)
        self.arity += 1
    
    def add_local_definition(self,ident_name,ident_obj: Identifier):
        self.local_definitions[ident_name] = ident_obj
    
    def add_to_body(self,body):
        self.body = self.body + body
    
    def set_name(self,name : str):
        self.name = name
        
    def get_name(self):
        return self.name
    
    #builds the local environment for this Function obj using its param_list and local_definitions given an initialized Enivroment and returns it.
    #args is a list of arguments user passed that will bind, each elt of type Identifier that will bind with the params 
    def build_local_environment(self,args,env: Environment) -> Environment:
        if env.is_global() or len(args) != self.arity:
            sys.exit("Cannot build local environment.")
            
        for ident in self.local_definitions:
            env.add_definition(ident,self.local_definitions[ident])
            
        for i,ident_name in enumerate(self.param_list):
            env.add_definition(self.param_list[i],args[i])
        return env
    
    

#the "anonymous" types should be declared on the heap i.e. when you call (get-param '(1 2 3)), you first do a malloc that allocates the list '(1 2 3), and then you pass the ptr to this obj(which the malloc return gives you)

#since ints,floats,chars and bools will be on the stack and are of fixed size, their values will be directly passed to arg registers. 

#but then how to free the memory?
# for example say I have:

# (define (get-car lst) (car lst))
# (get-car '(1 2 3))

# after get-car returns 1, '(1 2 3) wont have a reference anymore. This is where garbage collection will come in