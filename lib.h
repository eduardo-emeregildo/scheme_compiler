//lib.c will have the imlementations of builtin function function bodies.
// the value objs in this header are the value objects for each builtin.
// This is so that builtin functions can be first class as well as user defined
// functions
#ifndef lib
#define lib
#include "identifier.h"
//constants
const long SCHEME_FALSE = 2;
const long SCHEME_TRUE = 10;
void print_value_type(Value *value_obj);
void print_list(Value *value_obj);
void print_vector(Value *value_obj);
void is_function(long type);

/*
the ptrs to the functions below will be used when making value objs of type
function
*/
void _display(void *value_ptr);
long _add(Value *param_list);
long _sub(long minuend,Value *varargs);
double *check_and_extract_numbers(
long value1, long value2, char *builtin_name, double untagged_values[2]);
long _equal_sign(long value1,long value2);
Value display = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_display,false,1}}};
Value addition = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_add,true,1}}};
Value subtraction = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_sub,true,2}}};
Value equal_sign = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_equal_sign,false,2}}};
#endif