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
//#define DEBUG_SYMBOLS_GC
//these are to determine when the gc should be called
int bytes_allocated = 0;
int next_gc = 2048;
#define LIVE_LOCAL_MAX 256
#define GC_HEAP_GROW_FACTOR 2;

/*
live_locals is a stack to track the locals that are currently in use. the main 
usage of this is so that during collect_garbage, all the locals that the gc will
keep will be in here.
*/
Value *live_locals[LIVE_LOCAL_MAX];
int live_locals_top = 0; // points to slot where next push will go to

//pointers for linked list of objects
Object *head = NULL;
Object *tail = NULL;

long global_var_count = 0;

//these are used to track gray objects in the mark sweep algo
int gray_count = 0;
int gray_capacity = 0;
Value **gray_stack = NULL;
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
        Value *p = (Value *)calloc(num_value_objects,sizeof(Value));
        if (p == NULL) {
                abort_message("Ran out of memory or tried to allocate negative bytes.");
        }
        bytes_allocated += sizeof(Value) * num_value_objects;
        add_object(p);
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
        bytes_allocated += sizeof(struct Str);
        size_t length = strlen(str);
        str_obj->length = length;
        str_obj->chars = str;
        return str_obj;
}


// allocates empty pair
struct Pair *allocate_pair() 
{
        struct Pair *pair_obj = (struct Pair *)calloc(1,sizeof(struct Pair));
        validate_ptr(pair_obj);
        bytes_allocated += sizeof(struct Pair);
        pair_obj->car.type = VAL_EMPTY_LIST;
        pair_obj->cdr.type = VAL_EMPTY_LIST;
        return pair_obj; 
}

//takes in array of vector objects that are already allocated to the heap.
struct Vector *allocate_vector(Value *vec_elts,size_t size)
{
        struct Vector *vec_obj = (struct Vector *)malloc(sizeof(struct Vector));
        validate_ptr(vec_obj);
        bytes_allocated += sizeof(struct Vector);
        vec_obj->size = size;
        vec_obj->items = vec_elts;
        return vec_obj;
}

struct FuncObj *allocate_function(void *function_addr,bool is_variadic,int arity)
{
        struct FuncObj *func = (struct FuncObj *)malloc(sizeof(struct FuncObj));
        validate_ptr(func);
        bytes_allocated += sizeof(struct FuncObj);
        func->function_ptr = function_addr;
        func->is_variadic = is_variadic;
        func->arity = arity;
        return func;
}

