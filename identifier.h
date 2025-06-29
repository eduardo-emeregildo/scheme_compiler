#ifndef identifier
#define identifier
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>
typedef enum {
        VAL_CHAR,
        VAL_STR,
        VAL_INT,
        VAL_DOUBLE,
        VAL_BOOLEAN,
        VAL_PAIR,
        VAL_VECTOR,
        VAL_FUNCTION,
        VAL_CLOSURE,
        VAL_SYMBOL,
        VAL_EMPTY_LIST

} ValueType;

// this is for boxed types on the heap
typedef struct {
        ValueType type;
        bool is_marked;
        union{
                struct Str *str;
                double _double;
                struct Pair *pair;
                struct Vector *vector;
                struct FuncObj *function;
                struct ClosureObj *closure;
                void *empty_list; // will point to NULL
                long tagged_type; //only exists if a elt in lst is int,char,bool
        } as;
} Value;

// car.type = VAL_EMPTY_LIST denotes the empty list
// cdr.type = VAL_EMPTY_LIST indicates the end of a list
// empty list would only be used if one of the list elements is an empty list
//i.e. '(1 2 () 3)
struct Pair {
        Value car;
        Value cdr;
};

struct Str {
        int length;
        char* chars; 
};

// if size is 0, items will point to NULL
struct Vector {
        int size;
        Value *items;
};

struct FuncObj {
        void *function_ptr;
        bool is_variadic;
        int arity;
};

struct ClosureObj {
        Value *function;
        struct UpvalueObj* upvalues;
        int num_upvalues;
};

struct UpvalueObj {
        int offset;
        int nesting_count; //this combined with offset used for searching
        long value;
};

//linked list to track all objects that are in the heap. in identifier.h, will create
// a pointer an Object pointer thats called head and Object pointer thats called
// tail, since these are the two that I will be using. 
//they will both be initialized to Null

// head will of course hold a ptr to the first object and tail will hold a pointer
//to the last obj.the last object's next field will be Null to denote end of list
struct Object{
        Value *value;
        struct Object *next;
};
typedef struct Object Object;

bool is_int(long item);
bool is_ptr(long item);
bool is_bool(long item);
bool is_char(long item);
void abort_message(char *error_message);
void check_int_range(long num);
long make_tagged_int(long num);
long untag_int(long num);
Value *make_tagged_ptr(size_t num_value_objects);
long make_tagged_bool(bool boolean);
long make_tagged_char(char character);
long remove_tag(long tagged_item);
void validate_ptr(void *ptr);
Value *make_value_int(long integer);
Value *make_value_char(char character);
Value *make_value_bool(bool boolean);
Value *make_empty_list();
struct Str *allocate_str(char *str);
struct Pair *allocate_pair();
struct Vector *allocate_vector(Value *vec_elts,size_t size);
struct FuncObj *allocate_function(void *function_addr,bool variadic,int arity);
struct ClosureObj *allocate_closure(Value *function);
void set_ith_value_int(Value *val_ptr,long integer,size_t index);
void set_ith_value_char(Value *val_ptr,char character,size_t index);
void set_ith_value_bool(Value *val_ptr,bool boolean,size_t index);
void set_ith_value_dbl(Value *val_ptr,double num,size_t index);
void set_ith_value_str(Value *val_ptr,char *str,size_t index);
void set_ith_value_symbol(Value *val_ptr,char *str,size_t index);
void set_ith_value_pair(Value *val_ptr,struct Pair *pair_obj,size_t index);
void set_ith_value_vector(Value *val_ptr,struct Vector *vec,size_t index);
void set_ith_value_function(Value *val_ptr,struct FuncObj *func_obj,size_t index);
void set_ith_value_empty_list(Value *val_ptr, size_t index);
void set_ith_value_closure(Value *val_ptr,struct ClosureObj *closure,size_t index);
void set_ith_value_unknown(Value *val_ptr, long type,size_t index);
Value *get_car_ptr(struct Pair *pair_obj);
Value *get_cdr_ptr(struct Pair *pair_obj);
Value *make_value_double(double num);
Value *make_value_string(struct Str *str_obj);
Value *make_value_symbol(struct Str *str_obj);
Value *make_value_pair(struct Pair *pair_obj);
Value *make_value_list(Value *value_obj_array, size_t len);
Value *make_value_vector(Value *value_obj_array, size_t len);
Value *make_value_function(struct FuncObj *func_obj);
Value *make_value_closure(struct ClosureObj *closure);
Value *check_param_function_call(Value *func_obj,long *args,int arg_amount);
Value *check_if_callable(long type);
Value *make_arg_list(Value *func_obj,long *args,int arg_amount);
Value *make_arg_list_min_args(int min_args,long *args,int arg_amount);
long pass_by_value(long arg);
void value_deep_copy(Value *copy,Value* val_obj);
void turn_to_val_type(long non_ptr_type,Value *val_obj);
long move_local_to_heap(long local);
long turn_to_non_ptr_type(Value *ptr_type);
bool is_non_ptr_type(Value *val_type);
bool is_closure(long type);
Value *add_upvalue(Value *closure,long value, int offset, int nesting_count);
Value *add_upvalue_nonlocal(
Value *target_closure, Value *self_closure,int offset, int nesting_count);
long get_upvalue(Value *closure, int offset,int nesting_amt);
long get_upvalue_ptr(Value *closure, int offset,int nesting_amt);
void setexclam_upvalue(Value *closure,long new_val,int offset,int nesting_amt);
long setexclam(long definition,long new_val);
Value *mark_value(Value *val);
Value *check_type_and_mark_value(Value *val);
void add_object(Value *val_type);
void collect_garbage(Value **global_start, long global_count, Value *self_closure);
void mark_globals(Value **global_start,int global_count);
void mark_locals(Value * self_closure);
void push_graystack(Value *gray_value);
void grow_capacity();
void reset_graystack();
void trace_references();
void blacken_value(Value *val);
void free_value(Value *val,bool is_ptr_freeable);
void sweep();
void push_to_live_local(Value *val);
Value* pop_live_local();
void pop_n_locals(int amount_to_pop);
#endif