// gcc -Wall -o identifier identifier.c

//now that make_val_pair is done, make a function that creates lists using
//this function

//Todo: work on making heap objects. i.e. implement: make_value_pair,make_vector,make_function,make_symbol
//Todo: remove the magic numbers in make_tagged_x functions. Make an enum instead
// at some point figure out which functions need to be inline
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
        void *vector;
        void *function;
        void * symbol;
        // int empty_list;
        long tagged_type; // only exists if a elt in lst is int,char,bool
    } as;
} Value;


//if car.type = VAL_EMPTY_LIST and cdr.type = VAL_EMPTY_LIST, its an empty list
// cdr.type = VAL_EMPTY_LIST indicates the end of a list
// empty list would only be used if one of the list elements is an empty list
//i.e. '(1 2 () 3)
struct Pair{
    Value car;
    Value cdr;
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

void check_int_range(long num){
    if (num > MAX_SCHEME_INT || num < MIN_SCHEME_INT){
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

Value* make_tagged_ptr(){
    Value *p = (Value *)malloc(sizeof(Value));
    if (p == NULL){
        abort_message("Ran out of memory or tried to malloc with negative bytes.");
    }
    return p;
}

long make_tagged_bool(bool boolean){
    return ((long)boolean << 3) | 0x2;
}

long make_tagged_char(char character){
    return ((long)character << 3) | 0x4;
}

// removes tag for bool,char ONLY. int is handled differently, and we leave ptrs alone
long remove_tag(long tagged_item){
    return tagged_item >> 3;
}


/*
these next functions should only be used for list/vector elements.
declaring an int,char, or bool that isnt a vector elt should be done with the
functions above
*/

Value *make_value_int(long integer)
{
        Value *ptr_value_int = make_tagged_ptr();
        ptr_value_int->type = VAL_INT;
        ptr_value_int->as.tagged_type = make_tagged_int(integer);
        return ptr_value_int;
}

Value *make_value_char(char character)
{
        Value *ptr_value_char = make_tagged_ptr();
        ptr_value_char->type = VAL_CHAR;
        ptr_value_char->as.tagged_type = make_tagged_char(character);
        return ptr_value_char;
}

Value *make_value_bool(bool boolean)
{
        Value *ptr_value_bool = make_tagged_ptr();
        ptr_value_bool->type = VAL_BOOLEAN;
        ptr_value_bool->as.tagged_type = make_tagged_bool(boolean);
        return ptr_value_bool;
}

void validate_ptr(void *ptr)
{
        if(ptr == NULL){
                abort_message("Ran out of memory.");
        }
}

struct Str *allocate_str()
{
        struct Str *str_obj = (struct Str *)malloc(sizeof(struct Str));
        validate_ptr(str_obj);
        return str_obj;
}

struct Pair *allocate_pair() 
{
       struct Pair *pair_obj = (struct Pair *)malloc(sizeof(struct Pair));
       validate_ptr(pair_obj);
       return pair_obj; 
}


//////////////////////////////////////////// Heap Objs Below ////////////////////////////////////////////
// make_value_string,make_value_pair,make_vector,make_function,make_symbol
Value *make_value_double(double num){
    Value *ptr_value_double = make_tagged_ptr();
    ptr_value_double->type = VAL_DOUBLE;
    ptr_value_double->as._double = num;
    return ptr_value_double;
}

Value *make_value_string(char *str){
    // malloc the necessary bytes. set to ptr
    // create the boxed type: [VAL_STR | ptr to string struct]
    // make ptr point to the boxed
    Value *ptr_value_string = make_tagged_ptr();
    size_t string_length = strlen(str);
    ptr_value_string->type = VAL_STR;
    struct Str *str_obj = allocate_str(); 
    str_obj->length = string_length;
    str_obj->chars = malloc(string_length);
    strncpy(str_obj->chars,str,string_length);
    ptr_value_string->as.str = str_obj;
    return ptr_value_string;
}

/*
should only be used if the empty list is a list element. 
NOT to denote the end of list
*/
Value *make_empty_list()
{
        Value *ptr_value_empty_list = make_tagged_ptr();
        ptr_value_empty_list->type = VAL_PAIR;
        struct Pair *pair_obj = allocate_pair();
        pair_obj->car.type = VAL_EMPTY_LIST;
        pair_obj->cdr.type = VAL_EMPTY_LIST;
        ptr_value_empty_list->as.pair = pair_obj;
        return ptr_value_empty_list;
}

// creates a pair given the car and cdr.
// the parameters are pointers to already allocated Values on the heap
Value *make_value_pair(Value *car_val,Value *cdr_val)
{
        Value *ptr_value_pair = make_tagged_ptr();
        ptr_value_pair->type = VAL_PAIR;
        struct Pair *pair_obj = allocate_pair();
        pair_obj->car = *car_val;
        pair_obj->cdr = *cdr_val;
        ptr_value_pair->as.pair = pair_obj;
        return ptr_value_pair;
}

/* 
input should be..
an array of value ptrs(that are already alloced on the heap), going in reverse.
so last value is on index 0. This is so that next pair is already allocated

returns a Value obj with type pair, as a pair

The empty list is denoted by car.type = Val_empty_list and cdr.type = val_empty_list
if only cdr.type = empty list, then that is the end of the list. 
I could make it so that the last elt's cdr points to [VAL_EMPTY | 0], 
but this would allocate an extra 16 bytes for each list. 
*/
Value *make_value_list(Value **value_obj_array,size_t len)
{
        Value *cur_value_obj;
        for(size_t i = 0; i < len ; i++) {
                struct Pair *pair_obj = allocate_pair();
                pair_obj->car = *value_obj_array[i];
                if(i == 0) {
                        pair_obj->cdr.type = VAL_EMPTY_LIST;
                } else{
                        // set the cdr to previous Value res
                        pair_obj->cdr = *cur_value_obj;
                }
                cur_value_obj = make_tagged_ptr();
                cur_value_obj->type = VAL_PAIR;
                cur_value_obj->as.pair = pair_obj;            
        }
        return cur_value_obj;
}

int main(){
    long test = 0x000000004;
    printf("is_int test: %d\n",is_int(test));
    printf("is_ptr test: %d\n",is_ptr(test));
    printf("is_bool test: %d\n",is_bool(test));
    printf("is_char test: %d\n",is_char(test));
    printf("Max Int is: %ld\n",MAX_SCHEME_INT);
    printf("Min Int is: %ld\n",MIN_SCHEME_INT);
    Value *addr = make_tagged_ptr();
    printf("ADDRESS IS: %p\n", addr);

    long tag_int_test = make_tagged_int(0x873);
    long untagged_int = untag_int(tag_int_test);
    printf("TAGGED INT IS NOW: %ld\t IN HEX ITS: %#018lx\n",tag_int_test,tag_int_test);
    printf("UNTAGGING THE INT NOW GIVES: %ld\t IN HEX ITS: %#018lx\n",untagged_int,untagged_int);
    long bool_test = make_tagged_bool(true);
    long untagged_bool = remove_tag(bool_test);
    printf("TAGGED BOOL IS NOW: %ld\t IN HEX ITS: %#018lx\n",bool_test,bool_test);
    printf("UNTAGGED BOOL IS NOW: %ld\t IN HEX ITS: %#018lx\n",untagged_bool,untagged_bool);
    char input_char = 'A';
    long char_test = make_tagged_char(input_char);
    long untagged_char = remove_tag(char_test);
    printf("TAGGED CHAR IS NOW: %ld\t IN HEX ITS: %#018lx\n",char_test,char_test);
    printf("UNTAGGED CHAR IS NOW: %ld\t IN ASCII ITS: %c\n",untagged_char,(char)untagged_char);

    //testing functions that check the tag
    long res_array[] = {tag_int_test,bool_test,char_test,addr};
    int length = sizeof(res_array) / sizeof(res_array[0]);
    for(int i = 0; i < length; i++ ){
        printf("%d\n",is_int(res_array[i]));
        printf("%d\n",is_ptr(res_array[i]));
        printf("%d\n",is_bool(res_array[i]));
        printf("%d\n\n",is_char(res_array[i]));
    }
    Value *double_on_heap = make_value_double(25.2);
    printf("%lf\n", double_on_heap->as._double);
    printf("Address of value_type: %p\n", double_on_heap);

    char a[5] = "hello";
    char *b = "hello";
    char *c = malloc(5);
    printf("Size is: %ld\n",strlen(a));
    printf("Size is: %ld\n",strlen(b));
    printf("%c\n",a[0]);
    printf("%c\n",b[3]);
    printf("b is: %s\n",b);
    strncpy(c,b,5);
    printf("c is: %s\n",b);
    Value *str_on_heap = make_value_string("a");
    printf("STRING ON HEAP TYPE: %d\n",str_on_heap->type);
    printf("STRING ON HEAP LENGTH: %d\n",str_on_heap->as.str->length);
    printf("STRING ON HEAP CONTENTS: %s\n",str_on_heap->as.str->chars);

    Value *int_on_heap = make_value_int(4);
    Value *int2_on_heap = make_value_int(5);
    printf("INT ON HEAP TYPE: %d\n",int_on_heap->type);
    printf("INT ON HEAP VAL: %ld\n",untag_int(int_on_heap->as.tagged_type));

    Value *pair_on_heap = make_value_pair(int_on_heap,int2_on_heap);
    printf("PAIR ON HEAP TYPE: %d\n",pair_on_heap->type);
    printf("PAIR ON HEAP CAR: %ld\n",untag_int(pair_on_heap->as.pair->car.as.tagged_type));
    printf("PAIR ON HEAP CDR: %ld\n",untag_int(pair_on_heap->as.pair->cdr.as.tagged_type));

        //testing that make_value_list handles nested lists.
        Value *first_elt = make_value_int(3);
        Value *second_elt = make_value_int(2);
        Value *third_elt = make_value_int(1);

        // arrays get decayed to ptrs, so this is a double ptr.
        Value *input_for_list[4] = {first_elt,second_elt,pair_on_heap,third_elt};
        printf("First elt type: %d\n", input_for_list[0]->type);

    Value *lst = make_value_list(input_for_list,4);
    struct Pair *cur = lst->as.pair;
    while(cur->cdr.type != VAL_EMPTY_LIST){

        if(cur->car.type == VAL_PAIR) {
                //print the pair
                struct Pair *nested_pair = cur->car.as.pair;
                printf("Printing pair:\n");
                printf("car: %ld\n",untag_int(nested_pair->car.as.tagged_type));
                printf("cdr: %ld\n",untag_int(nested_pair->cdr.as.tagged_type));
        }

        else {
                printf("%ld\n",untag_int(cur->car.as.tagged_type));
        }
        cur = cur->cdr.as.pair;
        if(cur->cdr.type == VAL_EMPTY_LIST){
                printf("%ld\n",untag_int(cur->car.as.tagged_type));
        }
    }
    return 0;
}
