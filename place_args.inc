;linux calling convention: rdi,rsi,rdx,rcx,r8,r9

;rax = varargs
;rbx = arity
;r10 = min_args
;%1 = env_depth (positive)
;%2 = function offset (positive) 
;r12 = cur_arg (init to 0)

;r13 will store the old value of r15. After the function call, it will restore r15.
;this is so that in the stack_args_function_call label, r15 is guaranteed to be
;restored by the callee

;place_args takes in env_depth(positive) and function offset(positive) 
;as args 1 and 2 respectively. 

;all other macros take 1 arg, which is the env_depth


;%define ith_regarg_offset (%1 + (8*(r12 + 1)))
;%define ith_stackarg_offset (%1 + ((rbx - r12) * 8))
;%define seventh_arg_offset (%1 + ((r14 + 1) * 8))

%define FALSE 2
%define TRUE 10

; to compute regarg offset
%macro compute_regarg_offset 1
        mov r14, r12
        inc r14
        imul r14, 8
        add r14,%1
        neg r14
%endmacro

%macro compute_stackarg_offset 1
        mov r15, rbx
        sub r15,r12
        imul r15,8
        add r15,%1
        neg r15
%endmacro

%macro compute_seventh_arg_offset 1
        mov r15, r14
        inc r15
        imul r15, 8
        add r15, %1
        neg r15
%endmacro

%macro move_to_reg 1
        compute_regarg_offset %1
        cmp r12,0
        cmove rdi, QWORD [rbp + r14]
        cmp r12,1
        cmove rsi, QWORD [rbp + r14]
        cmp r12,2
        cmove rdx, QWORD [rbp + r14]
        cmp r12,3
        cmove rcx, QWORD [rbp + r14]
        cmp r12,4
        cmove r8, QWORD [rbp + r14]
        cmp r12, 5
        cmove r9, QWORD [rbp + r14]
%endmacro
;%define ith_regarg_offset (%1 + (8*(r12 + 1)))
;%define ith_stackarg_offset (%1 + ((rbx - r12) * 8))
;%define seventh_arg_offset (%1 + ((r14 + 1) * 8))

%macro place_args 2
        mov r13, r15 ; store old r15 and restore after function call
        %%loop:
                cmp r12,r10
                je %%varargs
                cmp r12, rbx
                je %%function_call
                jl %%register_args
        %%register_args:
                cmp r12, 5
                jg %%stack_args
                move_to_reg %1
                inc r12
                jmp %%loop
        %%stack_args:
                ;for the stack args. -8, is the offset of the last arg,
                ;assuming env depth is 0
                compute_regarg_offset %1
                mov r14, QWORD [rbp + r14]
                ;mov r14, QWORD [rbp - ith_regarg_offset]
                compute_stackarg_offset %1
                mov QWORD [rbp + r15], r14
                inc r12
                jmp %%loop
        %%varargs:
                ; mov varargs in rax to corresponding spot.
                ; basically itll put the varargs where the next arg would be on the stack
                ; and jumps back
                compute_regarg_offset %1
                mov QWORD [rbp + r14], rax
                ;mov QWORD [rbp - ith_regarg_offset], rax
                jmp %%register_args
        %%function_call:
                ; subtrack the correct amt from rsp, do the function call, add rsp back
                mov r14, rbx
                sub r14, 7
                jge %%stack_args_function_call
                ; no stack args case
                sub rsp, %1
                mov rax,  QWORD [rbp - %2] ; varargs already placed so rax is free
                add rax, 8
                mov rax, QWORD [rax]
                call QWORD [rax]
                add rsp, %1
                jmp %%end

                
        %%stack_args_function_call:
                ;stack args case, rsp has to point to 7th arg
                compute_seventh_arg_offset %1
                lea rsp, QWORD [rsp + r15]
                mov rax,  QWORD [rbp - %2] ; varargs already placed so rax is free
                add rax, 8
                mov rax, QWORD [rax]
                call QWORD [rax]
                neg r15
                lea rsp, QWORD [rsp + r15]
        
        %%end:
                mov r15, r13
%endmacro