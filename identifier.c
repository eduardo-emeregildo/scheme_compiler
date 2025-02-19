// gcc -Wall -c -o identifier.o identifier.c
#include "identifier.h"

// for signed 63 bit int: [-2^62, 2^62 - 1]
const long MAX_SCHEME_INT = 0x3fffffffffffffff; 
const long MIN_SCHEME_INT = 0xc000000000000000;
const unsigned long INT_MASK = 0X1;
const unsigned long BOOL_MASK = 0x2;
const unsigned long CHAR_MASK = 0x4;
const unsigned long TAGGED_TYPE_MASK = 0X7;
const unsigned long IS_NEGATIVE_MASK = 0x8000000000000000;
//pass either the 64 bit val or the 64 bit addr(for pointers)
bool is_int(long item) 
{
        return (item & INT_MASK) == 1;
}

bool is_ptr(long item)
{
        return (item & TAGGED_TYPE_MASK) == 0;
}

bool is_bool(long item)
{
        return (item & TAGGED_TYPE_MASK) == 2;
}

// a tagged char is stored in 8 bytes so just pass it as a long
bool is_char(long item)
{
        return (item & TAGGED_TYPE_MASK) == 4;
}

void abort_message(char *error_message)
{
        printf("Error, %s",error_message);
        exit(EXIT_FAILURE);
}

void check_int_range(long num)
{
        if (num > MAX_SCHEME_INT || num < MIN_SCHEME_INT) {
                abort_message("Integer out of range");
        }
}

long make_tagged_int(long num)
{
        check_int_range(num);
        return (num << 1) + 1;
}

long untag_int(long num)
{
        if((num & IS_NEGATIVE_MASK) == 0){
                return (num >> 1);
        } else {
                return (num >> 1) | IS_NEGATIVE_MASK;
        }
}

Value *make_tagged_ptr(size_t num_value_objects)
{
        Value *p = (Value *)malloc(sizeof(Value)*num_value_objects);
        if (p == NULL) {
                abort_message("Ran out of memory or tried to allocate negative bytes.");
        }
        return p;
}

long make_tagged_bool(bool boolean)
{
        return ((long)boolean << 3) | BOOL_MASK;
}

long make_tagged_char(char character)
{
        return ((long)character << 3) | CHAR_MASK;
}

// removes tag for bool,char ONLY. int is handled differently, and we leave ptrs alone
long remove_tag(long tagged_item)
{
        return tagged_item >> 3;
}

void validate_ptr(void *ptr)
{
        if(ptr == NULL){
                abort_message("Ran out of memory.");
        }
}


/*
//////////////////////////////////////////// Heap Objs Below ////////////////////////////////////////////

these next 3 functions should only be used for list/vector elements.
declaring an int,char, or bool that isnt in a vector/list should be done with the
functions above
*/

Value *make_value_int(long integer)
{
        Value *ptr_value_int = make_tagged_ptr(1);
        ptr_value_int->type = VAL_INT;
        ptr_value_int->as.tagged_type = make_tagged_int(integer);
        return ptr_value_int;
}

Value *make_value_char(char character)
{
        Value *ptr_value_char = make_tagged_ptr(1);
        ptr_value_char->type = VAL_CHAR;
        ptr_value_char->as.tagged_type = make_tagged_char(character);
        return ptr_value_char;
}

Value *make_value_bool(bool boolean)
{
        Value *ptr_value_bool = make_tagged_ptr(1);
        ptr_value_bool->type = VAL_BOOLEAN;
        ptr_value_bool->as.tagged_type = make_tagged_bool(boolean);
        return ptr_value_bool;
}

Value *make_empty_list()
{
        Value* ptr_empty_list = make_tagged_ptr(1);
        ptr_empty_list->type = VAL_EMPTY_LIST;
        ptr_empty_list->as.empty_list = NULL;
        return ptr_empty_list;
}

/*
given a character arr(that is declared in a local label), return ptr to 
Str object. symbol types will also use this object
*/
struct Str *allocate_str(char *str)
{
        struct Str *str_obj = (struct Str *)malloc(sizeof(struct Str));
        validate_ptr(str_obj);
        size_t length = strlen(str);
        str_obj->length = length;
        str_obj->chars = str;
        return str_obj;
}


// allocates empty pair
struct Pair *allocate_pair() 
{
        //struct Pair *pair_obj = (struct Pair *)malloc(sizeof(struct Pair));
        struct Pair *pair_obj = (struct Pair *)calloc(1,sizeof(struct Pair));
        validate_ptr(pair_obj);
        pair_obj->car.type = VAL_EMPTY_LIST;
        pair_obj->cdr.type = VAL_EMPTY_LIST;
        return pair_obj; 
}

