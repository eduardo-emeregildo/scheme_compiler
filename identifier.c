// gcc -Wall -o identifier identifier.c

// see if i can do the same change that i did to vector and make_value_vector to pairs.
//Todo0: test make_value_string, then write make_value_symbol. should be the same thing as with string.
//Todo1: remove the magic numbers in make_tagged_x functions. Make an enum instead
//Todo2: figure out which functions need to be inline
//Todo3: start working on the parser so that it emits asm code that calls these functions

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

// for signed 63 bit int: [-2^62, 2^62 - 1]
const long MAX_SCHEME_INT = 0x3fffffffffffffff; 
const long MIN_SCHEME_INT = 0xc000000000000000;
typedef enum{
   VAL_CHAR,
   VAL_STR,
   VAL_INT,
   VAL_DOUBLE,
   VAL_BOOLEAN,
   VAL_PAIR,
   VAL_VECTOR,
   VAL_FUNCTION,
   VAL_SYMBOL,
   VAL_EMPTY_LIST

} ValueType;

// this is for boxed types on the heap
typedef struct{
    ValueType type;
    union{
        struct Str *str;
        double _double;
        struct Pair *pair;
        struct Vector *vector;
        void *function;
        void * symbol;
        long tagged_type; // only exists if a elt in lst is int,char,bool
    } as;
} Value;


// car = NULL denotes the empty list
// cdr = NULL indicates the end of a list
// empty list would only be used if one of the list elements is an empty list
//i.e. '(1 2 () 3)
struct Pair{
    Value *car;
    Value *cdr;
};

struct Str{
    int length;
    char* chars; 
};

struct Vector{
    int size;
    Value *items;
};

//pass either the 64 bit val or the 64 bit addr(for pointers)
bool is_int(long item){
    return (item & 0x1) == 1;
}

bool is_ptr(long item){
    return (item & 0x7) == 0;
}

bool is_bool(long item){
    return (item & 0x7) == 2;
}

// a tagged char is stored in 8 bytes so just pass it as a long
bool is_char(long item){
    return (item & 0x7) == 4;
}

void abort_message(char *error_message){
    printf("Error. %s",error_message);
    exit(EXIT_FAILURE);
}

void check_int_range(long num)
{
        if (num > MAX_SCHEME_INT || num < MIN_SCHEME_INT) {
                abort_message("Integer out of range");
        }
}

long make_tagged_int(long num){
    check_int_range(num);
    return (num << 1) + 1;
}

long untag_int(long num){
    //checks msb to see if number is negative
    //can do this with the bit mask 0x8000000000000000
    if((num & 0x8000000000000000) == 0){
        return (num >> 1);
    } else{
        return (num >> 1) | 0x8000000000000000;
    }
}

Value *make_tagged_ptr(size_t num_value_objects){
    Value *p = (Value *)malloc(sizeof(Value)*num_value_objects);
    if (p == NULL){
        abort_message("Ran out of memory or tried to malloc with negative bytes.");
    }
    return p;
}

long make_tagged_bool(bool boolean)
{
        return ((long)boolean << 3) | 0x2;
}

long make_tagged_char(char character)
{
        return ((long)character << 3) | 0x4;
}

// removes tag for bool,char ONLY. int is handled differently, and we leave ptrs alone
long remove_tag(long tagged_item)
{
        return tagged_item >> 3;
}

void validate_ptr(void *ptr)
{
        if(ptr == NULL){
                abort_message("Ran out of memory.");
        }
}


/*
//////////////////////////////////////////// Heap Objs Below ////////////////////////////////////////////

these next functions should only be used for list/vector elements.
declaring an int,char, or bool that isnt in a vector/list should be done with the
functions above
*/

Value *make_value_int(long integer)
{
        Value *ptr_value_int = make_tagged_ptr(1);
        ptr_value_int->type = VAL_INT;
        ptr_value_int->as.tagged_type = make_tagged_int(integer);
        return ptr_value_int;
}

