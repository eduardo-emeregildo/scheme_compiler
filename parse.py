import sys
from lex import *
from emit import *
from environment import *
from function import *
from scheme_builtins import *

#make all user defined functions so that they can reference themselves. I think it
#has to be implicitly passed. What you are passing is the closure object.

#start implementing adding upvalues/retrieving them
#first handle normal closures, then handle the anonymous ones (i.e. lambda/let)
#how will lambdas search for upvalues??? 

#Todo4: implement closures
#Todo5: implement gc
#Todo6: test compiler with different optimization levels, see which one you can
#get away with
#Todo7: Add some macros for casting to improve readability
#Todo8: implement list procedure

#Todo's in the future:
# 1. implement string interning
# 2. implement tail call optimization
# 3. have display print out special characters, i.e. \n,\t etc
# 4. imports
# 5. have a "debug" mode where it prints all the symbols,terminals,nonterminals
    
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
    
    #sets last_exp_res to a vector. Might need to rename other functions above
    #to have set in the name instead of evaluate
    def set_vector(self,vector_obj):
        self.set_last_exp_res(IdentifierType.VECTOR,vector_obj)
        
    def program(self):
        print("Program")
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
        #Parse all expressions in the program
        while not self.check_token(TokenType.EOF):
            self.expression()
        # self.emitter.emit_global_definitions(self.global_environment.symbol_table)
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
            is_global = self.cur_environment.is_global()
            definition_result = self.cur_environment.find_definition(
            self.cur_token.text)
            definition = definition_result[0]
            is_upvalue = definition_result[1]
            def_ident_obj = Environment.get_ident_obj(definition)
            print("DEFINITION IS: ",definition)
            print("is_upvalue is: ",is_upvalue)
            self.set_last_exp_res(def_ident_obj.typeof,def_ident_obj.value)
            # if is_upvalue:
            #     print("in is_upvalue, cur_function is: ",self.emitter.cur_function)
            #     #search upvalue and put result in rax
            #     #how can i reference the exact closure obj that was defined in
            #     #outer? 
            #     #perhaps its own closure obj should be added as a param
            #     #this would then be how all functions refer to their own object
            
            if is_global:
                self.emitter.emit_var_to_global(self.cur_token.text,definition)
            else:
                self.emitter.emit_var_to_local(self.cur_token.text,definition)
            self.next_token()
                    
        elif self.check_token(TokenType.QUOTE_SYMBOL):
            print("EXPRESSION-QUOTE-SYMBOL")
            self.next_token()
            self.datum()
        
        elif self.check_token(TokenType.BUILTIN):
            print("BUILTIN")
            is_global = self.cur_environment.is_global()
            builtin_function = BUILTINS[self.cur_token.text]
            self.emitter.add_extern(self.cur_token.text)
            self.emitter.emit_builtin_function(self.cur_token.text,is_global)
            self.set_last_exp_res(IdentifierType.FUNCTION,builtin_function)
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
                #self.parens.pop()
                
            # (delay <expression>)
            elif self.check_token(TokenType.DELAY):
                self.next_token()
                print("EXPRESSION-DELAY")
                self.expression()
                self.match(TokenType.EXPR_END)
                #self.parens.pop()
            
            elif self.check_token(TokenType.DO):
                self.next_token()
                self.do_exp()
                
            elif self.check_token(TokenType.QUASIQUOTE):
                self.next_token()
                self.quasiquote_exp()
            #<procedure call> ::= (<operator> <operand>*)
            #first exp must be an ident_obj of type function
            else:
                print("EXPRESSION-PROCEDURECALL")
                print("OPERATOR")
                self.expression()
                if self.last_exp_res.typeof == IdentifierType.CLOSURE:
                    print("CLOSURE :DDDDDDDDD")
                    #load the function value ptr in rax.
                    is_global = self.cur_environment.is_global()
                    self.emitter.get_function_from_closure(is_global)
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
    # is being used. The function object is in rax.
    def general_function_call(self):
        print("GENERAL FUNCTION CALL")
        is_global = self.cur_environment.is_global()
        arg_count = 0
        self.emitter.emit_to_section(
        ";general function call start",self.cur_environment.is_global())
        #save rax temporarily to perform checks on it later
        self.emitter.save_rax(self.cur_environment)
        env_depth = self.cur_environment.depth
        #evaluates the args
        while not self.check_token(TokenType.EXPR_END):
            print("OPERAND")
            arg_count += 1
            self.expression()
            self.emitter.push_arg(arg_count,env_depth,is_global)
            self.cur_environment.depth -= 8
        self.cur_environment.depth += 8*arg_count
        
        # now perform runtime checks to see if  operator is a function/ 
        # what kind of function
        self.emitter.emit_function_check(self.cur_environment,env_depth,arg_count)
        self.emitter.emit_variadic_check(is_global)
        variadic_label = self.emitter.emit_conditional_jump("!=",is_global)
        #now put args in the right place for non variadic case
        #-8 is offset of last arg (assuming env depth is 0)
        for cur_arg in range(arg_count):
            if cur_arg < 6:                
                self.emitter.emit_register_arg(cur_arg,env_depth,is_global)
            else:
                self.emitter.emit_arg_to_stack(
                cur_arg,env_depth,is_global,arg_count)
        self.emitter.emit_to_section("\t;finished putting args non variadic",is_global)
        #advance rsp to point to 7th arg, if less than 7 args, advance rsp so 
        # local defs arent overwritten
        self.emitter.subtract_rsp_given_arity(arg_count,env_depth,is_global)
        #now call the function
        self.emitter.emit_function_call(env_depth,is_global)
        self.emitter.add_rsp_given_arity(arg_count,env_depth,is_global)
        #this jmp goes to rest of function
        rest_of_function_label = self.emitter.emit_jump(is_global)
        #variadic branch:
        self.emitter.emit_param_variadic_call(
        variadic_label,env_depth,env_depth,is_global)
        self.emitter.emit_ctrl_label(is_global,rest_of_function_label)
        self.emitter.undo_save_rax(self.cur_environment)
        self.evaluate_function_call("")
        self.next_token()
        
    #places args in correct registers for function call and emits a function call
    #This is a helper for function_call.
    def place_args_and_call_function(
        self,env_depth,is_global,arg_count,func_obj,is_builtin):
        for cur_arg in range(arg_count):
            if cur_arg < 6:
                self.emitter.emit_register_arg(
                cur_arg,env_depth,is_global,arg_count)
            else:
                seventh_arg_offset =  abs(env_depth - (arg_count - 6)*8)
                self.emitter.subtract_rsp(seventh_arg_offset,is_global)
                break
        # for calls where no args are on the stack, subtract ONLY the depth if
        # there is stuff to preserve on the stack(AKA if depth != 0)
        if arg_count < 6:
            self.emitter.subtract_rsp(abs(env_depth),is_global)
        if is_builtin:
            self.emitter.emit_builtin_call(func_obj.name,is_global)
        else:
            self.emitter.emit_function_call(env_depth,is_global)
        #add back the rsp
        if arg_count > 6:
            self.emitter.add_rsp(seventh_arg_offset,is_global)
        else:
            self.emitter.add_rsp(abs(env_depth),is_global)
        #self.emitter.undo_save_rax(self.cur_environment)
        #self.evaluate_function(func_obj) 
        # not sure if i need a function call to set last_exp_res ill keep this
        #commented out for now
    
    #given a function object, does a function call. last_exp_res will be set to
    #the function that was called
    def function_call(self,func_obj):
        print("FUNCTION CALL")
        is_builtin = False
        if func_obj.name in BUILTINS:
            is_builtin = True
        if not is_builtin:
            self.emitter.save_rax(self.cur_environment)
        arg_count = 0
        is_global = self.cur_environment.is_global()
        env_depth = self.cur_environment.depth
        #subtract environment's depth temporarily to compute the args without 
        #overwritting the stack,i.e. the local definitions
        self.cur_environment.depth -= func_obj.arity*8
        while not self.check_token(TokenType.EXPR_END):
            print("OPERAND")
            arg_count += 1
            if arg_count > func_obj.arity:
                break
            self.expression()
            #push each arg to the stack so that they're stored while evaluating each arg
            self.emitter.push_arg(arg_count,env_depth,is_global,func_obj.arity)
        self.cur_environment.depth += func_obj.arity*8
        if arg_count != func_obj.arity:
                self.abort(f"Arity mismatch. Function " + 
                f"{func_obj.name} requires {str(func_obj.arity)} arguments.")
        self.place_args_and_call_function(
        env_depth,is_global,arg_count,func_obj,is_builtin)
        if not is_builtin:
            self.emitter.undo_save_rax(self.cur_environment)
        self.evaluate_function_call(func_obj.name)
        self.next_token()
    
    def variadic_function_call(self,func_obj):
        print("VARIADIC FUNCTION CALL")
        is_builtin = False
        if func_obj.name in BUILTINS:
            is_builtin = True
        if not is_builtin:
            self.emitter.save_rax(self.cur_environment)
        arg_count = 0
        is_global = self.cur_environment.is_global()
        old_env_depth = self.cur_environment.depth
        min_args = func_obj.arity - 1
        variadic_args = []
        #push args to stack to store while each arg gets evaluated
        while not self.check_token(TokenType.EXPR_END):
            arg_count += 1
            self.expression()
            self.emitter.push_arg(arg_count,old_env_depth,is_global)
            self.cur_environment.depth -= 8
        if arg_count < min_args:
            self.abort(f"Arity mismatch. {func_obj.name} requires at least" + 
            f" {min_args} arguments")
        #now make varargs list
        self.emitter.emit_make_arg_list(
        min_args,func_obj.arity,arg_count,old_env_depth,is_global)
        self.cur_environment.depth = old_env_depth
        #place args in the right spot
        for cur_arg in range(func_obj.arity):
            if cur_arg < 6:                
                self.emitter.emit_register_arg(cur_arg,old_env_depth,is_global)
            else:
                self.emitter.emit_arg_to_stack(
                cur_arg,old_env_depth,is_global,func_obj.arity)
        self.emitter.subtract_rsp_given_arity(func_obj.arity,old_env_depth,is_global)
        #now call function
        if is_builtin:
            self.emitter.emit_builtin_call(func_obj.name,is_global)
        else:
            self.emitter.emit_function_call(old_env_depth,is_global)
        self.emitter.add_rsp_given_arity(func_obj.arity,old_env_depth,is_global)
        if not is_builtin:
            self.emitter.undo_save_rax(self.cur_environment)
        self.evaluate_function_call(func_obj.name)
        self.next_token()
        
        
    #(if <test> <consequent> <alternate>) | (if <test> <consequent>), where test,consequent and alternate are expressions
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
        parent_env = self.cur_environment
        previous_function = self.emitter.cur_function
        self.cur_environment = parent_env.create_local_env()
        self.bound_var_list(function)
        self.body(function)
        #now switch back to parent environment/ previous function
        self.emitter.set_current_function(previous_function)
        self.cur_environment = parent_env
        #self.evaluate_function(function)
        function_ident = Identifier(IdentifierType.FUNCTION,function)
        self.evaluate_closure(function_ident)
        self.emitter.emit_identifier_to_section(self.last_exp_res,self.cur_environment)
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
            
    #(case <expression> <case clause>*) | (case <expression> <case clause>* (else <sequence>))  #<case clause> ::= ((<datum>*) <sequence>)       
    def case_exp(self):
        print("EXPRESSION-CASE")
        self.expression()
        
        if self.check_token(TokenType.EXPR_END):
            #self.parens.pop()
            self.next_token()
            
        elif self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
            self.else_rule()
            self.match(TokenType.EXPR_END)
            #self.parens.pop()
        
        # one or more case clauses and an optional else at the end
        else:
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.EXPR_START) and self.check_peek(TokenType.ELSE):
                    self.else_rule()
                    break
                self.case_clause()
            self.match(TokenType.EXPR_END)
            #self.parens.pop()
    
    # (let (<binding spec>*) <body>) | (let <variable> (<binding spec>*) <body>) 
    def let_exp(self):
        print("EXPRESSION-LET")
        function = Function()
        does_let_have_name = False
        let_name = None
        let_name_internal = self.emitter.create_lambda_name() 
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
            # self.emitter.emit_definition(ident_name,is_global,offset)
            self.next_token()
        self.match(TokenType.EXPR_START)
        if let_name is None:
            let_name = let_name_internal
        #setting up block in asm where the function's code will live
        function.set_name(let_name_internal)
        self.emitter.set_current_function(function.name)
        self.emitter.emit_function_label(function.name)
        self.emitter.emit_function_prolog()
        arg_count = 0
        while not self.check_token(TokenType.EXPR_END):
            arg_count += 1
            self.binding_spec(function,arg_count,parent_env_depth,parent_env,previous_function)
        self.next_token()
        function_ident_obj = Identifier(IdentifierType.FUNCTION,function)
        closure_obj = Identifier(IdentifierType.CLOSURE,function_ident_obj)
        self.emitter.emit_to_section(";before body :D", self.cur_environment.is_global())
        
        #compile and add itself to its environment so it can reference itself
        #and variables it stored in the closure. In the case where user did not
        #give the let a name, searching for upvalues is probably going to be done
        #differently
        self.emitter.emit_identifier_to_section(closure_obj,self.cur_environment)
        #add definition (uses let_name because this is name we want to look up)
        #self.cur_environment.add_definition(let_name,function_ident_obj)
        self.cur_environment.add_definition(let_name,closure_obj)
        offset = Environment.get_offset(self.cur_environment.symbol_table[let_name])
        self.emitter.emit_definition(function.name,self.cur_environment.is_global(),offset)
        
        #compile body of function
        self.body(function)
        #now switch back to old environment
        self.emitter.set_current_function(previous_function)
        self.cur_environment = parent_env
        is_global = self.cur_environment.is_global()
        #compile function in parent so function obj is in rax.
        #Note: A Closure isnt formed here since in let expressions, the closure 
        # will live internally.
        self.emitter.emit_to_section(";compiling let function:",is_global)
        self.emitter.emit_identifier_to_section(function_ident_obj,self.cur_environment)
        
        self.cur_environment.depth = parent_env_depth
        self.emitter.emit_to_section(";starting function call of let",is_global)
        #place args
        for cur_arg in range(function.arity):
            if cur_arg < 6:
                self.emitter.emit_register_arg(cur_arg,parent_env_depth,is_global)
            else:
                self.emitter.emit_arg_to_stack(
                cur_arg,parent_env_depth,is_global,function.arity)
        self.emitter.subtract_rsp_given_arity(function.arity,parent_env_depth,is_global)
        #Now call function(the function obj is already in rax)
        self.emitter.emit_function_call_in_rax(is_global)
        self.emitter.add_rsp_given_arity(function.arity,parent_env_depth,is_global)
        self.match(TokenType.EXPR_END)
        self.evaluate_function_call("")
    
    #<binding spec> ::= (<variable> <expression>)  
    def binding_spec(
    self,function,arg_count,parent_env_depth,parent_env,previous_function):
        print("BINDING-SPEC")
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
        self.emitter.push_arg(arg_count,parent_env_depth,is_global)
        self.cur_environment.depth -= 8
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
        #self.parens.pop()
        
    # (letrec (<binding spec>*) <body>)
    def letrec_exp(self):
        print("EXPRESSION-LETREC")
        self.match(TokenType.EXPR_START)
        while not self.check_token(TokenType.EXPR_END):
            self.binding_spec()
        self.next_token()
        self.body()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()

    # (set! <variable> <expression>)
    def setexclam_exp(self):
        print("EXPRESSION-SET!")
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
        
    #(rec <variable> <expression>)
    def rec_exp(self):
        print("EXPRESSION-REC")
        self.match(TokenType.IDENTIFIER)
        print("VARIABLE")
        self.expression()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
        
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
        #self.parens.pop()
        self.next_token()

    # (quasiquote <datum>) , but datum is handled differently here. It must accept unquote and unquote-splicing keywords
    #remember for the emitter that for unquote, expr must evaluate to a constant, and for unquote-splicing, expr must eval to a list/vector
    def quasiquote_exp(self):
        print("EXPRESSION-QUASIQUOTE")
        self.quasiquote_datum()
        self.match(TokenType.EXPR_END)
        #self.parens.pop()
        
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
        self.emitter.emit_function_label(function.name)
        self.emitter.emit_function_prolog()
        if self.check_token(TokenType.IDENTIFIER):
            #lambda form that has a rest argument
            print("VARIABLE")
            function.set_variadic()
            function.add_param(self.cur_token.text)
            self.add_param_to_env(1)
            self.next_token()
        elif self.check_token(TokenType.EXPR_START):
            arg_count = 0
            self.next_token()
            while not self.check_token(TokenType.EXPR_END):
                if self.check_token(TokenType.DOT):
                    #varargs case
                    print("DOT")
                    if arg_count < 1:
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
            #define label in bss section only if its new var
            if is_global and not self.cur_environment.is_defined(ident_name):
                self.emitter.emit_bss_section(f"\t{ident_name}: resq 1")                    
            self.next_token()
            self.expression()
            self.cur_environment.add_definition(ident_name,
            Identifier(self.last_exp_res.typeof,self.last_exp_res.value))
            offset = Environment.get_offset(
            self.cur_environment.symbol_table[ident_name])
            self.emitter.emit_definition(ident_name,is_global,offset)
            
        elif self.check_token(TokenType.EXPR_START):
            #function case
            function = Function()
            parent_env = self.cur_environment
            previous_function = self.emitter.cur_function
            self.cur_environment = parent_env.create_local_env()
            
            self.call_pattern(function)
            self.body(function)
            self.emitter.set_current_function(previous_function)
            #now switch back to parent environment
            ident_name = function.get_name()
            self.cur_environment = parent_env
            function_ident = Identifier(IdentifierType.FUNCTION,function)
            self.evaluate_closure(function_ident)
            #lastly, make function object in the runtime
            self.emitter.emit_identifier_to_section(self.last_exp_res,
            self.cur_environment)
            is_global = self.cur_environment.is_global()
            offset = Environment.get_offset(
            self.cur_environment.symbol_table[ident_name])
            self.emitter.emit_definition(ident_name,is_global,offset)
        else:
            self.abort("Incorrect syntax in definition expression")
            
        self.match(TokenType.EXPR_END)
        # self.last_exp_res = None # since definitions arent exps
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
            if not self.emitter.is_definition_name_okay(self.cur_token.text):
                self.abort("Reserved function name.")
            function.set_name(self.cur_token.text)
            self.emitter.set_current_function(function.name)
            if function.name in self.emitter.functions: #for redifining function
                del self.emitter.functions[function.name]
            #declare space in bss section for function obj if function was made
            # from global env
            is_parent_global = self.cur_environment.parent.is_global()
            ident = self.cur_token.text
            if is_parent_global and not self.cur_environment.parent.is_defined(ident):
                self.emitter.emit_bss_section(f"\t{ident}: resq 1")
            self.emitter.emit_function_label(function.name)
            self.emitter.emit_function_prolog()
            self.next_token()
            arg_count = 0
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
        while not self.check_token(TokenType.EXPR_END):
            self.expression()
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
        #is_global = self.cur_environment.is_global()
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