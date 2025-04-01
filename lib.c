#include "lib.h"
//prints a value type
void print_value_type(Value *value_obj) 
{
        printf("value location: %p",value_obj);
        switch(value_obj->type) {
        case VAL_CHAR:
                printf("%c",(int)remove_tag(value_obj->as.tagged_type));
                break;
        case VAL_STR:
                printf("%s",value_obj->as.str->chars);
                break;
        case VAL_INT:
                printf("%ld",untag_int(value_obj->as.tagged_type));
                break;
        case VAL_DOUBLE:
                printf("%lf",value_obj->as._double);
                break;
        case VAL_BOOLEAN:
                printf("0x%ld",remove_tag(value_obj->as.tagged_type));
                break;
        case VAL_PAIR:
                print_list(value_obj);
                break;
        case VAL_VECTOR:
                print_vector(value_obj);
                break;
        case VAL_FUNCTION:
                printf("function at: %p",value_obj->as.function->function_ptr);
                break;
        case VAL_SYMBOL:
                printf("'%s",value_obj->as.str->chars);
                break;
        case VAL_EMPTY_LIST:
                printf("()");
                break;
        case VAL_CLOSURE:
                printf("(closure at %p). function at: %p",
                value_obj->as.closure,
                value_obj->as.closure->function->as.function->function_ptr);
                break;
        default:
                break;
        }
}

void print_list(Value *value_obj)
{
        struct Pair *lst_cur_pair = value_obj->as.pair;
        printf("(");
        if (lst_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                print_value_type(get_car_ptr(lst_cur_pair));
                printf(")");
                return;
        }
        while(lst_cur_pair->cdr.type != VAL_EMPTY_LIST) { 
                print_value_type(get_car_ptr(lst_cur_pair));
                if(lst_cur_pair->cdr.type != VAL_PAIR) {
                        //dot notation case
                        if(lst_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                                break;
                        }
                        printf(" . ");
                        print_value_type(get_cdr_ptr(lst_cur_pair));
                        break;
                }
                lst_cur_pair = lst_cur_pair->cdr.as.pair;
                if(lst_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                        printf(" ");
                        print_value_type(get_car_ptr(lst_cur_pair));
                        break;
                }
                printf(" ");
        }
        printf(")");

}

void print_vector(Value *value_obj)
{
        printf("#(");
        Value *vec = value_obj->as.vector->items;
        int vec_len = value_obj->as.vector->size;
        for(size_t i = 0; i < vec_len ; i++) {
                print_value_type(&vec[i]);
                if(i < (vec_len - 1)) {
                        printf(" ");
                }
        }
        printf(")");
}
void _display(long self,void *type)
{
        long long_type = (long)type;
        if (is_ptr(long_type)) {
                print_value_type((Value *)type);
        } else if (is_int(long_type)) {
                printf("%ld", untag_int(long_type));
        } else if (is_bool(long_type)) {
                printf("0x%ld",remove_tag(long_type));
        } else if (is_char(long_type)) {
                printf("%c",(int)remove_tag(long_type));
        }
        else {
                abort_message("in display function, not a valid type.\n");
        }
        printf("\n");
}

long _add(long self,Value *param_list)
{
        if (param_list->type == VAL_EMPTY_LIST) {
                return make_tagged_int(0);
        }
        long num_sum = 0;
        double double_sum = 0.0;
        struct Pair *cur_param = param_list->as.pair;
        while (cur_param->car.type != VAL_EMPTY_LIST) {
                if (cur_param->car.type == VAL_INT) {
                        num_sum += untag_int(cur_param->car.as.tagged_type);
                } else if (cur_param->car.type == VAL_DOUBLE) {
                        double_sum += cur_param->car.as._double;
                } else {
                        abort_message("In +. Expected a number.\n");
                }
                if (cur_param->cdr.type == VAL_EMPTY_LIST) {
                        break;
                }
                cur_param = cur_param->cdr.as.pair;
        }
        if (double_sum == 0) {
                return make_tagged_int(num_sum);
        }
        return (long)make_value_double((double)num_sum + double_sum);

}

