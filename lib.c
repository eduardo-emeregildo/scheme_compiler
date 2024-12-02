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
                printf("function at: %p\n",value_obj->as.function);
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
        while(lst_cur_pair->cdr.type != VAL_EMPTY_LIST) {
                printf(" ");        
                print_value_type(get_car_ptr(lst_cur_pair));
                if(lst_cur_pair->cdr.type != VAL_PAIR) {
                        //dot notation case
                        if(lst_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                                break;
                        }
                        // printf("%ld\n",untag_int(lst_cur_pair->cdr.as.tagged_type));
                        print_value_type(get_cdr_ptr(lst_cur_pair));
                        break;
                }
                lst_cur_pair = lst_cur_pair->cdr.as.pair;
                if(lst_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                        // printf("%ld\n",untag_int(lst_cur_pair->car.as.tagged_type));
                        print_value_type(get_car_ptr(lst_cur_pair));
                        break;
                }
        }
        printf(" )\n");

}

void print_vector(Value *value_obj)
{
        printf("#(");
        Value *vec = value_obj->as.vector->items;
        int vec_len = value_obj->as.vector->size;
        for(size_t i = 0; i < vec_len ; i++) {
                printf(" ");
                print_value_type(&vec[i]);
        }
        printf(" )\n");
}
void _display(void *type)
{
        long long_type = (long)type;
        if (is_ptr(long_type)) {
                print_value_type((Value *)type);

        } else if (is_int(long_type)) {
                printf("%ld\n", untag_int(long_type));
        } else if (is_bool(long_type)) {
                printf("0x%ld\n",remove_tag(long_type));
        } else if (is_char(long_type)) {
                printf("%c\n",(int)remove_tag(long_type));
        }
        else {
                abort_message("Error in display function. Not a valid type.");
        }
}