//takes in array of vector objects that are already allocated to the heap.
struct Vector *allocate_vector(Value *vec_elts,size_t size)
{
        struct Vector *vec_obj = (struct Vector *)malloc(sizeof(struct Vector));
        validate_ptr(vec_obj);
        vec_obj->size = size;
        vec_obj->items = vec_elts;
        return vec_obj;
}

struct FuncObj *allocate_function(void *function_addr,bool is_variadic,int arity)
{
        struct FuncObj *func = (struct FuncObj *)malloc(sizeof(struct FuncObj));
        validate_ptr(func);
        func->function_ptr = function_addr;
        func->is_variadic = is_variadic;
        func->arity = arity;
        return func;
}

struct ClosureObj *allocate_closure(Value *function)
{
        struct ClosureObj *closure = (struct ClosureObj *)malloc(sizeof(struct ClosureObj));
        validate_ptr(closure);
        closure->function = function;
        closure->upvalues = (struct UpvalueObj *)malloc(sizeof(struct UpvalueObj)*4);
        validate_ptr(closure->upvalues);
        closure->num_upvalues = 0;
        return closure;
}
/*
some helpers to help with creation of vec/lists
set_ith_value_x setters can be used to set a pair struct's car/cdr, if you
call them with index = 0
*/
void set_ith_value_int(Value *val_ptr,long integer,size_t index)
{
        val_ptr[index].type = VAL_INT;
        val_ptr[index].as.tagged_type = make_tagged_int(integer);
}

void set_ith_value_char(Value *val_ptr,char character,size_t index)
{
        val_ptr[index].type = VAL_CHAR;
        val_ptr[index].as.tagged_type = make_tagged_char(character);
}

void set_ith_value_bool(Value *val_ptr,bool boolean,size_t index)
{
        val_ptr[index].type = VAL_BOOLEAN;
        val_ptr[index].as.tagged_type = make_tagged_bool(boolean);
}

void set_ith_value_dbl(Value *val_ptr,double num,size_t index)
{
        val_ptr[index].type = VAL_DOUBLE;
        val_ptr[index].as._double = num;
}

void set_ith_value_str(Value *val_ptr,char *str,size_t index)
{
        val_ptr[index].type = VAL_STR;
        val_ptr[index].as.str = allocate_str(str);

}

void set_ith_value_symbol(Value *val_ptr,char *str,size_t index)
{
        val_ptr[index].type = VAL_SYMBOL;
        val_ptr[index].as.str = allocate_str(str);

}

void set_ith_value_pair(Value *val_ptr,struct Pair *pair_obj,size_t index)
{
        val_ptr[index].type = VAL_PAIR;
        val_ptr[index].as.pair = pair_obj;
}

void set_ith_value_empty_list(Value *val_ptr, size_t index)
{
        val_ptr[index].type = VAL_EMPTY_LIST;
        val_ptr[index].as.empty_list = NULL;
}

void set_ith_value_vector(Value *val_ptr,struct Vector *vec,size_t index)
{
        val_ptr[index].type = VAL_VECTOR;
        val_ptr[index].as.vector = vec;
}

void set_ith_value_function(Value *val_ptr,struct FuncObj *func_obj,size_t index)
{
        val_ptr[index].type = VAL_FUNCTION;
        val_ptr[index].as.function = func_obj;

}

void set_ith_value_closure(Value *val_ptr,struct ClosureObj *closure,size_t index)
{
        val_ptr[index].type = VAL_CLOSURE;
        val_ptr[index].as.closure = closure;
}

Value *get_car_ptr(struct Pair *pair_obj)
{
        return &pair_obj->car;
}

Value *get_cdr_ptr(struct Pair *pair_obj)
{
        return &pair_obj->cdr;
}

Value *make_value_double(double num)
{
        Value *ptr_value_double = make_tagged_ptr(1);
        ptr_value_double->type = VAL_DOUBLE;
        ptr_value_double->as._double = num;
        return ptr_value_double;
}

Value *make_value_string(struct Str *str_obj)
{
        Value *ptr_value_string = make_tagged_ptr(1);
        ptr_value_string->type = VAL_STR;
        ptr_value_string->as.str = str_obj;
        return ptr_value_string;
}

Value *make_value_symbol(struct Str *str_obj)
{
        Value *ptr_value_symbol = make_tagged_ptr(1);
        ptr_value_symbol->type = VAL_SYMBOL;
        ptr_value_symbol->as.str = str_obj;
        return ptr_value_symbol;
}