long _sub(long self,long minuend,Value *varargs)
{       
        bool is_res_double = false;
        double minuend_value;
        double substrahend_value;
        if (is_int(minuend)) {
                minuend_value = untag_int(minuend);
        } else if (is_ptr(minuend) &&  ((Value *)minuend)->type == VAL_DOUBLE) {
                is_res_double = true;
                minuend_value = ((Value *)minuend)->as._double;
        } else {
                abort_message("in -. Expected a number.\n");
        }

        long substrahend = _add(self,varargs);
        if (is_int(substrahend)) {
                substrahend_value = untag_int(substrahend);
        } else {
                is_res_double = true;
                substrahend_value = ((Value *)substrahend)->as._double;
        }

        // in case varargs is empty, scheme does 0 - minuend, so swap values
        if (varargs->type == VAL_EMPTY_LIST) {
                double temp = minuend_value;
                minuend_value = substrahend_value;
                substrahend_value = temp;
        }
        if (is_res_double) {
                return (long)make_value_double(minuend_value - substrahend_value);
        }
        return make_tagged_int(minuend_value - substrahend_value);
}

long _mul(long self,Value *param_list)
{
        if (param_list->type == VAL_EMPTY_LIST) {
                return make_tagged_int(1);
        }
        bool is_res_double = false;
        double product = 1;
        struct Pair *cur_param = param_list->as.pair;
        while (cur_param->car.type != VAL_EMPTY_LIST) {
                int cur_param_type = cur_param->car.type;
                if (cur_param_type == VAL_INT) {
                        product *= untag_int(cur_param->car.as.tagged_type);
                } else if (cur_param_type == VAL_DOUBLE) {
                        is_res_double = true;
                        product *= cur_param->car.as._double;
                } else {
                        abort_message("in *. Expected a number.\n");
                }
                if (cur_param->cdr.type == VAL_EMPTY_LIST) {
                        break;
                }
                cur_param = cur_param->cdr.as.pair;
        }

        if (is_res_double) {
                return (long)make_value_double(product);
        }
        return make_tagged_int(product);
}

long _div(long self,long dividend, Value* varargs)
{
        bool is_res_double = false;
        double dividend_value;
        double divisor_value;
        if (is_int(dividend)) {
                dividend_value = untag_int(dividend);
        } else if (is_ptr(dividend) &&  ((Value *)dividend)->type == VAL_DOUBLE) {
                is_res_double = true;
                dividend_value = ((Value *)dividend)->as._double;
        } else {
                abort_message("in /. Expected a number.\n");
        }

        long divisor = _mul(self,varargs);
        if (is_int(divisor)) {
                divisor_value = untag_int(divisor);
        } else {
                is_res_double = true;
                divisor_value = ((Value *)divisor)->as._double;
        }

        // in case varargs is empty, scheme does 1 / dividend, so swap values
        if (varargs->type == VAL_EMPTY_LIST) {
                double temp = dividend_value;
                dividend_value = divisor_value;
                divisor_value = temp;
        }
        if (divisor_value == 0.0) {
                abort_message("In /. Division by 0.\n");
        }
        double res = dividend_value / divisor_value;
        if (floor(res) != res || is_res_double) {
                return (long)make_value_double(res);
        }
        return make_tagged_int(res);
}

// checks if value1 and value2 are numbers and returns their untagged values
double *check_and_extract_numbers(
long value1, long value2,char *builtin_name, double untagged_values[2])
{
        if (is_int(value1)) {
                untagged_values[0] = untag_int(value1);
        } else if (is_ptr(value1) && ((Value *)value1)->type == VAL_DOUBLE) {
                untagged_values[0] = ((Value *)value1)->as._double;
        } else {
                printf("Error in %s. Expected a number\n",builtin_name);
                exit(EXIT_FAILURE);
        }

        if (is_int(value2)) {
                untagged_values[1] = untag_int(value2);
        } else if (is_ptr(value2) && ((Value *)value2)->type == VAL_DOUBLE) {
                untagged_values[1] = ((Value *)value2)->as._double;
        } else {
                printf("Error in %s. Expected a number\n",builtin_name);
                exit(EXIT_FAILURE);
        }
        return untagged_values;
}