struct ClosureObj *allocate_closure(Value *function)
{
        struct ClosureObj *closure = (struct ClosureObj *)malloc(sizeof(struct ClosureObj));
        validate_ptr(closure);
        bytes_allocated += sizeof(struct ClosureObj);
        closure->function = function;
        closure->upvalues = (struct UpvalueObj *)malloc(sizeof(struct UpvalueObj)*4);
        validate_ptr(closure->upvalues);
        bytes_allocated += sizeof(struct UpvalueObj) * 4;
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
        Value *ptr_value_closure = make_tagged_ptr(1);
        ptr_value_closure->type = VAL_CLOSURE;
        ptr_value_closure->as.closure = closure;
        return ptr_value_closure;
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
void turn_to_val_type(long non_ptr_type, Value *val_obj)
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

//if local is a non_ptr, moves it to the heap by making it a value type.
//if its already a value type, return the type
long move_local_to_heap(long local)
{
        //if already on the heap
        if (is_ptr(local)) {
                push_to_live_local((Value *)local);
                return local;
        }
        Value* local_heap = make_tagged_ptr(1);
        turn_to_val_type(local,local_heap);
        push_to_live_local(local_heap);
        return (long)local_heap;
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
if value type is int,char,bool, turns it back into a non_ptr_type and returns.
otherwise returns the value_type.
this is used when turning a captured local thats a int,char,bool back into non_ptr
type
*/ 
long turn_to_non_ptr_type(Value *ptr_type)
{
        int type = ptr_type->type;
        if (type == VAL_INT || type == VAL_CHAR || type == VAL_BOOLEAN) {
                return ptr_type->as.tagged_type;
        }
        return (long)ptr_type;
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

// checks if type is callable, i.e if its a closure. If its a closure,
//returns the function obj of closure, otherwise throws an error
Value *check_if_callable(long type)
{
        if (!is_ptr(type)) {
                abort_message("application not a procedure\n");
        }
        Value *value_type = (Value *)type;
        if (value_type->type != VAL_CLOSURE) {
                abort_message("application not a procedure\n");
        }
        return value_type->as.closure->function;
}

bool is_closure(long type)
{
        if (is_ptr(type) && ((Value *)type)->type == VAL_CLOSURE) {
                return true;
        }
        return false;
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
                        value_deep_copy(&cur_pair->car,((Value *)args[i]));
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
                        value_deep_copy(&cur_pair->car,((Value *)args[i]));

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

//if arg is a value type, creates a copy to pass by value.
long pass_by_value(long arg)
{
        if (!is_ptr(arg)) {
                return arg;
        }

        Value *copy = make_tagged_ptr(1);
        value_deep_copy(copy,(Value *)arg);
        return (long)copy;
}

//does a deep copy of val_type. copy is what gets edited
void value_deep_copy(Value *copy,Value* val_obj)
{
        copy->type = val_obj->type;
        switch(copy->type) {
        case VAL_STR:
                struct Str *str_copy = allocate_str(val_obj->as.str->chars);
                copy->as.str = str_copy;
                break;
        case VAL_SYMBOL:
                struct Str *symbol_str_copy = allocate_str(val_obj->as.str->chars);
                copy->as.str = symbol_str_copy;
                break;
        case VAL_PAIR:
                struct Pair *pair_copy = allocate_pair();
                value_deep_copy(&pair_copy->car,&val_obj->as.pair->car);
                value_deep_copy(&pair_copy->cdr,&val_obj->as.pair->cdr);
                copy->as.pair = pair_copy;
                break;
        case VAL_VECTOR:
                Value *vec_items_copy = make_tagged_ptr(val_obj->as.vector->size);
                int size = val_obj->as.vector->size;
                for (int i = 0 ;i < size; i++) {
                        value_deep_copy(&vec_items_copy[i],&val_obj->as.vector->items[i]);
                        
                }
                struct Vector *vector_copy = allocate_vector(vec_items_copy,size);
                copy->as.vector = vector_copy;
                break;
        case VAL_FUNCTION:
                void *function_addr = val_obj->as.function->function_ptr;
                bool is_variadic = val_obj->as.function->is_variadic;
                int arity = val_obj->as.function->arity;
                struct FuncObj *function_copy = allocate_function(function_addr,is_variadic,arity);
                copy->as.function = function_copy;
                break;
        case VAL_CLOSURE:
                Value *function = make_tagged_ptr(1);
                value_deep_copy(function,val_obj->as.closure->function);
                struct ClosureObj *closure_copy = allocate_closure(function);
                copy->as.closure = closure_copy;
                int num_upvalues = val_obj->as.closure->num_upvalues;
                //deep copy of upvalue array
                for (int i = 0; i < num_upvalues; i++) {
                        int nesting_count = val_obj->as.closure->upvalues[i].nesting_count;
                        int offset = val_obj->as.closure->upvalues[i].offset;
                        Value *upvalue_copy = make_tagged_ptr(1);
                        value_deep_copy(upvalue_copy,(Value *)val_obj->as.closure->upvalues[i].value);
                        add_upvalue(copy,(long)upvalue_copy,offset,nesting_count);
                }
                break;
        default:
                copy->as.tagged_type = val_obj->as.tagged_type;
        }
}

Value *add_upvalue(Value *closure,long value, int offset, int nesting_count)
{
        if (closure->type != VAL_CLOSURE) {
                abort_message("adding upvalue, not a closure.\n");
        }
        //check size of upvalues, if multiple of 4, resize
        int upvalue_count = closure->as.closure->num_upvalues; 
        if (upvalue_count != 0 && ((upvalue_count & 0x3) == 0)) {
                #ifdef DEBUG_SYMBOLS_GC
                        printf("Resizing:\n");
                #endif
                int new_size = sizeof(struct UpvalueObj) * ((upvalue_count) * 2);

                bytes_allocated -= (sizeof(struct UpvalueObj) *upvalue_count);
                struct UpvalueObj* new_upvalues = (struct UpvalueObj *)malloc(new_size);
                bytes_allocated += new_size;
                int num_bytes = upvalue_count * sizeof(struct UpvalueObj);
                memcpy(new_upvalues,closure->as.closure->upvalues,num_bytes);
                free(closure->as.closure->upvalues);
                closure->as.closure->upvalues = new_upvalues;
        }
        closure->as.closure->upvalues[upvalue_count].offset = offset;
        closure->as.closure->upvalues[upvalue_count].value = value;
        closure->as.closure->upvalues[upvalue_count].nesting_count = nesting_count;
        closure->as.closure->num_upvalues++;
        return closure;
}

//add upvalue from self_closure's upvalues into target closure
Value *add_upvalue_nonlocal(
Value *target_closure, Value *self_closure,int offset, int nesting_count)
{
        long upvalue = get_upvalue_ptr(self_closure,offset,nesting_count - 1);
        return add_upvalue(target_closure,upvalue,offset,nesting_count);
}

//given an offset and nesting amount, retrieve the upvalue. If not found, throw error.
// if upvalue is int,char,bool return as a non ptr type
long get_upvalue(Value *closure, int offset,int nesting_amt)
{
        struct UpvalueObj *upvalues = closure->as.closure->upvalues;
        int upvalue_total = closure->as.closure->num_upvalues;
        bool found = false;
        long res;
        for (int i = 0; i < upvalue_total; i++) {
                if ((upvalues[i].offset == offset) && 
                (nesting_amt == upvalues[i].nesting_count)) {
                        found = true;
                        res = upvalues[i].value;
                        if (is_non_ptr_type((Value *)res)) {
                                res = ((Value *)res)->as.tagged_type;
                        }
                        break;
                }
        }
        if (!found) {
                printf(
                "Tried to find upvalue with offset %d, and nesting amount %d.\n",
                offset,nesting_amt);
                abort_message(
                "finding upvalue. Offset and nesting amount not found.\n");
        }
        return res;
}

//same as get_upvalue except it always returns the value pointer. 
//used in add_upvalue_nonlocal
long get_upvalue_ptr(Value *closure, int offset,int nesting_amt)
{
        struct UpvalueObj *upvalues = closure->as.closure->upvalues;
        int upvalue_total = closure->as.closure->num_upvalues;
        bool found = false;
        long res;
        for (int i = 0; i < upvalue_total; i++) {
                if ((upvalues[i].offset == offset) && 
                (nesting_amt == upvalues[i].nesting_count)) {
                        found = true;
                        res = upvalues[i].value;
                        break;
                }
        }
        if (!found) {
                printf(
                "Tried to find upvalue with offset %d, and nesting amount %d.\n",
                offset,nesting_amt);
                abort_message(
                "finding upvalue. Offset and nesting amount not found.\n");
        }
        return res;
}

// set! but definition being set is an upvalue. upvalue is set 
void setexclam_upvalue(Value *closure,long new_val,int offset,int nesting_amt)
{
        struct UpvalueObj *upvalues = closure->as.closure->upvalues;
        int upvalue_total = closure->as.closure->num_upvalues;
        for (int i = 0; i < upvalue_total; i++) {
                if ((upvalues[i].offset == offset) && 
                (nesting_amt == upvalues[i].nesting_count)) {
                        if (!is_ptr(new_val)) {
                                turn_to_val_type(new_val,(Value *)upvalues[i].value);
                        } else {
                                Value *cur_upvalue = (Value *)upvalues[i].value;
                                value_deep_copy(cur_upvalue,((Value *)new_val));
                        }

                        return;
                }
        }
        abort_message("in set!. Offset and nesting amount not found.\n");
}

//modifies local/gloabl definition if its a ptr, otherwise returns newval
long setexclam(long definition,long new_val)
{
        if (!is_ptr(definition)) {
                return new_val;
        }
        Value *definition_obj = (Value *)definition;
        if (!is_ptr(new_val)) {
                if (is_int(new_val)) {
                        definition_obj->type = VAL_INT;
                } else if (is_bool(new_val)){
                        definition_obj->type = VAL_BOOLEAN;
                } else {
                        definition_obj->type = VAL_CHAR;
                }
                definition_obj->as.tagged_type = new_val;

        } else {
                Value *new_val_obj = (Value *)new_val;
                value_deep_copy(definition_obj,new_val_obj);
        }
        return definition;
}

Value *mark_value(Value *val)
{
        if (!val->is_marked) {
                val->is_marked = true;
                push_graystack(val);
        } else {
                #ifdef DEBUG_SYMBOLS_GC
                        printf("VALUE OF TYPE %d WAS ALREADY MARKED!\n",val->type);
                #endif
        }
        return val;
}

Value *check_type_and_mark_value(Value *val)
{
        if (!is_ptr((long)val)) {
                return NULL;
        }
        return mark_value(val);
}


void add_object(Value *val_type)
{
        Object *new_object = (Object *)malloc(sizeof(Object));
        validate_ptr(new_object);
        new_object->value = val_type;
        new_object->next = NULL;
        //no objects on the heap, initializing the list so it has one object
        if (head == NULL) {
                head = new_object;
                tail = head;
                return;
        }
        tail->next = new_object;
        tail = new_object;
}

void mark_globals(Value **global_start,int global_count)
{
        if (global_start == NULL) {
                #ifdef DEBUG_SYMBOLS_GC
                        printf("first global def hasn't been set yet.\n");
                #endif
                return;
        }
        #ifdef DEBUG_SYMBOLS_GC
                printf("in mark_globals, about to iterate all globals:\n");
        #endif
        for (int i = 0; i < global_count; i++) {
                Value *current_global = global_start[i];
                if (current_global == NULL) {
                        /*
                        a global definition is null when its spot in the bss section
                        hasnt been written to yet. this happens when the definition
                        is in the process of being made
                        */
                       #ifdef DEBUG_SYMBOLS_GC
                                printf("definition %d is null.\n",i);
                       #endif
                        
                }
                else if (!is_ptr((long)current_global)) {
                        #ifdef DEBUG_SYMBOLS_GC
                                printf("definition %d is not a pointer.\n",i);
                        #endif
                } else {
                        #ifdef DEBUG_SYMBOLS_GC
                                printf("definition %d's TYPE IS: %d\n",i,((Value *)current_global)->type);
                        #endif
                        mark_value(current_global);
                }
        }
}

void mark_locals(Value *self_closure)
{
        for (int i = 0; i < live_locals_top; i++) {
                if (is_ptr((long)live_locals[i])) {
                        mark_value(live_locals[i]);
                }

        }
        #ifdef DEBUG_SYMBOLS_GC
                printf("now marking upvalues:\n");
        #endif
        
        if (self_closure == NULL) {
                #ifdef DEBUG_SYMBOLS_GC
                        printf("in global scope, so no upvalues.\n");
                #endif
                return;
        }
        struct UpvalueObj *upvalues = self_closure->as.closure->upvalues;
        int upval_count = self_closure->as.closure->num_upvalues;
        for (int i = 0; i < upval_count; i++) {
                #ifdef DEBUG_SYMBOLS_GC
                        printf("upvalue %d of type %d being marked.\n",i,((Value*)upvalues[i].value)->type);
                #endif
                mark_value((Value*)upvalues[i].value);
        }
        #ifdef DEBUG_SYMBOLS_GC
                printf("done marking upvalues:\n");
        #endif
        
}

void collect_garbage(Value **global_start, long global_count, Value *self_closure)
{
        if (bytes_allocated < 0) {
                abort_message("There's a problem with how im deducting bytes_allocated.\n");

        }
        if (bytes_allocated <= next_gc) {
                return;
        }
        #ifdef DEBUG_SYMBOLS_GC
                printf("--gc begin\n");
                printf("BYTES ALLOCATED IS: %d\n",bytes_allocated);
                int prev_bytes_allocated = bytes_allocated;
                printf("global count is %ld\n",global_count);
                printf("collect_garbage being called :D\n");
                printf("Walking through global definitions:\n");
        #endif
        mark_globals(global_start,global_count);
        #ifdef DEBUG_SYMBOLS_GC
                printf("now walking through local definitions:\n");
        #endif
        mark_locals(self_closure);
        #ifdef DEBUG_SYMBOLS_GC
                printf("number of values in graystack is: %d\n",gray_count);
                for (int i = 0 ; i < gray_count; i++) {
                        printf("graystack item %d's type is: %d\n",i, gray_stack[i]->type);
                }
                printf("now getting indirect references:\n");
        #endif
        trace_references();
        #ifdef DEBUG_SYMBOLS_GC
                printf("NOW SWEEPING:\n");
        #endif
        sweep();
        reset_graystack();
        next_gc = bytes_allocated * GC_HEAP_GROW_FACTOR;
        #ifdef DEBUG_SYMBOLS_GC
                printf(
                "After gc finished running, bytes_allocated is now %d, so %d bytes were freed\n"
                ,bytes_allocated,prev_bytes_allocated - bytes_allocated);
                printf("--gc end\n\n");
        #endif
}

void push_graystack(Value *gray_value)
{
        if (gray_capacity == gray_count) {
                grow_capacity();
        }
        gray_stack[gray_count] = gray_value;
        gray_count++;
        #ifdef DEBUG_SYMBOLS_GC
                printf("added object to gray stack\n");
        #endif
        
}
//to grow gray_stack
void grow_capacity()
{
       //initialization
        if (gray_stack == NULL) {
                gray_stack = calloc(1,sizeof(Value*));
                validate_ptr(gray_stack);
                gray_capacity = 1;
                return;
        }
        gray_capacity *= 2;
        gray_stack = realloc(gray_stack,gray_capacity * sizeof(Value*));
        validate_ptr(gray_stack);
}
void reset_graystack()
{
       gray_count = 0;
       gray_capacity = 0;
       free(gray_stack);
       gray_stack = NULL; 
}
void trace_references()
{
        while (gray_count > 0) {
                Value *cur_val = gray_stack[--gray_count];
                blacken_value(cur_val);
        }
}

//depending on val's type, set the is_mark flag of any Value struct reference val has.
//Only pair,vector and closure have indirect references of Value structs
void blacken_value(Value *val)
{
        switch (val->type) {
        case VAL_PAIR:
                mark_value(&(val->as.pair->car));
                mark_value(&(val->as.pair->cdr));
                break;
        case VAL_CLOSURE:
                int upval_count = val->as.closure->num_upvalues;
                struct UpvalueObj *upvalues = val->as.closure->upvalues;
                mark_value(val->as.closure->function);
                //now add all upvalues to graystack
                for (int i = 0; i < upval_count; i++) {
                        mark_value((Value*)upvalues[i].value);
                }
                break;
        case VAL_VECTOR:
                int vec_size = val->as.vector->size;
                Value *vec_items = val->as.vector->items;
                for (int i = 0; i < vec_size; i++) {
                        mark_value(&vec_items[i]);
                }
                break;
        default:
                #ifdef DEBUG_SYMBOLS_GC
                        printf("value being blackened has no indirect references.\n");
                #endif
                break;
        }
}

//frees value type. is_ptr_freeable is to indicate whether val should be freed,
//i.e. the ptr in val was obtained from malloc,calloc,realloc.
void free_value(Value *val,bool is_ptr_freeable)
{
        if (val == NULL) {
                #ifdef DEBUG_SYMBOLS_GC
                        printf("value was already freed!\n");
                #endif
                return;
        }
        #ifdef DEBUG_SYMBOLS_GC
                printf("freeing val of type %d\n",val->type);
        #endif 
        //free the fields of val
        switch(val->type) {
        case VAL_STR:
                free(val->as.str);
                bytes_allocated -= sizeof(struct Str);
                val->as.str = NULL;
                break;
        case VAL_PAIR:
                free_value(&(val->as.pair->car),true);
                free_value(&(val->as.pair->cdr),false);
                break;
        case VAL_FUNCTION:
                free(val->as.function);
                bytes_allocated -= sizeof(struct FuncObj);
                val->as.function = NULL;
                break;
        case VAL_CLOSURE:
                free(val->as.closure->upvalues);
                bytes_allocated -= (sizeof(struct UpvalueObj) * val->as.closure->num_upvalues);
                free(val->as.closure);
                bytes_allocated -= sizeof(struct ClosureObj);
                val->as.closure->upvalues = NULL;
                val->as.closure = NULL;
                break;
        case VAL_VECTOR:
                int size = val->as.vector->size;
                Value *vec_items = val->as.vector->items;
                //starts at i = 1 because vec_items[0] is already in the linked list,
                // so will get picked up
                for (int i = 1; i < size; i++) {
                        free_value(&vec_items[i],false);
                }
                free(val->as.vector);
                bytes_allocated -= sizeof(struct Vector);
                val->as.vector = NULL;
                break;
        case VAL_SYMBOL:
                free(val->as.str);
                bytes_allocated -= sizeof(struct Str);
                val->as.str = NULL;
                break;
        default:
                //type didnt require special handling
                break;
        }
        if (is_ptr_freeable) {
                //free the actual value type
                free(val);
        }
        bytes_allocated -= sizeof(Value);
        val = NULL;
}

/*
once all reachable value types are marked, this frees all value types whose 
is_marked bit is set to false
*/
void sweep()
{
        Object *cur_obj = head;
        Object *prev_obj = NULL;
        while (cur_obj != NULL) {
                #ifdef DEBUG_SYMBOLS_GC
                        printf(
                        "IN SWEEP. TYPE IS: %d. is_marked is: %d\n",
                        cur_obj->value->type,cur_obj->value->is_marked);
                #endif
                
                if (cur_obj->value->is_marked) {
                        //set it back to false for next time gc is called
                        cur_obj->value->is_marked = false;
                        prev_obj = cur_obj;
                        cur_obj = cur_obj->next;
                } else {
                        //free current value, fix the next ptrs of the linked list.
                        //and free the current object type
                        free_value(cur_obj->value,true);
                        cur_obj->value = NULL;
                        //fix pointers of linked list
                        
                        if (prev_obj == NULL) {
                                //object being freed is the head
                                head = cur_obj->next;
                                free(cur_obj);
                                cur_obj = head;
                        } else {
                                prev_obj->next = cur_obj->next;
                                free(cur_obj);
                                cur_obj = prev_obj->next;
                        }
                } 
        }
}


void push_to_live_local(Value *val)
{
        if (live_locals_top >= LIVE_LOCAL_MAX) {
                abort_message("ran out of space on live_locals.\n");
        }
        live_locals[live_locals_top] = val;
        live_locals_top++;
}

Value* pop_live_local()
{
        if (live_locals_top == 0) {
                abort_message("live_locals is already empty.\n");
        }
        live_locals_top--;
        return live_locals[live_locals_top];
}

void pop_n_locals(int amount_to_pop) 
{
        int new_top = live_locals_top - amount_to_pop;
        if (new_top < 0) {
                printf("live_locals_top is: %d, amount_to_pop is: %d\n",live_locals_top,amount_to_pop);
                abort_message("live_locals does not have n objects to pop\n");
        }
        live_locals_top = new_top;
}