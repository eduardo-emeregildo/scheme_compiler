// gcc -Wall -O3 -o identifier_test identifier_test.c identifier.c
#include "identifier.h"

int main()
{
        printf("TESTING THE PAIR '(1 . 2)\n");
        struct Pair *pair_obj = allocate_pair();
        set_ith_value_int(get_car_ptr(pair_obj),1,0);
        set_ith_value_int(get_cdr_ptr(pair_obj),2,0);
        printf("CAR: %ld\n",untag_int(pair_obj->car.as.tagged_type));
        printf("CDR: %ld\n",untag_int(pair_obj->cdr.as.tagged_type));
        printf("TESTING MAKE_VALUE_LIST FUNCTION '(3 4 5):\n");
        Value *input_for_list = make_tagged_ptr(3);
        set_ith_value_int(input_for_list,3,0);
        set_ith_value_int(input_for_list,4,1);
        set_ith_value_int(input_for_list,5,2);
        Value *lst = make_value_list(input_for_list,3);
        struct Pair *lst_cur_pair = lst->as.pair;
        while(lst_cur_pair->cdr.type != VAL_EMPTY_LIST) {
                printf("%ld\n",untag_int(lst_cur_pair->car.as.tagged_type));
                lst_cur_pair = lst_cur_pair->cdr.as.pair;
                if(lst_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                        printf("%ld\n",untag_int(lst_cur_pair->car.as.tagged_type));
                        break;
                }
        }

        printf("BUILDING THE LIST '(6 7 8) THE WAY ASM WOULD DO IT:\n");
        struct Pair *new_pair_obj = allocate_pair();
        struct Pair *cur = new_pair_obj;

        set_ith_value_int(get_car_ptr(cur),6,0);
        set_ith_value_pair(get_cdr_ptr(cur),allocate_pair(),0);
        cur = cur->cdr.as.pair;

        set_ith_value_int(get_car_ptr(cur),7,0);
        set_ith_value_pair(get_cdr_ptr(cur),allocate_pair(),0);
        cur = cur->cdr.as.pair;

        set_ith_value_int(get_car_ptr(cur),8,0);

        Value *asm_pair = make_value_pair(new_pair_obj);
        lst_cur_pair = asm_pair->as.pair;
        while(lst_cur_pair->cdr.type != VAL_EMPTY_LIST) {
                printf("%ld\n",untag_int(lst_cur_pair->car.as.tagged_type));
                lst_cur_pair = lst_cur_pair->cdr.as.pair;
                if(lst_cur_pair->cdr.type == VAL_EMPTY_LIST) {
                        printf("%ld\n",untag_int(lst_cur_pair->car.as.tagged_type));
                        break;
                }
        }
        printf("NOW TESTING VECTORS:\n");
        /*
        this is how calls to this file in python will look when building 
        an array of vec objects
        */
        Value *input_for_vec = make_tagged_ptr(3);
        set_ith_value_int(input_for_vec,3,0);
        set_ith_value_int(input_for_vec,4,1);
        set_ith_value_int(input_for_vec,5,2);
        Value *vec = make_value_vector(input_for_vec,3);
        printf("%ld\n", untag_int(vec->as.vector->items[0].as.tagged_type));
        printf("%ld\n", untag_int(vec->as.vector->items[1].as.tagged_type));
        printf("%ld\n", untag_int(vec->as.vector->items[2].as.tagged_type));
        printf("NOW TESTING STRINGS:\n");
        struct Str *str_obj = allocate_str("hello");
        Value *value_obj_str = make_value_string(str_obj);
        printf("%d\n",value_obj_str->type);
        printf("%s\n",value_obj_str->as.str->chars);
        return 0;
}