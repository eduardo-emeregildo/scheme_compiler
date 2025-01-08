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
        if(lst_cur_pair->car.type == VAL_EMPTY_LIST) {
                print_value_type(get_car_ptr(lst_cur_pair));
                return;
        }
        printf("(");
        while(lst_cur_pair->car.type != VAL_EMPTY_LIST) {        
                print_value_type(get_car_ptr(lst_cur_pair));
                if(lst_cur_pair->cdr.type != VAL_PAIR) {
                        //dot notation case
                        if(lst_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                                break;
                        }
                        printf(" ");
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

long _add(Value *param_list){
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
                        // printf("Error in +, Expected a number, got %d\n", cur_param->car.type);
                        // exit(EXIT_FAILURE);
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
{       bool is_res_double = false;
        double minuend_value;
        double substrahend_value;
        if (is_int(minuend)) {
                minuend_value = untag_int(minuend);
        } else if (((Value *)minuend)->type == VAL_DOUBLE) {
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
        if (is_res_double) {
                return (long)make_value_double(minuend_value - substrahend_value);
        }
        return make_tagged_int(minuend_value - substrahend_value);
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