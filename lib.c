#include "lib.h"
//prints a value type
void print_value_type(Value *value_obj) 
{
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
        default:
                break;
        }
}

void print_list(Value *value_obj)
{
        struct Pair *lst_cur_pair = value_obj->as.pair;
        printf("(");
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
void _display(void *type)
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

long _add(Value *param_list)
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

long _sub(long minuend,Value *varargs)
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

        long substrahend = _add(varargs);
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

long _mul(Value *param_list)
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

long _div(long dividend, Value* varargs) {
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

        long divisor = _mul(varargs);
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

long _equal_sign(long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,"=",untagged_values);
        if (untagged_values[0] == untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _greater(long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,">",untagged_values);
        if (untagged_values[0] > untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _greater_equal(long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,">=",untagged_values);
        if (untagged_values[0] >= untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _less(long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,"<",untagged_values);
        if (untagged_values[0] < untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _less_equal(long value1,long value2)
{
        double untagged_values[2];
        check_and_extract_numbers(value1,value2,"<=",untagged_values);
        if (untagged_values[0] <= untagged_values[1]) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _car(long type)
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

long _cdr(long type)
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

long _null(long type)
{       
        if (!is_ptr(type)) {
                return SCHEME_FALSE;
        }
        else if ( ((Value *)type)->type == VAL_EMPTY_LIST) {
                return SCHEME_TRUE;
        }
        return SCHEME_FALSE;
}

long _eq(long value1,long value2)
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
long _equal(long value1,long value2)
{
        bool is_val1_ptr = is_ptr(value1);
        bool is_val2_ptr = is_ptr(value2);
        long res = SCHEME_FALSE;
        if (is_val1_ptr != is_val2_ptr) {
                return SCHEME_FALSE;
        } else if (!is_val1_ptr) {
                res = _eq(value1, value2);
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
                        res = _eq(value1,value2);
                }
        }
        return res;

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
        long res = _equal((long)&val1_cur_pair->car, (long)&val2_cur_pair->car);
        if(res == SCHEME_FALSE) {
                return SCHEME_FALSE;
        }
        return _equal((long)&val1_cur_pair->cdr, (long)&val2_cur_pair->cdr);
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
                res = _equal((long)&vector1->items[i], (long)&vector2->items[i]);
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