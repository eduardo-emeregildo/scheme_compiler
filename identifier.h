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
        VAL_SYMBOL,
        VAL_EMPTY_LIST

} ValueType;

// this is for boxed types on the heap
typedef struct {
        ValueType type;
        union{
                struct Str *str;
                double _double;
                struct Pair *pair;
                struct Vector *vector;
                //void *function;
                struct FuncObj *function;
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
struct Str *allocate_str(char *str);
struct Pair *allocate_pair();
struct Vector *allocate_vector(Value *vec_elts,size_t size);
struct FuncObj *allocate_function(void *function_addr,bool variadic,int arity);
void set_ith_value_int(Value *val_ptr,long integer,size_t index);
void set_ith_value_char(Value *val_ptr,char character,size_t index);
void set_ith_value_bool(Value *val_ptr,bool boolean,size_t index);
void set_ith_value_dbl(Value *val_ptr,double num,size_t index);
void set_ith_value_str(Value *val_ptr,char *str,size_t index);
void set_ith_value_symbol(Value *val_ptr,char *str,size_t index);
void set_ith_value_pair(Value *val_ptr,struct Pair *pair_obj,size_t index);
void set_ith_value_vector(Value *val_ptr,struct Vector *vec,size_t index);
void set_ith_value_function(Value *val_ptr,struct FuncObj *func_obj,size_t index);
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
#endif