Value *make_value_char(char character)
{
        Value *ptr_value_char = make_tagged_ptr(1);
        ptr_value_char->type = VAL_CHAR;
        ptr_value_char->as.tagged_type = make_tagged_char(character);
        return ptr_value_char;
}

Value *make_value_bool(bool boolean)
{
        Value *ptr_value_bool = make_tagged_ptr(1);
        ptr_value_bool->type = VAL_BOOLEAN;
        ptr_value_bool->as.tagged_type = make_tagged_bool(boolean);
        return ptr_value_bool;
}

//given a character arr allocated on the heap, return ptr to Str object
struct Str *allocate_str(char *str)
{

        struct Str *str_obj = (struct Str *)malloc(sizeof(struct Str));
        validate_ptr(str_obj);
        size_t length = strlen(str);
        str_obj->length = length;
        str_obj->chars = str;
        return str_obj;
}

struct Pair *allocate_pair(Value *car_val,Value *cdr_val) 
{
        struct Pair *pair_obj = (struct Pair *)malloc(sizeof(struct Pair));
        validate_ptr(pair_obj);
        pair_obj->car = car_val;
        pair_obj->cdr = cdr_val;
        return pair_obj; 
}

//takes in array of vector objects that are already allocated to the heap.
struct Vector *allocate_vector(Value *vec_elts,size_t size)
{
        struct Vector *vec_obj = (struct Vector *)malloc(sizeof(struct Vector));
        validate_ptr(vec_obj);
        vec_obj->size = size;
        vec_obj->items = vec_elts;
        return vec_obj;
}

//set_ith_value and create_value_ptr_arr are helpers for the params of make_value_list

// given an array of value ptrs and a ptr to a Value obj, set the ith position in array to this ptr
//Careful if index is beyond size of arra of value ptrs
void set_ith_value(Value **value_obj_array,Value *elt,size_t index)
{
        value_obj_array[index] = elt;
}

Value **create_val_ptr_arr(size_t length)
{
        Value **val_ptr_arr = (Value **)malloc(sizeof(Value **));
        *val_ptr_arr = (Value *)malloc(sizeof(Value *) * length);
        return val_ptr_arr;

}

//some experimental setter functions to use less pointers
Value *make_value_arr(size_t length)
{
        Value *val_array = make_tagged_ptr(length);
        return val_array;
}
void set_ith_value_int(Value *val_ptr,long integer,size_t index)
{
        val_ptr[index].type = VAL_INT;
        val_ptr[index].as.tagged_type = make_tagged_int(integer);
}

void set_ith_value_char(Value *val_ptr,char character,size_t index)
{
        val_ptr[index].type = VAL_CHAR;
        val_ptr[index].as.tagged_type = make_tagged_char(character);
}

void set_ith_value_bool(Value *val_ptr,bool boolean,size_t index)
{
        val_ptr[index].type = VAL_BOOLEAN;
        val_ptr[index].as.tagged_type = make_tagged_bool(boolean);
}

void set_ith_value_dbl(Value *val_ptr,double num,size_t index)
{
        val_ptr[index].type = VAL_DOUBLE;
        val_ptr[index].as._double = num;
}


void set_ith_value_str(Value *val_ptr,char *str,size_t index)
{
        val_ptr[index].type = VAL_STR;
        val_ptr[index].as.str = allocate_str(str);

}

void set_ith_value_pair(Value *val_ptr,struct Pair *pair_obj,size_t index)
{
        val_ptr[index].type = VAL_PAIR;
        val_ptr[index].as.pair = pair_obj;
}

void set_ith_value_vector(Value *val_ptr,struct Vector *vec,size_t index)
{
        val_ptr[index].type = VAL_VECTOR;
        val_ptr[index].as.vector = vec;
}

// make_value_string,make_value_pair,make_vector,make_function,make_symbol
// the value ptr given in these functions is the Value ptr that you will write to

Value *make_value_double(double num)
{
        Value *ptr_value_double = make_tagged_ptr(1);
        ptr_value_double->type = VAL_DOUBLE;
        ptr_value_double->as._double = num;
        return ptr_value_double;
}

