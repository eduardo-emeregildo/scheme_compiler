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
long _mul(Value *param_list);
long _div(long dividend, Value* varargs);
double *check_and_extract_numbers(
long value1, long value2, char *builtin_name, double untagged_values[2]);
long _equal_sign(long value1,long value2);
long _greater(long value1,long value2);
long _greater_equal(long value1,long value2);
long _less(long value1,long value2);
long _less_equal(long value1,long value2);
long _car(long value);
long _cdr(long type);
long _null(long type);
long _eq(long value1,long value2);
Value DISPLAY = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_display,false,1}}};
Value ADDITION = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_add,true,1}}};
Value SUBTRACTION = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_sub,true,2}}};
Value MULT = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_mul,true,1}}};
Value DIVISION = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_div,true,2}}};
Value EQUAL_SIGN = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_equal_sign,false,2}}};
Value GREATER = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_greater,false,2}}};
Value GREATER_EQUAL = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_greater_equal,false,2}}};
Value LESS = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_less,false,2}}};
Value LESS_EQUAL = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_less_equal,false,2}}};
Value CAR = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_car,false,1}}};
Value CDR = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_cdr,false,1}}};
Value NULLQ = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_null,false,1}}};
Value EQ = {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&_eq,false,2}}};
#endif