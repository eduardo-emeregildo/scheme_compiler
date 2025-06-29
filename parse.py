import sys
from lex import *
from emit import *
from environment import *
from function import *
from upvalue import *
#Todo's in the future:
# 1. implement string interning
# 2. implement tail call optimization
# 3. have display print out special characters, i.e. \n,\t etc
# 4. imports
# 5. have a "debug" mode where it prints all the symbols,terminals,nonterminals
# 6. Add some macros for casting to improve readability    
# 7. see if i can remove emitting assembly to call collect_garbage

# Parser object keeps track of current token and checks if the code matches the grammar.
class Parser:
    def __init__(self, lexer,emitter):
        self.lexer = lexer
        self.emitter = emitter
        #store last result of an expression as an identifier class
        self.last_exp_res = None
        self.cur_token = None
        self.peek_token = None
        self.global_environment = Environment()
        self.cur_environment = self.global_environment
        self.tracker = UpvalueTracker()
        self.next_token()
        self.next_token()

    # Return true if the current token matches.
    def check_token(self, type):
        return type == self.cur_token.type
    
    def set_last_exp_res(self,typeof,val):
        self.last_exp_res = Identifier(typeof,val)
    
    def get_last_exp_type(self):
        return self.last_exp_res.typeof
    
    def get_last_exp_value(self):
        if self.last_exp_res is None:
            self.abort("Cannot get last_exp_value since it is set to None.")
        return self.last_exp_res.value
        
    def is_token_any(self,type,type_arr):
        return type in type_arr
    
    # Return true if the next token matches.
    def check_peek(self, type):
        return type == self.peek_token.type

    # Try to match current token. If not, error. Advances the current token.
    def match(self, type):
        if not self.check_token(type):
            self.abort(
            "Expected " + type.name + ", got " + self.cur_token.type.name)
        self.next_token()
        
    # Advances the current token.
    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message):
        sys.exit("Error. " + message)
    
    def evaluate_constant(self):
        match self.cur_token.type:
            case TokenType.NUMBER:
                if isinstance(self.cur_token.text,int):
                    self.set_last_exp_res(IdentifierType.INT,str(self.cur_token.text))
                else: 
                    self.set_last_exp_res(IdentifierType.FLOAT,str(self.cur_token.text))
            case TokenType.BOOLEAN:
                self.set_last_exp_res(IdentifierType.BOOLEAN,self.cur_token.text)
            case TokenType.CHAR:
                self.set_last_exp_res(IdentifierType.CHAR,self.cur_token.text)
            case TokenType.STRING:
                self.set_last_exp_res(IdentifierType.STR,self.cur_token.text)
            case _:
                self.abort(
                "Calling evaluate_constant(). current token is not a constant") 
                                
    def evaluate_symbol(self):
        self.set_last_exp_res(IdentifierType.SYMBOL,self.cur_token.text)
    
    #pair_list is just a list of Identifiers
    def evaluate_pair(self,pair_list):
        self.set_last_exp_res(IdentifierType.PAIR,pair_list)
    
    def evaluate_function(self,function_obj):
        self.set_last_exp_res(IdentifierType.FUNCTION,function_obj)
    
    def evaluate_closure(self,function_ident_obj: Identifier):
        self.set_last_exp_res(IdentifierType.CLOSURE,function_ident_obj)
    
    def evaluate_param(self,arg_name):
        self.set_last_exp_res(IdentifierType.PARAM,arg_name)
        
    def evaluate_function_call(self,func_name):
        self.set_last_exp_res(IdentifierType.FUNCTION_CALL,func_name)
    
    def set_vector(self,vector_obj):
        self.set_last_exp_res(IdentifierType.VECTOR,vector_obj)
    
    #returns bool indicating if the offset of seventh arg is 16 byte aligned 
    # depending on number of args and environment depth given.
    def check_if_alignment_needed(self,env_depth,total_args):
        if total_args < 7:
            return False
        seventh_arg_offset = env_depth - ((total_args - 6) * 8)
        return True if seventh_arg_offset % 16 != 0 else False
    
    
    #checks that definition name doesnt have a name that would conflict with
    # lambdas and lets (i.e. LA1,LA2 etc.)
    def is_definition_name_okay(self,name):
        if len(name) < 3:
            return True
        elif name[0] == "L" and name[1] == "A":
            return not name[2:].isnumeric()
        else:
            return True
    
    #searches for identifier. If identifier is in an enclosing scope, 
    #sends an upvalue request
    def resolve_identifier(self):
        is_global = self.cur_environment.is_global()
        definition_result = self.cur_environment.find_definition(
        self.cur_token.text)
        definition = definition_result[0]
        is_upvalue = definition_result[1]
        nest_count = definition_result[2]
        def_ident_obj = Environment.get_ident_obj(definition)
        offset = Environment.get_offset(definition)
        self.set_last_exp_res(def_ident_obj.typeof,def_ident_obj.value)
        if is_upvalue:
            if self.tracker.is_tracker_on():
                #add to tracker
                env = self.cur_environment
                for i in range(nest_count,0,-1):
                    inner_function_name = env.name
                    env = env.parent
                    is_local = True if i == 1 else False
                    upvalue_request = [inner_function_name,offset,is_local,i]
                    if self.is_definition_name_okay(inner_function_name):
                        self.tracker.add_upvalue_request(env.name,upvalue_request)
                    else:
                        self.tracker.add_anonymous_request(env.name,upvalue_request)
        return definition_result
    
    #result will be in rax
    def resolve_and_eval_identifier(self):
        is_global = self.cur_environment.is_global()
        definition_result = self.resolve_identifier()
        definition = definition_result[0]
        is_upvalue = definition_result[1]
        nest_count = definition_result[2]
        def_ident_obj = Environment.get_ident_obj(definition)
        offset = Environment.get_offset(definition)
        is_captured = Environment.get_is_captured_flag(definition)
        env_depth = self.cur_environment.depth
        if is_upvalue:
            #assumes that upvalue is always a ptr type. For ints,bools,and chars
            #returns just the tagged type
            self.emitter.emit_get_upvalue(env_depth,offset,nest_count,is_global)
        elif is_global:
            self.emitter.emit_var_to_global(self.cur_token.text,definition)
        else:
            self.emitter.emit_var_to_local(
            self.cur_token.text,offset,def_ident_obj,is_captured,env_depth,is_global)
    
    def add_upvals_to_anon_functions(self,is_global):
        cur_function = self.emitter.cur_function
        #now current function will supply upvalues that inner functions requested,
        #if no requests, wont do anything
        if self.tracker.function_has_anon_requests(cur_function):
            function_requests = self.tracker.get_anonymous_requests(cur_function)
            for request in function_requests:
                inner_function_def = self.cur_environment.symbol_table[request[0]] 
                inner_function_offset = inner_function_def[0]
                is_captured = inner_function_def[2]
                upvalue_offset = request[1]
                is_local = request[2]
                nest_count = request[3]
                if is_local:
                    #first turn non ptr types to ptr types, then do emit_add_upvalue.
                    if not is_captured:
                        #save rax to restore after move_local_to_heap
                        self.emitter.save_rax(self.cur_environment)
                        self.emitter.emit_move_local_to_heap(
                        upvalue_offset,self.cur_environment)
                        
                        self.cur_environment.locals_moved_to_heap_count += 1
                        
                        self.cur_environment.set_def_as_captured(request[1])
                        env_depth = self.cur_environment.depth
                        #restore rax
                        self.emitter.move_stack_def_to_rax(env_depth,is_global)
                        self.emitter.undo_save_rax(self.cur_environment)
                    self.emitter.emit_add_upvalue_anonymous(
                    self.cur_environment,upvalue_offset,nest_count)
                else:
                    #search upvalues of current definition instead of locals, add
                    #to target closure
                    self.emitter.emit_add_upvalue_nonlocal_anonymous(
                    self.cur_environment,upvalue_offset,nest_count)
            del self.tracker.anonymous_requests[cur_function]

    def program(self):
        print("Program")
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
        #Parse all expressions in the program
        while not self.check_token(TokenType.EOF):
            self.expression()
        self.emitter.emit_main_section("\tmov rax,0\n\tpop rbp\n\tret")
    
    #after self.expression() is executed, what the expression evaluates to
    #will be in rax   
    def expression(self): 
        if self.check_token(TokenType.NEWLINE):
            self.next_token()
        #<constant> ::= <boolean> | <number> | <character> | <string>
        elif self.check_token(TokenType.NUMBER):
            print("EXPRESSION-NUMBER")
            if isinstance(self.cur_token.text,int):
                self.set_last_exp_res(IdentifierType.INT,str(self.cur_token.text))
                self.emitter.emit_identifier_to_section(self.last_exp_res,
                self.cur_environment)
            else:
                self.set_last_exp_res(IdentifierType.FLOAT,str(self.cur_token.text))
                self.emitter.emit_identifier_to_section(self.last_exp_res,
                self.cur_environment)
            self.next_token()
        
        elif self.check_token(TokenType.CHAR):
            print("EXPRESSION-CHAR")
            self.set_last_exp_res(IdentifierType.CHAR,self.cur_token.text)
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment)
            self.next_token()
            
        elif self.check_token(TokenType.BOOLEAN):
            print("EXPRESSION-BOOLEAN")
            self.set_last_exp_res(IdentifierType.BOOLEAN,self.cur_token.text)
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment)
            self.next_token()

        elif self.check_token(TokenType.STRING):
            print("EXPRESSION-STRING")
            self.set_last_exp_res(IdentifierType.STR,self.cur_token.text)
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment)
            self.next_token()
        
        elif self.check_token(TokenType.IDENTIFIER):
            print("EXPRESSION-VARIABLE")
            self.resolve_and_eval_identifier()
            self.next_token()
                    
        elif self.check_token(TokenType.QUOTE_SYMBOL):
            print("EXPRESSION-QUOTE-SYMBOL")
            self.next_token()
            self.datum()
        
        elif self.check_token(TokenType.BUILTIN):
            print("BUILTIN")
            is_global = self.cur_environment.is_global()
            builtin_closure = BUILTINS[self.cur_token.text]
            self.emitter.add_extern(self.cur_token.text)
            self.emitter.emit_builtin_closure(self.cur_token.text,is_global)
            self.last_exp_res = builtin_closure
            self.next_token()

        elif self.check_token(TokenType.EXPR_START):
            self.next_token()
            if self.check_token(TokenType.IF):
                self.next_token()
                self.if_exp()
    
            elif self.check_token(TokenType.QUOTE):
                self.next_token()
                self.quote_exp()
            
            elif self.check_token(TokenType.LAMBDA):
                self.next_token()
                self.lambda_exp()
            
            elif self.check_token(TokenType.DEFINE):
                self.next_token()
                self.definition_exp()
                
            elif self.check_token(TokenType.AND):
                self.next_token()
                self.and_exp()
                
            elif self.check_token(TokenType.OR):
                self.next_token()
                self.or_exp()
            
            elif self.check_token(TokenType.COND):
                self.next_token()
                self.cond_exp()
            
            elif self.check_token(TokenType.CASE):
                self.next_token()
                self.case_exp()

            elif self.check_token(TokenType.LET):
                self.next_token()
                self.let_exp()
            
            elif self.check_token(TokenType.LETSTAR):
                self.next_token()
                self.let_star_exp()
            
            elif self.check_token(TokenType.LETREC):
                self.next_token()
                self.letrec_exp()
                
            elif self.check_token(TokenType.SETEXCLAM):
                self.next_token()
                self.setexclam_exp()
            
            elif self.check_token(TokenType.REC):
                self.next_token()
                self.rec_exp()
                
            #(begin <expression>)
            elif self.check_token(TokenType.BEGIN):
                self.next_token()
                print("EXPRESSION-BEGIN")
                self.expression()
                self.match(TokenType.EXPR_END)
                
            # (delay <expression>)
            elif self.check_token(TokenType.DELAY):
                self.next_token()
                print("EXPRESSION-DELAY")
                self.expression()
                self.match(TokenType.EXPR_END)
            
            elif self.check_token(TokenType.DO):
                self.next_token()
                self.do_exp()
                
            elif self.check_token(TokenType.QUASIQUOTE):
                self.next_token()
                self.quasiquote_exp()
                
            #<procedure call> ::= (<operator> <operand>*)
            else:
                print("EXPRESSION-PROCEDURECALL")
                print("OPERATOR")
                self.expression()
                if self.last_exp_res.typeof == IdentifierType.CLOSURE:
                    self.evaluate_function(self.last_exp_res.value.value)
                    if self.last_exp_res.typeof == IdentifierType.FUNCTION:
                        func_obj = self.last_exp_res.value
                        if func_obj.is_variadic:
                            self.variadic_function_call(func_obj)
                        else:
                            self.function_call(func_obj)
                else:
                    self.general_function_call()
        else:
            self.abort("Token " + self.cur_token.text + " is not a valid expression")

    #for general function calling when the compiler cant tell what function 
    # is being used. The closure object is in rax.
    def general_function_call(self):
        print("GENERAL FUNCTION CALL")
        is_global = self.cur_environment.is_global()
        arg_count = 0
        self.emitter.emit_to_section(
        ";general function call start",self.cur_environment.is_global())
        #save rax temporarily to perform checks on it later
        self.emitter.save_rax(self.cur_environment)
        
        #these two are the same value, but the different names are for context
        callable_obj_depth = self.cur_environment.depth
        env_depth = self.cur_environment.depth
        
        arg_count += 1
        self.emitter.emit_to_section(
        ";general_function_call,storing self arg on line below:",is_global)
        self_arg_offset = self.emitter.push_arg(
        arg_count,self.cur_environment,env_depth,is_global)
        self.cur_environment.depth -= 8
        self.emitter.subtract_rsp(abs(self.cur_environment.depth),is_global)
        self.emitter.emit_push_live_local(is_global,self_arg_offset)
        self.emitter.add_rsp(abs(self.cur_environment.depth),is_global)
        
        #evaluates the args
        while not self.check_token(TokenType.EXPR_END):
            print("OPERAND")
            arg_count += 1
            self.expression()
            self.emitter.emit_pass_by_value(self.cur_environment.depth,is_global)
            arg_offset = self.emitter.push_arg(
            arg_count,self.cur_environment,env_depth,is_global)
            self.cur_environment.depth -= 8
            self.emitter.subtract_rsp(abs(self.cur_environment.depth),is_global)
            self.emitter.emit_push_live_local(is_global,arg_offset)
            self.emitter.add_rsp(abs(self.cur_environment.depth),is_global)
        
        #pop args from live locals
        self.emitter.emit_to_section(";popping locals in general function",is_global)
        self.emitter.pop_live_locals(self.cur_environment,arg_count,False)
        self.cur_environment.depth += 8*arg_count
        
        # now perform runtime checks to see if  operator is a function/ 
        # what kind of function
        self.emitter.emit_function_check(self.cur_environment,callable_obj_depth,arg_count)
        self.emitter.emit_zero_check(is_global)
        variadic_label = self.emitter.emit_conditional_jump("!=",is_global)
        self.emitter.emit_to_section(";aaaaa",is_global)
        
        #dealing with stack alignment for non varidic general function calling
        is_alignment_needed = self.check_if_alignment_needed(env_depth,arg_count)
        #now put args in the right place for non variadic case
        #-8 is offset of last arg (assuming env depth is 0)
        for cur_arg in range(arg_count):
            if cur_arg < 6:                
                self.emitter.emit_register_arg(cur_arg,env_depth,is_global)
            else:
                self.emitter.emit_arg_to_stack(
                cur_arg,env_depth,is_global,arg_count,is_alignment_needed)
        self.emitter.emit_to_section("\t;finished putting args non variadic",is_global)
        #advance rsp to point to 7th arg, if less than 7 args, advance rsp so 
        # local defs arent overwritten
        self.emitter.subtract_rsp_given_arity(
        arg_count,env_depth,is_global,is_alignment_needed)
        #now call the function
        self.emitter.emit_function_call(callable_obj_depth,is_global)
        self.emitter.add_rsp_given_arity(
        arg_count,env_depth,is_global,is_alignment_needed)
        #this jmp goes to rest of function
        rest_of_function_label = self.emitter.emit_jump(is_global)
        #variadic branch:
        self.emitter.emit_param_variadic_call(
        variadic_label,callable_obj_depth,env_depth,is_global)
        self.emitter.emit_ctrl_label(is_global,rest_of_function_label)
        self.emitter.undo_save_rax(self.cur_environment)
        self.evaluate_function_call("")
        self.next_token()
        
    #places args in correct registers for function call and emits a function call
    #This is a helper for function_call.
    def place_args_and_call_function(
        self,env_depth,callable_obj_depth,is_global,arg_count,func_obj):
        for cur_arg in range(arg_count):
            if cur_arg < 6:
                self.emitter.emit_register_arg(
                cur_arg,env_depth,is_global,arg_count)
            else:
                seventh_arg_offset =  abs(env_depth - (arg_count - 6)*8)
                self.emitter.subtract_rsp_absolute(seventh_arg_offset,is_global)
                break
        # for calls where no args are on the stack, subtract ONLY the depth if
        # there is stuff to preserve on the stack(AKA if depth != 0)
        if arg_count < 6:
            self.emitter.subtract_rsp(abs(env_depth),is_global)
        self.emitter.emit_function_call(callable_obj_depth,is_global)
        #add back the rsp
        if arg_count > 6:
            self.emitter.add_rsp_absolute(seventh_arg_offset,is_global)
        else:
            self.emitter.add_rsp(abs(env_depth),is_global)
    
    #given a function object, does a function call. last_exp_res will be set to
    #the function that was called
    def function_call(self,func_obj):
        print("FUNCTION CALL")
        self.emitter.emit_to_section(";function_call",self.cur_environment.is_global())
        self.emitter.save_rax(self.cur_environment)
        arg_count = 0
        is_global = self.cur_environment.is_global()
        env_depth = self.cur_environment.depth
        callable_obj_depth = self.cur_environment.depth

        is_alignment_needed = self.check_if_alignment_needed(env_depth,func_obj.arity)
        if is_alignment_needed:
            self.cur_environment.depth -= 8
            env_depth = self.cur_environment.depth
        #subtract environment's depth temporarily to compute the args without 
        #overwritting the stack,i.e. the local definitions
        self.cur_environment.depth -= func_obj.arity*8
        
        #adding the self arg of the closure:
        arg_count += 1
        self_arg_offset = self.emitter.push_arg(
        arg_count,self.cur_environment,env_depth,is_global,func_obj.arity)
        self.emitter.emit_to_section(";^added self arg",is_global)
        self.emitter.subtract_rsp(abs(self.cur_environment.depth),is_global)
        self.emitter.emit_push_live_local(is_global,self_arg_offset)
        self.emitter.add_rsp(abs(self.cur_environment.depth),is_global)
    
        while not self.check_token(TokenType.EXPR_END):
            print("OPERAND")
            arg_count += 1
            if arg_count > func_obj.arity:
                break
            self.expression()
            self.emitter.emit_pass_by_value(self.cur_environment.depth,is_global)
            #push each arg to the stack so that they're stored while evaluating each arg
            arg_offset = self.emitter.push_arg(
            arg_count,self.cur_environment,env_depth,is_global,func_obj.arity)
            self.emitter.subtract_rsp(abs(self.cur_environment.depth),is_global)
            self.emitter.emit_push_live_local(is_global,arg_offset)
            self.emitter.add_rsp(abs(self.cur_environment.depth),is_global)
        if arg_count != func_obj.arity:
                self.abort(f"Arity mismatch. Function " + 
                f"{func_obj.name} requires {str(func_obj.arity - 1)} arguments.")
        
        #now pop args from live_locals since you are about to do the function call
        self.emitter.emit_to_section(";popping locals",is_global)
        self.emitter.pop_live_locals(self.cur_environment,arg_count,False)
        
        #now that args have been processed, restore the env depth
        self.cur_environment.depth += func_obj.arity*8
        
        #now edit the saved closure obj (was saved by save_rax) to be the function
        #value_ptr:                
        self.emitter.emit_to_section(";editing closure obj to be function obj",is_global)
        self.emitter.get_function_from_closure(callable_obj_depth,is_global)
        self.emitter.emit_to_section(";done editing closure obj",is_global)
        
        self.place_args_and_call_function(
        env_depth,callable_obj_depth,is_global,arg_count,func_obj)
        self.emitter.undo_save_rax(self.cur_environment)
        if is_alignment_needed:
            self.cur_environment.depth += 8
        self.evaluate_function_call(func_obj.name)
        self.next_token()
    
    def variadic_function_call(self,func_obj):
        print("VARIADIC FUNCTION CALL")
        self.emitter.save_rax(self.cur_environment)
        arg_count = 0
        is_global = self.cur_environment.is_global()
        old_env_depth = self.cur_environment.depth
        callable_obj_depth = self.cur_environment.depth
        
        min_args = func_obj.arity - 1
        #adding self arg of the closure
        arg_count += 1
        self_arg_offset = self.emitter.push_arg(
        arg_count,self.cur_environment,old_env_depth,is_global)
        self.emitter.emit_to_section(";^added self arg",is_global)
        self.cur_environment.depth -= 8
        self.emitter.subtract_rsp(abs(self.cur_environment.depth),is_global)
        self.emitter.emit_push_live_local(is_global,self_arg_offset)
        self.emitter.add_rsp(abs(self.cur_environment.depth),is_global)
            
        #push args to stack to store while each arg gets evaluated
        while not self.check_token(TokenType.EXPR_END):
            arg_count += 1
            self.expression()
            self.emitter.emit_pass_by_value(self.cur_environment.depth,is_global)
            arg_offset = self.emitter.push_arg(
            arg_count,self.cur_environment,old_env_depth,is_global)
            
            self.cur_environment.depth -= 8
            self.emitter.subtract_rsp(abs(self.cur_environment.depth),is_global)
            self.emitter.emit_push_live_local(is_global,arg_offset)
            self.emitter.add_rsp(abs(self.cur_environment.depth),is_global)
        if arg_count < min_args:
            self.abort(f"Arity mismatch. {func_obj.name} requires at least" + 
            f" {min_args-1} arguments")
        #pop args from live locals
        self.emitter.emit_to_section(";popping locals in variadic function",is_global)
        self.emitter.pop_live_locals(self.cur_environment,arg_count,False)
        
        #now make varargs list
        self.emitter.emit_make_arg_list(
        min_args,func_obj.arity,arg_count,old_env_depth,is_global)
        self.cur_environment.depth = old_env_depth
        
        #dealing with stack alignment(stack must be 16 byte aligned at time of call)
        is_alignment_needed = self.check_if_alignment_needed(
        old_env_depth,func_obj.arity)
        
        #now edit the saved closure obj (was saved by save_rax) to be the function
        #value_ptr:
        self.emitter.emit_to_section(";editing closure obj to be function obj",is_global)
        self.emitter.get_function_from_closure(callable_obj_depth,is_global)
        self.emitter.emit_to_section(";done editing closure obj",is_global)
        
        #place args in the right spot
        for cur_arg in range(func_obj.arity):
            if cur_arg < 6:                
                self.emitter.emit_register_arg(cur_arg,old_env_depth,is_global)
            else:
                self.emitter.emit_arg_to_stack(
                cur_arg,old_env_depth,is_global,func_obj.arity,is_alignment_needed)
                
        self.emitter.subtract_rsp_given_arity(
        func_obj.arity,old_env_depth,is_global,is_alignment_needed)
        #now call function
        self.emitter.emit_function_call(callable_obj_depth,is_global)
        #restore rsp/environment depths after function call:
        self.emitter.add_rsp_given_arity(
        func_obj.arity,old_env_depth,is_global,is_alignment_needed)
        self.emitter.undo_save_rax(self.cur_environment)
        self.evaluate_function_call(func_obj.name)
        self.next_token()
        
        
    #(if <test> <consequent> <alternate>) | (if <test> <consequent>), where test,
    # consequent and alternate are expressions
    def if_exp(self):
        is_global = self.cur_environment.is_global()
        is_alternate = False
        print("EXPRESSION-IF")
        print("TEST")
        self.expression()
        self.emitter.emit_false_check(is_global)
        branch1_label = self.emitter.emit_conditional_jump("=",is_global)
        rest_of_exp_label = self.emitter.create_new_ctrl_label()
        print("CONSEQUENT")
        self.expression()
        if not self.check_token(TokenType.EXPR_END):
            print("ALTERNATE")
            #emit a jmp for the true branch so it can jump to the end
            self.emitter.emit_jump(is_global,rest_of_exp_label)
            is_alternate = True
            self.emitter.emit_ctrl_label(is_global,branch1_label)
            self.expression()
        self.emitter.emit_ctrl_label(
        is_global,rest_of_exp_label if is_alternate else branch1_label)
        self.match(TokenType.EXPR_END)
        
    #(quote <datum>)
    def quote_exp(self):
        print("EXPRESSION-QUOTE")
        self.datum()        
        if not self.check_token(TokenType.EXPR_END):
            self.abort("Incorrect syntax in quote expression. ")
        self.next_token()
        
    #(lambda <bound var list> <body>)
    def lambda_exp(self):
        print("EXPRESSION-LAMBDA")
        function = Function()
        is_global = self.cur_environment.is_global()
        if is_global:
            self.tracker.turn_tracker_on()
        print("IN LAMBDA: ", is_global)
        parent_env = self.cur_environment
        previous_function = self.emitter.cur_function
        self.cur_environment = parent_env.create_local_env()
        self.bound_var_list(function)
        self.body(function)
        #now switch back to parent environment/ previous function
        self.emitter.set_current_function(previous_function)
        self.cur_environment = parent_env
        if is_global:
            self.tracker.turn_tracker_off()
        function_ident = Identifier(IdentifierType.FUNCTION,function)
        self.evaluate_closure(function_ident)
        self.emitter.emit_identifier_to_section(
        self.last_exp_res,self.cur_environment)
        self.add_upvals_to_anon_functions(is_global)
        self.match(TokenType.EXPR_END)
        
    # (and <expression>*)
    def and_exp(self):
        print("EXPRESION-AND")
        is_global = self.cur_environment.is_global()
        rest_of_program_label = self.emitter.create_new_ctrl_label()
        expression_count = 0
        while not self.check_token(TokenType.EXPR_END):
            expression_count += 1
            self.expression()
            self.emitter.emit_false_check(is_global)
            if not self.check_token(TokenType.EXPR_END):
                self.emitter.emit_conditional_jump(
                "=",is_global,rest_of_program_label)
        self.emitter.emit_ctrl_label(is_global,rest_of_program_label)
        #default case where and was used with no expressions, i.e. (and)
        if expression_count == 0:
            self.emitter.set_rax_true(is_global)
        self.next_token()
        
    # (or <expression>*)
    def or_exp(self):
        print("EXPRESION-OR")
        is_global = self.cur_environment.is_global()
        rest_of_program_label = self.emitter.create_new_ctrl_label()
        expression_count = 0
        while not self.check_token(TokenType.EXPR_END):
            expression_count += 1
            self.expression()
            self.emitter.emit_false_check(is_global)
            if not self.check_token(TokenType.EXPR_END):
                self.emitter.emit_conditional_jump(
                "!=",is_global,rest_of_program_label)
        self.emitter.emit_ctrl_label(is_global,rest_of_program_label)
        if expression_count == 0:
            self.emitter.set_rax_false(is_global)
        self.next_token()
        
    # (cond <cond clause>*) | (cond <cond clause>* (else <sequence>))
    def cond_exp(self):
        print("EXPRESSION-COND")
        end_label = self.emitter.create_new_ctrl_label()
        cur_label = self.emitter.create_new_ctrl_label()
        next_label = self.emitter.create_new_ctrl_label()
        is_global = self.cur_environment.is_global()
        condition_count = 0
        while not self.check_token(TokenType.EXPR_END):
            if self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
                break
            condition_count += 1
            if condition_count > 1:
                self.emitter.emit_ctrl_label(is_global,cur_label)
            cur_label = next_label
            next_label = self.emitter.create_new_ctrl_label()
            self.cond_clause(cur_label,next_label,end_label,condition_count)
            cur_label = next_label
            next_label = self.emitter.create_new_ctrl_label()
        self.emitter.emit_ctrl_label(is_global,cur_label)
        if self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
            self.else_rule()
        self.emitter.emit_ctrl_label(is_global,end_label)
        self.next_token()
            
    #(case <expression> <case clause>*) | 
    # (case <expression> <case clause>* (else <sequence>))  
    # #<case clause> ::= ((<datum>*) <sequence>)       
    def case_exp(self):
        print("EXPRESSION-CASE")
        self.expression()
        
        if self.check_token(TokenType.EXPR_END):
            self.next_token()
            
        elif self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
            self.else_rule()
            self.match(TokenType.EXPR_END)
        
        # one or more case clauses and an optional else at the end
        else:
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
                    self.else_rule()
                    break
                self.case_clause()
            self.match(TokenType.EXPR_END)
    
    # (let (<binding spec>*) <body>) | (let <variable> (<binding spec>*) <body>) 
    def let_exp(self):
        print("EXPRESSION-LET")
        function = Function()
        does_let_have_name = False
        let_name = None
        let_name_internal = self.emitter.create_lambda_name()
        is_global = self.cur_environment.is_global()
        if is_global:
            self.tracker.turn_tracker_on()
        self.emitter.emit_to_section(";start of let args:",is_global)
        #setting up new environment for let
        parent_env = self.cur_environment
        parent_env_depth = self.cur_environment.depth
        previous_function = self.emitter.cur_function
        self.cur_environment = parent_env.create_local_env()
        #if user provided name to let function
        if self.check_token(TokenType.IDENTIFIER):
            print("VARIABLE")
            does_let_have_name = True
            let_name = self.cur_token.text
            self.next_token()
        self.match(TokenType.EXPR_START)
        if let_name is None:
            let_name = let_name_internal
        #setting up block in asm where the function's code will live
        function.set_name(let_name_internal)
        self.emitter.set_current_function(function.name)
        self.cur_environment.set_env_name(function.name)
        self.emitter.emit_function_label(function.name)
        self.emitter.emit_function_prolog()
        arg_count = 1
        
        #add self arg
        self.binding_spec(
        function,let_name,arg_count,parent_env_depth,parent_env,previous_function)
        while not self.check_token(TokenType.EXPR_END):
            arg_count += 1
            self.binding_spec(
            function,let_name,arg_count,parent_env_depth,parent_env,previous_function)
        self.next_token()
        function_ident_obj = Identifier(IdentifierType.FUNCTION,function)
        closure_obj = Identifier(IdentifierType.CLOSURE,function_ident_obj)
        self.emitter.emit_to_section(";before body :D", self.cur_environment.is_global())
        
        #compile body of function
        self.body(function)
        #now switch back to old environment
        self.emitter.set_current_function(previous_function)
        self.cur_environment = parent_env
        if is_global:
            self.tracker.turn_tracker_off()
        #compile function in parent so function obj is in rax.
        #Note: A Closure isnt formed here since in let expressions, the closure 
        # will live internally.
        self.emitter.emit_to_section(";compiling let function:",is_global)
        self.emitter.emit_identifier_to_section(
        closure_obj,self.cur_environment)
        self.add_upvals_to_anon_functions(is_global)
        #now edit self arg to be the closure obj:
        self_arg_offset = self.emitter.push_arg(
        1,self.cur_environment,parent_env_depth,is_global)
        self.emitter.emit_to_section(";^updated self arg",is_global)
        
        #push self arg to live_locals
        self.emitter.subtract_rsp(abs(self.cur_environment.depth),is_global)
        self.emitter.emit_push_live_local(is_global,self_arg_offset)
        self.emitter.add_rsp(abs(self.cur_environment.depth),is_global)
        
        #pop args from live_locals
        self.emitter.emit_to_section(";popping locals let call",is_global)
        self.emitter.pop_live_locals(self.cur_environment,arg_count,False)
        
        #set rax to the let closure
        self.emitter.set_rax_to_local_def(is_global,self_arg_offset)
        
        self.cur_environment.depth = parent_env_depth
        self.emitter.emit_to_section(";starting function call of let",is_global)
        
        is_alignment_needed = self.check_if_alignment_needed(
        parent_env_depth,function.arity)
        #place args
        for cur_arg in range(function.arity):
            if cur_arg < 6:
                self.emitter.emit_register_arg(cur_arg,parent_env_depth,is_global)
            else:
                self.emitter.emit_arg_to_stack(
                cur_arg,parent_env_depth,is_global,function.arity,is_alignment_needed)
        self.emitter.subtract_rsp_given_arity(
        function.arity,parent_env_depth,is_global,is_alignment_needed)
        #Now set rax to be a function obj and call function
        self.emitter.get_function_from_closure_rax(is_global)
        self.emitter.emit_function_call_in_rax(is_global)
        self.emitter.add_rsp_given_arity(
        function.arity,parent_env_depth,is_global,is_alignment_needed)
        self.match(TokenType.EXPR_END)
        self.evaluate_function_call("")
    
    #<binding spec> ::= (<variable> <expression>)  
    def binding_spec(
        self,function,let_name,arg_count,parent_env_depth,parent_env,previous_function):
        print("BINDING-SPEC")
        if arg_count == 1: #self arg
            function.add_param(let_name)
            self.cur_environment.add_definition(let_name,
            Identifier(IdentifierType.CLOSURE,Identifier(IdentifierType.FUNCTION,function)))
            self.emitter.emit_register_param(arg_count)
            child_env = self.cur_environment
            child_function = self.emitter.cur_function
            self.emitter.set_current_function(previous_function)
            self.cur_environment = parent_env
            is_global = self.cur_environment.is_global()
            self.cur_environment.depth -= 8
            #switch back to child environment
            self.emitter.set_current_function(child_function)
            self.cur_environment = child_env
            return
        
        self.match(TokenType.EXPR_START)
        if not self.check_token(TokenType.IDENTIFIER):
            self.abort("Incorrect syntax for binding spec. Expected an identifier.")
        print("VARIABLE")
        function.add_param(self.cur_token.text)
        self.add_param_to_env(arg_count)
        self.next_token()
        #now switch to parent env to process initial value of param, which
        #is result of the expression
        child_env = self.cur_environment
        child_function = self.emitter.cur_function
        self.emitter.set_current_function(previous_function)
        self.cur_environment = parent_env
        
        self.expression()
        is_global = self.cur_environment.is_global()
        
        self.emitter.emit_pass_by_value(self.cur_environment.depth,is_global)
        
        arg_offset = self.emitter.push_arg(
        arg_count,self.cur_environment,parent_env_depth,is_global)
        self.cur_environment.depth -= 8
        
        self.emitter.subtract_rsp(abs(self.cur_environment.depth),is_global)
        self.emitter.emit_push_live_local(is_global,arg_offset)
        self.emitter.add_rsp(abs(self.cur_environment.depth),is_global)
        
        #switch back to child environment
        self.emitter.set_current_function(child_function)
        self.cur_environment = child_env
        self.match(TokenType.EXPR_END)
    
    # (let* (<binding spec>*) <body>)
    def let_star_exp(self):
        print("EXPRESSION-LET*")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.binding_spec()
        self.next_token()
        self.body()
        self.match(TokenType.EXPR_END)
        
    # (letrec (<binding spec>*) <body>)
    def letrec_exp(self):
        print("EXPRESSION-LETREC")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.binding_spec()
        self.next_token()
        self.body()
        self.match(TokenType.EXPR_END)

    # (set! <variable> <expression>)
    def setexclam_exp(self):
        print("EXPRESSION-SET!")
        if not self.check_token(TokenType.IDENTIFIER):
            self.abort("in set!. Expected a variable.")
        print("VARIABLE")
        ident_name = self.cur_token.text
        definition_result = self.resolve_identifier()
        is_global = self.cur_environment.is_global()
        definition = definition_result[0]
        is_upvalue = definition_result[1]
        nest_count = definition_result[2]
        def_ident_obj = Environment.get_ident_obj(definition)
        offset = Environment.get_offset(definition)
        self.next_token()
        self.expression()
        env_depth = self.cur_environment.depth
        if is_upvalue:
            self.emitter.emit_setexclam_upvalue(
            offset,nest_count,env_depth,is_global)
        else:
            self.emitter.set_definition(offset,ident_name,env_depth,is_global)
        self.match(TokenType.EXPR_END)
        
    #(rec <variable> <expression>)
    def rec_exp(self):
        print("EXPRESSION-REC")
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.match(TokenType.EXPR_END)
        
    # (do (<iteration spec>*) (<end test> <sequence>+) <expression>*)
    def do_exp(self):
        print("EXPRESSION-DO")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.iteration_spec()
        self.next_token()
        self.end_test()
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.next_token()

    # (quasiquote <datum>) , but datum is handled differently here. It must 
    # accept unquote and unquote-splicing keywords remember for the emitter that 
    # for unquote, expr must evaluate to a constant, and for unquote-splicing, expr must eval to a list/vector
    def quasiquote_exp(self):
        print("EXPRESSION-QUASIQUOTE")
        self.quasiquote_datum()
        self.match(TokenType.EXPR_END)
        
    # <iteration spec> ::= (<variable> <init> <step>), init and step are expressions
    def iteration_spec(self):
        print("ITERATION-SPEC")
        self.match(TokenType.EXPR_START)
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.expression()
        self.match(TokenType.EXPR_END)

    # (<end test> <sequence>+) , <end test> is an expression
    def end_test(self):
        print("END-TEST")
        self.match(TokenType.EXPR_START)
        self.expression()
        self.expression()
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.next_token()
        
 
    # <cond clause> ::= (<test> <sequence>)
    def cond_clause(self,cur_label,next_label,end_label,condition_count):
        is_global = self.cur_environment.is_global()
        print("COND-CLAUSE")
        self.match(TokenType.EXPR_START)
        print("TEST")
        self.expression()
        self.emitter.emit_false_check(is_global)
        self.emitter.emit_conditional_jump("=",is_global,next_label)
        if condition_count > 1:
            self.emitter.emit_ctrl_label(is_global,cur_label)
        #sequence is now one or more expressions
        print("SEQUENCE")
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.emitter.emit_jump(is_global,end_label)
        self.next_token()
        
    #<case clause> ::= ((<datum>*) <sequence>)
    def case_clause(self):
        print("CASE-CLAUSE")
        self.match(TokenType.EXPR_START)
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.datum()
        self.match(TokenType.EXPR_END)
        self.expression()
        self.match(TokenType.EXPR_END)
   
    # (else <sequence>)     
    def else_rule(self):
        print("ELSE")
        self.match(TokenType.EXPR_START)
        self.match(TokenType.ELSE)
        print("SEQUENCE")
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        self.match(TokenType.EXPR_END)
        
    #<bound var list> ::= <variable> | (<variable>*) | (<variable>+ . <variable>)
    #has similarities to call pattern
    def bound_var_list(self,function):
        print("BOUND-VAR-LIST")
        #lambdas will be anonymous to the user, but internally they have a unique name
        lambda_name = self.emitter.create_lambda_name()
        function.set_name(lambda_name)
        self.emitter.set_current_function(function.name)
        self.cur_environment.set_env_name(function.name)
        self.emitter.emit_function_label(function.name)
        self.emitter.emit_function_prolog()
        #adding self arg, adding to definitions as type CLOSURE instead of PARAM
        #for performance reasons, self arg is guaranteed to be a closure
        function.add_param(function.name)
        self.cur_environment.add_definition(function.name,
        Identifier(IdentifierType.CLOSURE,Identifier(IdentifierType.FUNCTION,function)))
        self.emitter.emit_register_param(1)
            
        if self.check_token(TokenType.IDENTIFIER):
            #lambda form that has a rest argument
            print("VARIABLE")
            function.set_variadic()
            function.add_param(self.cur_token.text)
            self.add_param_to_env(2)
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            arg_count = 1
            self.next_token()
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.DOT):
                    #varargs case
                    print("DOT")
                    if arg_count < 2:
                        self.abort(
                        "in lambda. variadic lambda needs at least one required argument ")
                    function.set_variadic()
                    self.next_token()
                    if not self.check_token(TokenType.IDENTIFIER):
                        self.abort(
                        "Incorrect syntax for bound var list. Illegal use of .")
                    function.add_param(self.cur_token.text)
                    arg_count += 1
                    self.add_param_to_env(arg_count)
                    self.next_token()
                    if not self.check_token(TokenType.EXPR_END):
                        self.abort("Parentheses in bound var list not well formed")
                    break
                elif self.check_token(TokenType.IDENTIFIER):
                    #normal case (plain lambda)
                    print("VARIABLE")
                    function.add_param(self.cur_token.text)
                    arg_count += 1
                    self.add_param_to_env(arg_count)
                    self.next_token()
                else:
                    self.abort("Incorrect syntax in varlist of lambda expression.")
            self.next_token()
        else:
            self.abort("Incorrect syntax in lambda expression, " 
            + self.cur_token.text + " not an identifier.")
      
    # <definition> ::= (define <variable> <expression>) | (define <call pattern> <body>)
    # the define with the call pattern syntax essentially defines a function. 
    # The arg in call pattern is the function name
    #returns name of definition
    def definition_exp(self) -> str:
        print("EXPRESSION-DEFINE")
        ident_name = None
        if self.check_token(TokenType.IDENTIFIER):
            print("VARIABLE")
            ident_name = self.cur_token.text
            is_global = self.cur_environment.is_global()
            #setting start of bss section
            if is_global and self.emitter.first_global_def is None:
                self.emitter.set_first_global_def(ident_name)
            #define label in bss section only if its new var
            if is_global and not self.cur_environment.is_defined(ident_name):
                self.emitter.emit_bss_section(f"\t{ident_name}: resq 1")
                self.emitter.inc_global_var_count(self.cur_environment)
            self.next_token()
            self.expression()
            self.cur_environment.add_definition(ident_name,
            Identifier(self.last_exp_res.typeof,self.last_exp_res.value))
            offset = Environment.get_offset(
            self.cur_environment.symbol_table[ident_name])
            self.emitter.emit_definition(ident_name,self.cur_environment,offset)
            
        elif self.check_token(TokenType.EXPR_START):
            #function case
            function = Function()
            if self.cur_environment.is_global():
                self.tracker.turn_tracker_on()
            parent_env = self.cur_environment
            previous_function = self.emitter.cur_function
            self.cur_environment = parent_env.create_local_env()
            
            self.call_pattern(function)
            self.body(function)
            self.emitter.set_current_function(previous_function)
            #now switch back to parent environment
            ident_name = function.get_name()
            self.cur_environment = parent_env
            
            if self.cur_environment.is_global():
                self.tracker.turn_tracker_off()
                
            function_ident = Identifier(IdentifierType.FUNCTION,function)
            self.evaluate_closure(function_ident)
            #lastly, make function object in the runtime
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment)
            offset = Environment.get_offset(
            self.cur_environment.symbol_table[ident_name])
            self.emitter.emit_definition(ident_name,self.cur_environment,offset)
        else:
            self.abort("Incorrect syntax in definition expression")
            
        self.match(TokenType.EXPR_END)
        return ident_name

    #adds param to current environment and emits if its arg 1-6. 
    #used in call_pattern
    def add_param_to_env(self,arg_count):
        if arg_count < 7:
            self.cur_environment.add_definition(self.cur_token.text,
            Identifier(IdentifierType.PARAM,self.cur_token.text))
            self.emitter.emit_register_param(arg_count)
        else:
            #add stack definition to env. 
            # no need to emit since on the other side of the stack
            self.cur_environment.add_stack_definition(
            self.cur_token.text,(arg_count-5)*8)
            
            
    # <call pattern> ::= (<pattern> <variable>*) | 
    # (<pattern> <variable>* . <variable>) where pattern ::= variable
    # populates Function obj with everything except local definitions and body
    def call_pattern(self,function):
        print("CALL_PATTERN")
        self.match(TokenType.EXPR_START)
        if self.check_token(TokenType.IDENTIFIER):
            print("PATTERN")
            if not self.is_definition_name_okay(self.cur_token.text):
                self.abort("Reserved function name.")
            function.set_name(self.cur_token.text)
            self.emitter.set_current_function(function.name)
            self.cur_environment.set_env_name(function.name)
            if function.name in self.emitter.functions: #for redifining function
                del self.emitter.functions[function.name]
            is_parent_global = self.cur_environment.parent.is_global()
            ident = self.cur_token.text
            #setting start of bss section
            if is_parent_global and self.emitter.first_global_def is None:
                self.emitter.set_first_global_def(ident)

            #declare space in bss section for function obj if function was made
            # from global env
            if is_parent_global and not self.cur_environment.parent.is_defined(ident):
                self.emitter.emit_bss_section(f"\t{ident}: resq 1")
                self.emitter.inc_global_var_count(self.cur_environment.parent)
            self.emitter.emit_function_label(function.name)
            self.emitter.emit_function_prolog()
            self.next_token()
            arg_count = 0
            #for the "self" param, so internally the function can reference its closure
            function.add_param(function.name)
            arg_count += 1
            
            #instead of calling add_param_to_env, add the self param
            #as a closure since type is known at compile time. 
            # This will lead to better performance since runtime doesnt have to 
            # check types for this param.
            self.cur_environment.add_definition(function.name,
            Identifier(IdentifierType.CLOSURE,Identifier(IdentifierType.FUNCTION,function)))
            self.emitter.emit_register_param(arg_count)
            self.emitter.emit_function(";line above is 'self' arg")
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.DOT):
                    print("DOT")
                    function.set_variadic()
                    self.next_token()
                    if not self.check_token(TokenType.IDENTIFIER):
                        self.abort(
                        "Incorrect syntax for call pattern. Illegal use of '.'")
                    function.add_param(self.cur_token.text)
                    arg_count += 1
                    self.add_param_to_env(arg_count)
                    self.next_token()
                    if not self.check_token(TokenType.EXPR_END):
                        self.abort("Parentheses in call pattern not well formed.") 
                    break
                elif self.check_token(TokenType.IDENTIFIER):
                    print("VARIABLE")
                    function.add_param(self.cur_token.text)
                    #now add ALL args to environment and emit only args 1-6
                    arg_count += 1
                    self.add_param_to_env(arg_count)
                    self.next_token()
                else:
                    self.abort(str(self.cur_token.text) + " is not an identifier.")
            self.next_token()
        else:
            self.abort("Incorrect syntax for call pattern.")

    # the definitions are the local variables declared (within the function) 
    # which will be usable in the sequence.
    # <body> ::= <definition>* <sequence>
    def body(self,function):
        print("BODY")
        if self.check_token(TokenType.EXPR_END):
            self.abort("in function definition, empty body.")
            
        #add args to live_locals
        self.emitter.push_args_to_live_locals(function.arity,self.cur_environment)
        #Process all definitions, then call self.expression to create function
        #body
        while self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.DEFINE):
            self.next_token()
            self.next_token()
            definition_name = self.definition_exp()
            function.add_local_definition(definition_name,
            Identifier(self.last_exp_res.typeof,self.last_exp_res.value))
        #add current function to the parent so function can refer to itself
        ident_name = function.get_name()
        parent_env = self.cur_environment.parent
        if parent_env is None:
            self.abort("Cannot get parent of global environment.")
            
        function_ident = Identifier(IdentifierType.FUNCTION,function)
        parent_env.add_definition(ident_name,Identifier(
        IdentifierType.CLOSURE,function_ident))
        
        cur_function = self.emitter.cur_function
        #now current function will supply upvalues that inner functions requested,
        #if no requests, wont do anything
        if self.tracker.function_has_requests(cur_function):
            function_requests = self.tracker.get_upvalue_requests(cur_function)
            for request in function_requests:
                inner_function_def = self.cur_environment.symbol_table[request[0]] 
                inner_function_offset = inner_function_def[0]
                is_captured = inner_function_def[2]
                upvalue_offset = request[1]
                is_local = request[2]
                nest_count = request[3]
                if is_local:
                    #first turn non ptr types to ptr types, then do emit_add_upvalue.
                    #have to set is_captured also
                    if not is_captured:
                        self.emitter.emit_move_local_to_heap(
                        upvalue_offset,self.cur_environment)
                        
                        self.cur_environment.locals_moved_to_heap_count += 1
                        
                        self.cur_environment.set_def_as_captured(request[1])
                    self.emitter.emit_add_upvalue(
                    self.cur_environment,inner_function_offset,upvalue_offset,nest_count)
                else:
                    #search upvalues of current definition instead of locals, add
                    #to target closure
                    self.emitter.emit_add_upvalue_nonlocal(
                    self.cur_environment,inner_function_offset,upvalue_offset,nest_count)
            
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
        live_locals_count = function.arity + len(function.local_definitions) + \
        self.cur_environment.locals_moved_to_heap_count
        self.emitter.emit_to_section(";popping live locals on function exit",self.cur_environment.is_global())
        self.emitter.pop_live_locals(self.cur_environment,live_locals_count)
        self.emitter.emit_function_epilog()
        
    def is_constant(self):
        return self.is_token_any(self.cur_token.type,[TokenType.BOOLEAN,
        TokenType.NUMBER,TokenType.CHAR,TokenType.STRING])
    
    #evaluate_datum,evaluate_list,evaluate_vector evaluate a datnum without
    #emitting asm code
    def evaluate_datum(self):
        if self.is_constant():
            print("CONSTANT")
            self.evaluate_constant()
            self.next_token()
        elif self.check_token(TokenType.IDENTIFIER):
            print("SYMBOL")
            self.evaluate_symbol()
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            print("LIST")
            self.evaluate_list()
        elif self.check_token(TokenType.HASH):
            print("VECTOR")
            self.next_token()
            self.evaluate_vector()
        else:
            self.abort(self.cur_token.text + " Is not a valid datum.")

    #empty list is denoted by Identifier(IdentifierType.PAIR,[])
    #end of list is denoted by a None at the end. If no None at the end, then
    #it fell in to the DOT branch when evaluating list.
    #Note: None value can ONLY appear at the end
    #  # <list> ::= ( <datum>* ) | ( <datum>+ . <datum> )
    def evaluate_list(self):
        self.match(TokenType.EXPR_START)
        datum_list = []
        token_count = 0
        while not self.check_token(TokenType.EXPR_END):
            if self.check_token(TokenType.DOT):
                if token_count < 1:
                    self.abort("Creating a pair requires a car and a cdr.")
                self.next_token()
                self.evaluate_datum()
                datum_list.append(self.last_exp_res)
                break
            else:
                self.evaluate_datum()
                datum_list.append(self.last_exp_res)
                if self.check_token(TokenType.EXPR_END):
                    datum_list.append(None)
                token_count += 1
        self.match(TokenType.EXPR_END)
        self.evaluate_pair(datum_list)
    
    # <vector> ::= #( <datum>* ), starts from (
    def evaluate_vector(self):
        self.match(TokenType.EXPR_START)
        datum_list = []
        while not self.check_token(TokenType.EXPR_END):
            self.evaluate_datum()
            datum_list.append(self.last_exp_res)
        self.match(TokenType.EXPR_END)
        self.set_vector(datum_list)
        
    # starts from parens
    # <list> ::= ( <datum>* ) | ( <datum>+ . <datum> )
    
    
    # def list(self,is_quasi = False):
    #     #since this is not an expression, a list could potentially be deep within an exp, therefore store current amount of parens before processing the list
    #     print("LIST")
    #     num_parens = len(self.parens)
    #     self.parens.append(self.cur_token.text)
    #     token_count = 0
    #     self.next_token()
        
    #     datums = []
    #     is_global = self.cur_environment.is_global()
    #     self.add_extern("allocate_pair")
    #     self.emitter.emit_to_section(f"\tcall allocate_pair\n\tpush rax\n\tpush rax")
        
    #     while not self.check_token(TokenType.EXPR_END):
    #         if self.check_token(TokenType.DOT):
    #             print("DOT")
    #             if token_count < 1:
    #                 self.abort(" Creating a pair requires one or more datums before the " + self.cur_token.text + " token.")
    #             self.next_token()
    #             self.datum() if not is_quasi else self.quasiquote_datum()
                
    #             if not self.check_token(TokenType.EXPR_END):
    #                 self.abort("Incorrect syntax for making pairs.")
    #             # cur_node.set_cdr(self.last_exp_res)
    #             break
    #         else:
    #             self.datum() if not is_quasi else self.quasiquote_datum()
    #             #now set car of current(which is at the top of the stack)
    #             if not self.check_token(TokenType.DOT):
    #                 # cur_node.set_cdr(Identifier(IdentifierType.PAIR,Pair()) if not self.check_token(TokenType.EXPR_END) else None)
    #                 # cur_node = cur_node.get_cdr_value()
    #                 pass
    #             token_count += 1
                
    #     if len(self.parens) != 1 + num_parens:
    #         self.abort("Parentheses in list are not well formed.")
    #     self.parens.pop()
    #     self.evaluate_pair(datums)
    #     self.next_token()
    
    
    
    # <vector> ::= #( <datum>* ), starts from (
    # def vector(self,is_quasi = False):
    #     if not self.check_token(TokenType.EXPR_START):
    #         self.abort("Incorrect syntax for vector.")
    #     print("VECTOR")
    #     num_parens = len(self.parens)
    #     self.parens.append(self.cur_token.text)
    #     self.next_token()
    #     vector = []
    #     while not self.check_token(TokenType.EXPR_END):
    #         if self.check_token(TokenType.EXPR_START) and (self.check_peek(TokenType.UNQUOTE) or self.check_peek(TokenType.UNQUOTESPLICING)):
    #             if not is_quasi:
    #                 self.abort("UNQUOTE and UNQUOTE-SPLICING only valid in quasiquote expression.")
    #             self.next_token()
    #             self.next_token()
    #             self.expression()
    #             self.match(TokenType.EXPR_END)
    #         else:
    #             self.datum() if not is_quasi else self.quasiquote_datum()
    #             vector.append(self.last_exp_res)
        
    #     if len(self.parens) != 1 + num_parens:
    #         self.abort("Parentheses in list are not well formed.")
    #     self.parens.pop()
    #     self.evaluate_vector(vector)
    #     # print("PRINTING VECTOR:")
    #     # [print(ident.typeof,ident.value) for ident in vector]
    #     self.next_token()
    
    #<datum> ::= <constant> | <symbol> | <list> | <vector>
    def datum(self):
        print("DATUM")
        self.evaluate_datum()
        self.emitter.emit_identifier_to_section(self.last_exp_res,
        self.cur_environment)
    
    # (quasiquote <datum>) , but datum is handled differently here. It must accept unquote and unquote-splicing keywords
    # (unquote expr) , (unquote-splicing expr)
    def quasiquote_datum(self):
        print("QUASIDATUM")
        if self.is_constant():
            print("CONSTANT")
            self.next_token()   
        elif self.check_token(TokenType.IDENTIFIER):
            print("SYMBOL")
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            if self.check_peek(TokenType.UNQUOTE) or self.check_peek(TokenType.UNQUOTESPLICING):
                self.next_token()
                self.next_token()
                self.expression()
                self.match(TokenType.EXPR_END)
            else:
                self.list(True)       
        elif self.check_token(TokenType.HASH):
            self.next_token()
            self.vector(True)     
        else:
            self.abort(self.cur_token.text + " Is not a valid datum.")