Value *make_value_pair(struct Pair *pair_obj)
{
        Value *ptr_value_pair = make_tagged_ptr(1);
        ptr_value_pair->type = VAL_PAIR;
        ptr_value_pair->as.pair = pair_obj;
        return ptr_value_pair;
}

/* 
input is an array of value objects(that are already alloced on the heap).
returns a Value obj with type pair, as a pair.
the empty list is denoted by car.type = VAL_EMPTY_LIST. 
The end of list is denoted by cdr = VAL_EMPTY_LIST

this function will be used for testing, the assembly program will basically
do what this function does but with manual calls. That way theres no need to deal
with deallocating the array of value objects, 
which is useless after the list is formed
*/
Value *make_value_list(Value *value_obj_array, size_t len)
{       
        Value *ptr_value_list = make_tagged_ptr(1);   
        ptr_value_list->type = VAL_PAIR;
        struct Pair *head = allocate_pair();
        struct Pair *cur_pair = head;
        size_t last_item_index = len - 1; 
        for(size_t i = 0; i < len; i++) {
                cur_pair->car = value_obj_array[i];
                if((i != last_item_index)) {
                        cur_pair->cdr.type = VAL_PAIR;
                        cur_pair->cdr.as.pair = allocate_pair();
                        cur_pair = cur_pair->cdr.as.pair;
                }        
        }
        ptr_value_list->as.pair = head;
        return ptr_value_list;
}

/*
takes in an array of value objects and creates a vector object out of these. 
On the python side, when parsing say #(1 2 3), it will first parse the whole thing
to figure out the length, then allocate the correct arr of value objects.
*/
Value *make_value_vector(Value *value_obj_array, size_t len)
{
        Value *ptr_value_vector = make_tagged_ptr(1); 
        ptr_value_vector->type = VAL_VECTOR;
        struct Vector *vector_obj = allocate_vector(value_obj_array,len);
        ptr_value_vector->as.vector = vector_obj;
        return ptr_value_vector;
}


Value *make_value_function(struct FuncObj *func_obj)
{
        Value *ptr_value_function = make_tagged_ptr(1);
        ptr_value_function->type = VAL_FUNCTION;
        ptr_value_function->as.function = func_obj;
        return ptr_value_function;
}

Value *make_value_closure(struct ClosureObj *closure)
{
        Value *value_closure = make_tagged_ptr(1);
        value_closure->type = VAL_CLOSURE;
        value_closure->as.closure = closure;
        return value_closure;
}

//similar to set_value_x, but in this case its not known if the input is a value
// object or not(i.e. could be a value ptr, or a tagged type(int,bool,char)) 
void set_ith_value_unknown(Value *val_ptr, long type,size_t index) 
{
        if (is_ptr(type)) {
                Value *value_type = (Value *)type;
                val_ptr[index] = *value_type;
                return;
        }
        if (is_int(type)) {
                val_ptr[index].type = VAL_INT;
                val_ptr[index].as.tagged_type = type;
        } else if (is_bool(type)) {
                val_ptr[index].type = VAL_BOOLEAN;
                val_ptr[index].as.tagged_type = type;
        } else if (is_char(type)) {
                val_ptr[index].type = VAL_CHAR;
                val_ptr[index].as.tagged_type = type;
        } else {
                abort_message("in set_ith_value_unknown. Type is unknown.\n");
        }

}
//turns into an int,bool or char and sets this to the Value obj given.
void turn_to_val_type(long non_ptr_type,Value *val_obj)
{       
        if (is_int(non_ptr_type)) {
                val_obj->type = VAL_INT;
        } else if (is_bool(non_ptr_type)) {
                val_obj->type = VAL_BOOLEAN;
        } else if (is_char(non_ptr_type)) {
                val_obj->type = VAL_CHAR;
        } else {
                abort_message("not a non pointer type.\n");
        }
        val_obj->as.tagged_type = non_ptr_type;
}

bool is_non_ptr_type(Value *val_type)
{       
        int type = val_type->type;
        if (type == VAL_INT || type == VAL_CHAR || type == VAL_BOOLEAN) {
                return true;
        }
        return false;
}

