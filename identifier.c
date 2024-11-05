// gcc -Wall -o identifier identifier.c

//Todo: work on making heap objects. i.e. implement make_string,make_double,make_pair,make_vector,make_function,make_symbol
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>
#include <math.h>
#include <string.h>

//signed 64 bit int: [-2^63,2^63 - 1]
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
   VAL_SYMBOL

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
    } as;
} Value;


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

//////////////////////////////////////////// Heap Objs Below ////////////////////////////////////////////
// make_string,make_pair,make_vector,make_function,make_symbol
Value *make_double(double num){
    Value *ptr_val = make_tagged_ptr();
    ptr_val->type = VAL_DOUBLE;
    ptr_val->as._double = num;
    return ptr_val;
}

Value *make_string(char *str){
    // malloc the necessary bytes. set to ptr
    // create the boxed type: [VAL_STR | ptr to string struct]
    // make ptr point to the boxed
    Value *ptr_val = make_tagged_ptr();
    size_t string_length = strlen(str);
    ptr_val->type = VAL_STR;
    struct Str *str_obj = (struct Str *)malloc(sizeof(struct Str));
    if (str_obj == NULL){
        abort_message("Ran out of memory.");
    }    
    str_obj->length = string_length;
    str_obj->chars = malloc(string_length);
    strncpy(str_obj->chars,str,string_length);
    ptr_val->as.str = str_obj;
    return ptr_val;
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
    Value *double_on_heap = make_double(25.2);
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
    Value *str_on_heap = make_string("a");
    printf("STRING ON HEAP TYPE: %d\n",str_on_heap->type);
    printf("STRING ON HEAP LENGTH: %d\n",str_on_heap->as.str->length);
    printf("STRING ON HEAP CONTENTS: %s\n",str_on_heap->as.str->chars);
    return 0;
}
