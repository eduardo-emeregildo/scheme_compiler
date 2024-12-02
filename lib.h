//lib.c will have the imlementations of builtin function function bodies.
// the value objs in this header are the value objects for each builtin.
// This is so that builtin functions can be first class as well as user defined
// functions
#ifndef lib
#define lib
#include "identifier.h"
void print_value_type(Value *value_obj);
void print_list(Value *value_obj);
void print_vector(Value *value_obj);
void _DISPLAY(void *value_ptr);
Value DISPLAY = {VAL_FUNCTION,.as = {.function = &_DISPLAY}};
#endif