//lib.c will have the imlementations of builtin function function bodies.
// the value objs in this header are the value objects for each builtin.
// This is so that builtin functions can be first class as well as user defined
// functions
#ifndef lib
#define lib
#include "identifier.h"
#include <stdarg.h>
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
long new_add(long type,...); 
Value display = {VAL_FUNCTION,.as = {.function = &_display}};
Value addition = {VAL_FUNCTION,.as = {.function = &_add}};
#endif