Value *make_value_string(struct Str *str_obj){

        Value *ptr_value_string = make_tagged_ptr(1);
        ptr_value_string->type = VAL_STR;
        ptr_value_string->as.str = str_obj;
        return ptr_value_string;
}


// takes in  pair obj ptr and returns a value obj of type pair
Value *make_value_pair(struct Pair *pair_obj)
{
        Value *ptr_value_pair = make_tagged_ptr(1);
        ptr_value_pair->type = VAL_PAIR;
        ptr_value_pair->as.pair = pair_obj;
        return ptr_value_pair;
}

/* 
input is an array of value ptrs(that are already alloced on the heap).
returns a Value obj with type pair, as a pair.
the empty list is denoted by car = NULL. The end of list is denoted by 
cdr = NULL

ex: for the list '(1 2 3),
for each element, generate a value obj for this elt. the ptr will be be in rax.
then this gets put into an array of value ptrs. After each elt in the list is
processed, pass that array of value ptrs to this function to create the list. 
*/
Value *make_value_list(Value **value_obj_array, size_t len)
{       
        Value *ptr_value_list = make_tagged_ptr(1);   
        ptr_value_list->type = VAL_PAIR;
        struct Pair *head = allocate_pair(NULL,NULL);
        struct Pair *cur_pair = head;
        size_t last_item_index = len - 1; 
        for(size_t i = 0; i < len; i++) {
                cur_pair->car = value_obj_array[i];
                if((i != last_item_index)) {
                        cur_pair->cdr = make_value_pair(allocate_pair(NULL,NULL));
                        cur_pair = cur_pair->cdr->as.pair;
                }        
        }
        ptr_value_list->as.pair = head;
        return ptr_value_list;
}

/*
takes in an array of value objects and creates a vector object out of these. 
On the python side, when parsing say #(1 2 3), it will first parse the whole thing
to figure out the length, then allocate the correct arr of value objects.
*/
Value *make_value_vector(Value *value_obj_array, size_t len)
{
        Value *ptr_value_vector = make_tagged_ptr(1); 
        ptr_value_vector->type = VAL_VECTOR;
        struct Vector *vector_obj = allocate_vector(value_obj_array,len);
        ptr_value_vector->as.vector = vector_obj;
        return ptr_value_vector;
}

int main()
{
        Value *car = make_value_int(1);
        Value *cdr = make_value_int(2);
        printf("%d\n",car->type);
        printf("%p\n",car);
        printf("NOW TESTING THE PAIR '(1 . 2)\n");
        struct Pair *pair = allocate_pair(car,cdr);
        printf("CAR: %ld\n",untag_int(pair->car->as.tagged_type));
        printf("CDR: %ld\n",untag_int(pair->cdr->as.tagged_type));
        printf("NOW TESTING LISTS:\n");
        Value *third = make_value_int(3);
        Value *input_for_list[3] = {car,cdr,third};
        Value *lst = make_value_list(input_for_list,3);
        struct Pair *cur_pair = lst->as.pair;
        while (cur_pair->cdr != NULL) {
                printf("%ld\n",untag_int(cur_pair->car->as.tagged_type));
                cur_pair = cur_pair->cdr->as.pair;
                if(cur_pair->cdr == NULL) {
                        printf("%ld\n",untag_int(cur_pair->car->as.tagged_type));
                        break;
                }
        }
        printf("NOW TESTING VECTORS:\n");

        /*
        this is how calls to this file in python will look when building 
        an array of vec objects
        */
        Value *input_for_vec = make_value_arr(3);
        set_ith_value_int(input_for_vec,1,0);
        set_ith_value_int(input_for_vec,2,1);
        set_ith_value_int(input_for_vec,3,2);
        Value *vec = make_value_vector(input_for_vec,3);
        printf("%ld\n", untag_int(vec->as.vector->items[0].as.tagged_type));
        printf("%ld\n", untag_int(vec->as.vector->items[1].as.tagged_type));
        printf("%ld\n", untag_int(vec->as.vector->items[2].as.tagged_type));
        return 0;
}