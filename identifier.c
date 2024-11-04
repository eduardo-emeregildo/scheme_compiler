// gcc -o identifier identifier.c
//the goal (to start) is to deal with (define x 5)
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <limits.h>
#include <stdbool.h>
#include <math.h>

//signed 64 bit int: [-2^63,2^63 - 1]
// for signed 63 bit int: [-2^62, 2^62 - 1]
const long MAX_SCHEME_INT = 0x3fffffffffffffff; 
const long MIN_SCHEME_INT = 0xc000000000000000;
typedef enum{
   VAL_CHAR,
   VAL_STR,
   VAL_INT,
   VAL_FLOAT,
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
        char *str;
        double floating_point;
        // these might be ptrs to structs instead. For now leave as this.
        void *pair;
        void *vector;
        void *function;
        void * symbol;
    } as;
} Value;

typedef enum{
    TAG_PTR = 0x0,
    TAG_INT = 0x1,
    TAG_BOOL = 0x2,
    TAG_CHAR = 0x3
    

} TagType;

struct List{
    Value car;
    Value cdr;
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
    // printf("Before tagging: %#018lx\n",num);
    // printf("After tagging: %#018lx\n",(num << 1) + 1);
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

void* make_tagged_ptr(size_t num_bytes){
    void *p = malloc(num_bytes);
    if (p == NULL){
        abort_message("Ran out of memory or tried to malloc with negative bytes.");
    }
    return p;
}

long make_tagged_bool(long boolean){

}
long make_tagged_char(long character){

}

// removes tag for bool,char,int. Since ptrs tag is 000, no need to do anything here
long remove_tag(long tagged_item){

}

int main(){

    TagType var = TAG_CHAR;
    printf("%d\n",var);
    long test = 0x000000004;
    printf("is_int test: %d\n",is_int(test));
    printf("is_ptr test: %d\n",is_ptr(test));
    printf("is_bool test: %d\n",is_bool(test));
    printf("is_char test: %d\n",is_char(test));
    printf("Max Int is: %ld\n",MAX_SCHEME_INT);
    printf("Min Int is: %ld\n",MIN_SCHEME_INT);
    int yes  = 1;
    void *addr = make_tagged_ptr(yes);
    printf("ADDRESS IS: %p\n", addr);

    long tag_int_test = make_tagged_int(0x873);
    long untagged_int = untag_int(tag_int_test);
    printf("TAGGED INT IS NOW: %ld\t IN HEX ITS: %#018lx\n",tag_int_test,tag_int_test);
    printf("UNTAGGING THE INT NOW GIVES: %ld\t IN HEX ITS: %#018lx\n",untagged_int,untagged_int);
    
    return 0;
}