/*
performs runtime checks on a param that was used as a function. checks if the 
function is variadic, returns a list of the varargs if so.
Otherwise returns null ptr indicating that the param is non variadic

since check_if_callable is called before this function, it doesnt have to check
if object is a function
*/
Value *check_param_function_call(Value *func_obj,long *args,int arg_amount)
{
        //Value *func_obj = (Value *)function;
        // if (!is_ptr(function) || (func_obj->type != VAL_FUNCTION)) {
        //         abort_message("application not a procedure.");
        // }
        int function_arity = func_obj->as.function->arity;
        if (func_obj->as.function->is_variadic) {
                // variadic logic
                int min_args = function_arity - 1;
                if (arg_amount < (min_args)) {
                        printf(
                        "Runtime error, arity mismatch: Number of args does"\
                        " not match. Expected at least %d, given %d.\n",
                        min_args,arg_amount);
                        exit(EXIT_FAILURE);
                }
                return make_arg_list(func_obj,args,arg_amount);

        } else if (function_arity != arg_amount) {
                printf(
                "Runtime error, arity mismatch: Number of args does not match."\
                " Expected %d, given %d.\n",function_arity,arg_amount);
                exit(EXIT_FAILURE);
        }
        return NULL;
}

// checks if type is callable, i.e. a function or a closure. If its a closure,
//returns the function obj of closure, if its a function obj, returns itself,
//otherwise throw error
Value *check_if_callable(long type)
{
        if (!is_ptr(type)) {
                abort_message("application not a procedure.\n");
        }
        Value * value_type = (Value *)type;
        if (value_type->type == VAL_FUNCTION) {
                return value_type;
        } else if (value_type->type == VAL_CLOSURE) {
                return value_type->as.closure->function;
        } else {
                abort_message("application not a procedure.\n");
        }

}
/*
makes the pair obj containing the varargs. iterates the args array backwards.
*/
Value *make_arg_list(Value *func_obj,long *args,int arg_amount)
{       
        Value *vararg_list = make_tagged_ptr(1);
        int min_args = func_obj->as.function->arity - 1;
        //no args, so return empty list
        if (arg_amount == min_args) {               
                vararg_list->type = VAL_EMPTY_LIST;
                vararg_list->as.empty_list = NULL;
                return vararg_list;
        }
        int varargs_index = (arg_amount  - 1)  - min_args;
        vararg_list->type = VAL_PAIR;
        struct Pair *head = allocate_pair();
        struct Pair *cur_pair = head;
        for (int i = varargs_index; i > -1;i--) {
                if (is_ptr(args[i])) {
                        cur_pair->car = *(Value *)args[i];
                } else {
                        turn_to_val_type(args[i],&cur_pair->car);
                }
                if (i != 0) {
                        cur_pair->cdr.type = VAL_PAIR;
                        cur_pair->cdr.as.pair = allocate_pair();
                        cur_pair = cur_pair->cdr.as.pair;
                }
        }
        vararg_list->as.pair = head;
        return vararg_list;
}

/* 
same as make_arg_list except min_args is already known at compile time, so can
pass that instead of the function object
*/
Value *make_arg_list_min_args(int min_args,long *args,int arg_amount)
{       
        Value *vararg_list = make_tagged_ptr(1);
        //no args, so return empty list
        if (arg_amount == min_args) {               
                vararg_list->type = VAL_EMPTY_LIST;
                vararg_list->as.empty_list = NULL;
                return vararg_list;
        }
        int varargs_index = (arg_amount  - 1)  - min_args;
        vararg_list->type = VAL_PAIR;
        struct Pair *head = allocate_pair();
        struct Pair *cur_pair = head;
        for (int i = varargs_index; i > -1;i--) {
                if (is_ptr(args[i])) {
                        cur_pair->car = *(Value *)args[i];
                } else {
                        turn_to_val_type(args[i],&cur_pair->car);
                }
                if (i != 0) {
                        cur_pair->cdr.type = VAL_PAIR;
                        cur_pair->cdr.as.pair = allocate_pair();
                        cur_pair = cur_pair->cdr.as.pair;
                }
        }
        vararg_list->as.pair = head;
        return vararg_list;
}

void add_upvalue(Value *closure,long value, int offset)
{
        if (closure->type != VAL_CLOSURE) {
                abort_message("adding upvalue, not a closure.\n");
        }
        //check size of upvalues, if multiple of 4, resize
        int upvalue_count = closure->as.closure->num_upvalues; 
        if (upvalue_count != 0 && (upvalue_count & 0x3 == 0)) {
                printf("Resizing:\n");
                int new_size = sizeof(struct UpvalueObj) * ((upvalue_count) * 2);
                struct UpvalueObj* new_upvalues = (struct UpvalueObj *)malloc(new_size);
                memcpy(new_upvalues,closure->as.closure->upvalues,upvalue_count);
                free(closure->as.closure->upvalues);
                closure->as.closure->upvalues = new_upvalues;
        }
        closure->as.closure->upvalues[upvalue_count].offset = offset;
        closure->as.closure->upvalues[upvalue_count].value = value;
        closure->as.closure->num_upvalues++;
}

long get_upvalue()
{
        //implement
}