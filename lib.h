//lib.c will have the imlementations of builtin function function bodies.
// the value objs in this header are the value objects for each builtin.
// This is so that builtin functions can be first class as well as user defined
// functions
#ifndef lib
#define lib
#include "identifier.h"
#define FUNCTION_OBJ(name_function,is_variadic,arity) {VAL_FUNCTION,.as = {.function = &(struct FuncObj){&name_function,is_variadic,arity}}}
#define CLOSURE_OBJ(function_ptr) {VAL_CLOSURE,.as = {.closure = &(struct ClosureObj){&function_ptr,NULL,0}}}
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
void _display(long self, void *type);
long _add(long self,Value *param_list);
long _sub(long self,long minuend,Value *varargs);
long _mul(long self,Value *param_list);
long _div(long self,long dividend, Value* varargs);
double *check_and_extract_numbers(
long value1, long value2, char *builtin_name, double untagged_values[2]);
long _equal_sign(long self,long value1,long value2);
long _greater(long self,long value1,long value2);
long _greater_equal(long self,long value1,long value2);
long _less(long self,long value1,long value2);
long _less_equal(long self,long value1,long value2);
long _car(long self,long type);
long _cdr(long self,long type);
long _null(long self,long type);
long _eq(long self,long value1,long value2);
long _equal(long self,long value1,long value2);
long are_str_types_equal(Value *value1, Value *value2);
long are_pairs_equal(Value *value1, Value *value2);
long are_vectors_equal(Value *value1, Value *value2);
long _append(long self,Value *varargs);
long _vector_ref(long self,long vector, long position);
Value *_make_vector(long self,long size, long init_value);
long _vector_length(long self,long vector);
void _vector_set(long self, long vector,long position, long new_val);
long _pairq(long self, long val);
long _listq(long self,long val);
long _vectorq(long self, long val);
Value *_cons(long self, long car_val, long cdr_val);
bool is_list_improper(struct Pair *list);
struct Pair *advance_lst_to_end(struct Pair *list);
void append_to_list(struct Pair *list,struct Pair *varargs);

Value DISPLAY_FUNCTION = FUNCTION_OBJ(_display,false,2);
Value ADDITION_FUNCTION = FUNCTION_OBJ(_add,true,2);
Value MULT_FUNCTION = FUNCTION_OBJ(_mul,true,2);
Value SUBTRACTION_FUNCTION = FUNCTION_OBJ(_sub,true,3);
Value DIVISION_FUNCTION = FUNCTION_OBJ(_div,true,3);
Value EQUAL_SIGN_FUNCTION = FUNCTION_OBJ(_equal_sign,false,3);
Value GREATER_FUNCTION = FUNCTION_OBJ(_greater,false,3);
Value GREATER_EQUAL_FUNCTION = FUNCTION_OBJ(_greater_equal,false,3);
Value LESS_FUNCTION = FUNCTION_OBJ(_less,false,3);
Value LESS_EQUAL_FUNCTION = FUNCTION_OBJ(_less_equal,false,3);
Value CAR_FUNCTION = FUNCTION_OBJ(_car,false,2); 
Value CDR_FUNCTION = FUNCTION_OBJ(_cdr,false,2);
Value NULLQ_FUNCTION = FUNCTION_OBJ(_null,false,2);
Value EQ_FUNCTION = FUNCTION_OBJ(_eq,false,3); 
Value EQV_FUNCTION = FUNCTION_OBJ(_eq,false,3);
Value EQUAL_FUNCTION = FUNCTION_OBJ(_equal,false,3);
Value APPEND_FUNCTION = FUNCTION_OBJ(_append,true,2);
Value MAKE_VECTOR_FUNCTION = FUNCTION_OBJ(_make_vector,false,3);
Value VECTOR_REF_FUNCTION = FUNCTION_OBJ(_vector_ref,false,3);
Value VECTOR_LENGTH_FUNCTION = FUNCTION_OBJ(_vector_length,false,2);
Value VECTOR_SET_FUNCTION = FUNCTION_OBJ(_vector_set,false,4);
Value PAIRQ_FUNCTION = FUNCTION_OBJ(_pairq,false,2);
Value LISTQ_FUNCTION = FUNCTION_OBJ(_listq,false,2);
Value VECTORQ_FUNCTION = FUNCTION_OBJ(_vectorq,false,2);
Value CONS_FUNCTION = FUNCTION_OBJ(_cons,false,3);

Value DISPLAY = CLOSURE_OBJ(DISPLAY_FUNCTION);
Value ADDITION = CLOSURE_OBJ(ADDITION_FUNCTION);
Value MULT = CLOSURE_OBJ(MULT_FUNCTION);
Value SUBTRACTION = CLOSURE_OBJ(SUBTRACTION_FUNCTION);
Value DIVISION = CLOSURE_OBJ(DIVISION_FUNCTION);
Value EQUAL_SIGN = CLOSURE_OBJ(EQUAL_SIGN_FUNCTION);
Value GREATER = CLOSURE_OBJ(GREATER_FUNCTION);
Value GREATER_EQUAL = CLOSURE_OBJ(GREATER_EQUAL_FUNCTION);
Value LESS = CLOSURE_OBJ(LESS_FUNCTION);
Value LESS_EQUAL = CLOSURE_OBJ(LESS_EQUAL_FUNCTION);
Value CAR = CLOSURE_OBJ(CAR_FUNCTION); 
Value CDR = CLOSURE_OBJ(CDR_FUNCTION);
Value NULLQ = CLOSURE_OBJ(NULLQ_FUNCTION);
Value EQ = CLOSURE_OBJ(EQ_FUNCTION); 
Value EQV = CLOSURE_OBJ(EQV_FUNCTION);
Value EQUAL = CLOSURE_OBJ(EQUAL_FUNCTION);
Value APPEND = CLOSURE_OBJ(APPEND_FUNCTION);
Value MAKE_VECTOR = CLOSURE_OBJ(MAKE_VECTOR_FUNCTION);
Value VECTOR_REF = CLOSURE_OBJ(VECTOR_REF_FUNCTION);
Value VECTOR_LENGTH = CLOSURE_OBJ(VECTOR_LENGTH_FUNCTION);
Value VECTOR_SET = CLOSURE_OBJ(VECTOR_SET_FUNCTION);
Value PAIRQ = CLOSURE_OBJ(PAIRQ_FUNCTION);
Value LISTQ = CLOSURE_OBJ(LISTQ_FUNCTION);
Value VECTORQ = CLOSURE_OBJ(VECTORQ_FUNCTION);
Value CONS = CLOSURE_OBJ(CONS_FUNCTION);
#endif