long _equal_sign(long self,long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,"=",untagged_values);
        if (untagged_values[0] == untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _greater(long self,long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,">",untagged_values);
        if (untagged_values[0] > untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _greater_equal(long self,long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,">=",untagged_values);
        if (untagged_values[0] >= untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _less(long self,long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,"<",untagged_values);
        if (untagged_values[0] < untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _less_equal(long self,long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,"<=",untagged_values);
        if (untagged_values[0] <= untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _car(long self,long type)
{
        if (!is_ptr(type)) {
                abort_message("in car. Expected a pair.\n");
        } else if (((Value *)type)->type == VAL_EMPTY_LIST) {
                abort_message("in car. Cannot get car of empty list.\n");
        } else if ( ((Value *)type)->type != VAL_PAIR) {
                abort_message("in car. Expected a pair.\n");
        }
        Value *type_car = &((Value *)type)->as.pair->car;
        if (is_ptr(type_car->as.tagged_type)) {
                return (long)type_car;
        }
        return type_car->as.tagged_type;
}

long _cdr(long self,long type)
{
        if (!is_ptr(type)) {
                abort_message("in cdr. Expected a pair.\n");
        } else if ( ((Value *)type)->type == VAL_EMPTY_LIST) {
                abort_message("in cdr. Cannot get cdr of empty list.\n");
        } else if( ((Value *)type)->type != VAL_PAIR) {
                abort_message("in cdr. Expected a pair.\n");
        }
        Value *type_cdr = &((Value *)type)->as.pair->cdr;
        if (is_ptr(type_cdr->as.tagged_type)) {
                return (long)type_cdr;
        }
        return type_cdr->as.tagged_type;
}

long _null(long self,long type)
{       
        if (!is_ptr(type)) {
                return SCHEME_FALSE;
        }
        else if ( ((Value *)type)->type == VAL_EMPTY_LIST) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _eq(long self,long value1,long value2)
{
        bool is_val1_ptr = is_ptr(value1);
        bool is_val2_ptr = is_ptr(value2);
        long res = SCHEME_FALSE;
        if (is_val1_ptr != is_val2_ptr) {
                return res;
        } else if (is_val1_ptr) {
                //it doesnt really matter how i cast the union
                long val1_ptr = ((Value *)value1)->as.tagged_type;
                long val2_ptr = ((Value *)value2)->as.tagged_type;
                if (val1_ptr == val2_ptr) {
                        res = SCHEME_TRUE; 
                }
        } else if(value1 == value2) {
                res = SCHEME_TRUE;
        }
        return res;
}

/*
for structural equality. when values are not string,list,vector symbol, 
does the same thing as eqv?. otherwise check elt by elt the values
*/
long _equal(long self,long value1,long value2)
{
        bool is_val1_ptr = is_ptr(value1);
        bool is_val2_ptr = is_ptr(value2);
        long res = SCHEME_FALSE;
        if (is_val1_ptr != is_val2_ptr) {
                return SCHEME_FALSE;
        } else if (!is_val1_ptr) {
                res = _eq(self,value1, value2);
        } else {
                Value *val1_ptr = ((Value *)value1);
                Value *val2_ptr = ((Value *)value2);
                if (val1_ptr->type != val2_ptr->type) {
                        return SCHEME_FALSE;
                }
                if (val1_ptr->type == VAL_EMPTY_LIST) {
                        return SCHEME_TRUE;
                }
                if (val1_ptr->type == VAL_PAIR) {
                        res = are_pairs_equal(val1_ptr,val2_ptr);
                } else if (val1_ptr->type == VAL_VECTOR) {
                        res = are_vectors_equal(val1_ptr,val2_ptr);
                } else if (val1_ptr->type == VAL_STR) {
                        res = are_str_types_equal(val1_ptr,val2_ptr);
                } else if (val1_ptr->type == VAL_SYMBOL) {
                        res = are_str_types_equal(val1_ptr,val2_ptr);
                } else {
                        res = _eq(self,value1,value2);
                }
        }
        return res;
}

/*
appends each list in varargs. returns the first list followed by elts of the other
lists. 

If there are no args (i.e. varargs is empty list), return the empty list.

If there is exactly one argument, it is returned.

Otherwise, the resulting list is always newly allocated

In the event that one of the varargs is the empty list, ignore this arg.

In the event that one of the varargs isnt a list, it MUST be the last arg.
If it isnt last, or if there is more than one vararg that isnt a list, throw error.
*/
long _append(long self,Value *varargs)
{
        if (varargs->type == VAL_EMPTY_LIST) {
                return (long)varargs;
        }
        struct Pair *vararg_cur_pair = varargs->as.pair;
        //exactly one arg
        if (vararg_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                if (is_non_ptr_type(&vararg_cur_pair->car)) {
                        return vararg_cur_pair->car.as.tagged_type;
                } else return (long)&vararg_cur_pair->car;
        }
        struct Pair *appended_list = allocate_pair();
        struct Pair *cur_list = appended_list;
        bool is_list_initialized = false;
        //find and copy first list(ignores empty lists). This will be the base 
        //list to append to
        while (!is_list_initialized) {
                if (vararg_cur_pair->car.type == VAL_PAIR) {
                //copy, then check if improper
                cur_list->car = vararg_cur_pair->car.as.pair->car;
                cur_list->cdr = vararg_cur_pair->car.as.pair->cdr;
                is_list_initialized = true;
                cur_list = advance_lst_to_end(cur_list);
                //if list is improper, check that current vararg is the last one
                if (is_list_improper(cur_list)) {        
                        if(vararg_cur_pair->cdr.type != VAL_EMPTY_LIST) {
                        abort_message("in append. Expected a pair.\n");
                        }
                        return (long)make_value_pair(appended_list);
                }

                } else if (vararg_cur_pair->car.type != VAL_EMPTY_LIST) {
                        //check if there is another vararg. If so,throw error.
                        //otherwise return the val type
                        if(vararg_cur_pair->cdr.type != VAL_EMPTY_LIST) {
                                abort_message("in append. Expected a pair.\n");
                        }
                        if (is_non_ptr_type(&vararg_cur_pair->car)) {
                                return vararg_cur_pair->car.as.tagged_type;
                        } else return (long)&vararg_cur_pair->car;
                }
        //remember varargs are always set up to be a proper list. so if the
        //cdr is not a pair, its guaranteed to be an empty list
                if (vararg_cur_pair->cdr.type != VAL_PAIR) {
                        if (!is_list_initialized) {
                        abort_message("Reached the end of vararg without initializing list!\n");
                        }
                        return (long)make_value_pair(appended_list);
                } 
                vararg_cur_pair = vararg_cur_pair->cdr.as.pair;
        }
        //now traverse rest of varargs, adding each vararg to the cdr of cur_list.
        append_to_list(cur_list,vararg_cur_pair);
        return (long)make_value_pair(appended_list);
}

Value *_make_vector(long self,long size, long init_value)
{
        if (!is_int(size)) {
                abort_message("in make-vector. size must be an integer.\n");
        }
        long untagged_size = untag_int(size);
        Value *vec = make_tagged_ptr(untagged_size);
        bool is_init_ptr = is_ptr(init_value);
        for (int i = 0; i < untagged_size ; i++) {
                if (!is_init_ptr) {
                        turn_to_val_type(init_value,&vec[i]);
                } else {
                        vec[i].type =((Value *)init_value)->type;
                        vec[i].as.tagged_type =((Value *)init_value)->as.tagged_type;
                } 
        }
        return make_value_vector(vec,untagged_size);
}

long _vector_ref(long self,long vector, long position)
{
        if (!is_ptr(vector)) {
                abort_message("in vector-ref. Expected a vector.\n");
        } else if (((Value *)vector)->type != VAL_VECTOR) {
                abort_message("in vector-ref. Expected a vector.\n");
        } else if (!is_int(position)) {
                abort_message("in vector-ref. Expected an int for position.\n");
        }
        long vec_size = ((Value *)vector)->as.vector->size;
        long untagged_position = untag_int(position);
        if (untagged_position < 0 || untagged_position > (vec_size - 1)) {
                abort_message("in vector-ref. Position out of range.\n");
        }
        Value *vec_items = ((Value *)vector)->as.vector->items;
        if (is_non_ptr_type(&vec_items[untagged_position])) {
                return vec_items[untagged_position].as.tagged_type;
        }
        return (long)&vec_items[untagged_position];
}

long _vector_length(long self,long vector)
{
        if (!is_ptr(vector)) {
                abort_message("in vector-length. Not a vector.\n");
        } else if (((Value *)vector)->type != VAL_VECTOR) {
                abort_message("in vector-length. Not a vector.\n");
        }
        return make_tagged_int(((Value *)vector)->as.vector->size);
}

void _vector_set(long self, long vector,long position, long new_val)
{
        if (!is_ptr(vector)) {
                abort_message("in vector-set!. Expected a vector.\n");
        } else if (((Value *)vector)->type != VAL_VECTOR) {
                abort_message("in vector-set!. Expected a vector.\n");
        } else if (!is_int(position)) {
                abort_message("in vector-set!. Expected an int for position.\n");
        }
        long vec_size = ((Value *)vector)->as.vector->size;
        long untagged_position = untag_int(position);
        if (untagged_position < 0 || untagged_position > (vec_size - 1)) {
                abort_message("in vector-set!. Position out of range.\n");
        }
        Value *vec_items = ((Value *)vector)->as.vector->items;
        if (!is_ptr(new_val)) {
                turn_to_val_type(new_val,&vec_items[untagged_position]);
        } else {
                vec_items[untagged_position].type = ((Value *)new_val)->type;
                vec_items[untagged_position].as.tagged_type = ((Value *)new_val)->as.tagged_type;
        }
}
//implements pair?
long _pairq(long self, long val)
{
        long res = SCHEME_FALSE;
        if (is_ptr(val) && ((Value *)val)->type == VAL_PAIR) {
                res = SCHEME_TRUE;
        }
        return res;
}

//implements list?
long _listq(long self,long val)
{
        long res = SCHEME_FALSE;
        if (is_ptr(val)) {
                int type = ((Value *)val)->type;
                if (type == VAL_EMPTY_LIST){
                        return SCHEME_TRUE;
                } else if (type != VAL_PAIR) {
                        return SCHEME_FALSE;
                }
                struct Pair *lst = ((Value *)val)->as.pair;
                lst = advance_lst_to_end(lst);
                if (lst->cdr.type == VAL_EMPTY_LIST) {
                        res = SCHEME_TRUE;
                }
        }
        return res;
}

//implements vector?
long _vectorq(long self, long val)
{
        long res = SCHEME_FALSE;
        if (is_ptr(val) && ((Value *)val)->type == VAL_VECTOR) {
                res = SCHEME_TRUE;
        }
        return res;
}
bool is_list_improper(struct Pair *list)
{
        if (list->cdr.type == VAL_EMPTY_LIST || list->cdr.type == VAL_PAIR) {
                return false;
        }
        return true;
}

//list will be the last pair of the list, i.e. cdr wont be a list
struct Pair *advance_lst_to_end(struct Pair *list)
{
        while (list->cdr.type == VAL_PAIR) {
                list = list->cdr.as.pair;
        }
        return list;
}

//given a list in first arg and varargs as second arg,append varargs to list
void append_to_list(struct Pair *list,struct Pair *varargs)
{
        bool end_of_varargs = false;
        while (!end_of_varargs) {
                //add to the cdr of the list
                list->cdr.type = varargs->car.type;
                list->cdr.as.tagged_type = varargs->car.as.tagged_type;
                if (varargs->car.type == VAL_PAIR) {        
                        list = advance_lst_to_end(list);
                        if (is_list_improper(list)) {        
                                if(varargs->cdr.type != VAL_EMPTY_LIST) {
                                abort_message("in append. Expected a pair.\n");
                                }
                        break;
                        }
                        //below is non_pair case
                } else if (varargs->car.type != VAL_EMPTY_LIST) {

                        if(varargs->cdr.type != VAL_EMPTY_LIST) {
                                abort_message("in append. Expected a pair.\n");
                        }
                        break;
                }
                //advance to next, set end_of_args
                if (varargs->cdr.type != VAL_PAIR) {
                        end_of_varargs = true;
                }
                else {
                        varargs = varargs->cdr.as.pair;
                }
        }
}

//for checking if str types or symbol types are equal?
long are_str_types_equal(Value *value1, Value *value2)
{
        if (value1->as.str->length != value2->as.str->length ) {
                return SCHEME_FALSE;
        }
        int res = strcmp(value1->as.str->chars, value2->as.str->chars);
        if (res == 0) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long are_pairs_equal(Value *value1, Value *value2)
{
        struct Pair *val1_cur_pair = value1->as.pair;
        struct Pair *val2_cur_pair = value2->as.pair;
        long res = _equal(0,(long)&val1_cur_pair->car, (long)&val2_cur_pair->car);
        if(res == SCHEME_FALSE) {
                return SCHEME_FALSE;
        }
        return _equal(0,(long)&val1_cur_pair->cdr, (long)&val2_cur_pair->cdr);
}

long are_vectors_equal(Value *value1, Value *value2)
{
        struct Vector *vector1 = value1->as.vector;
        struct Vector *vector2 = value2->as.vector;
        long res = SCHEME_FALSE;
        if (vector1->size != vector2->size) {
                return res;
        } else if (vector1->size == 0) {
                return SCHEME_TRUE;
        }
        for (size_t i = 0; i < vector1->size; i++) {
                res = _equal(0,(long)&vector1->items[i], (long)&vector2->items[i]);
                if (res == SCHEME_FALSE) {
                        break;
                }
        }
        return res;
}
void is_function(long type)
{
        Value *value_type = (Value*)type;
        if (!is_ptr(type)) {
                abort_message("in runtime. Argument is not a function\n");
        }
        else if (value_type->type != VAL_FUNCTION) {
                abort_message("in runtime. Argument is not a function\n");
        }
        //return value_type;
}