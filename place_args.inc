;linux calling convention: rdi,rsi,rdx,rcx,r8,r9

;given the varargs array in rax, 
;the arity in rbx, min_args in r10, and env depth at r11 (positive),
;r12 is reserved for counting cur_arg,initialized to 0
;r13 is the offset of the function (negative)
;Do the following asm:

;assume arity is 5, min_args is 4

;regs in use, rax,rbx,r10,r11,r12,r13

; ill use r14,r15 regs for temporary storage

;%define ith_regarg_offset (r11 + (8*(r12 + 1)))
;%define ith_stackarg_offset (r11 + ((rbx - r12) * 8))
;%define seventh_arg_offset (r11 + ((r14 + 1) * 8))

; to compute regarg offset
%macro compute_regarg_offset 0
        mov r14, r12
        inc r14
        imul r14, 8
        add r14,r11
%endmacro

%macro compute_stackarg_offset 0
        mov r15, rbx
        sub rbx,r12
        imul r15,8
        add r15,r11
        neg r15
%endmacro

%macro compute_seventh_arg_offset 0
        mov r15, r14
        inc r15
        imul r15, 8
        add r15, r11
        neg r15
%endmacro

%macro move_to_reg 0
        compute_regarg_offset
        cmove r9, QWORD [rbp + r14]
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
%endmacro

%macro place_args 0
        %%loop:
                cmp r12, rbx
                jge %%function_call
                jl %%register_args
        %%register_args:
                cmp r12, 5
                jg %%stack_args
                move_to_reg
                inc r12
                cmp r12, r10
                je %%varargs
                jmp %%loop
        %%stack_args:
                ;for the stack args. -8, is the offset of the last arg,
                ;assuming env depth is 0
                compute_regarg_offset
                mov r14, QWORD [rbp + r14]
                ;mov r14, QWORD [rbp - ith_regarg_offset]
                compute_stackarg_offset
                mov QWORD [rbp + r15], r14
                inc r12
                jmp %%loop
        %%varargs:
                ; mov varargs in rax to corresponding spot.
                ; basically itll put the varargs where the next arg would be on the stack
                ; and jumps back
                compute_regarg_offset
                mov QWORD [rbp + r14], rax
                ;mov QWORD [rbp - ith_regarg_offset], rax
                jmp %%register_args
        %%function_call:
                ; subtrack the correct amt from rsp, do the function call, add rsp back
                mov r14, rbx
                sub r14, 7
                jge %%stack_args_function_call
                ; no stack args case
                neg r11
                lea rsp, QWORD [rsp + r11]
                mov rax,  QWORD [rbp + r13] ; varargs already placed so rax is free
                add rax, 8
                mov rax, QWORD [rax]
                call QWORD [rax]
                neg r11
                lea rsp, QWORD [rsp + r11]

                ;stack args case, rsp has to point to 7th arg
        %%stack_args_function_call:
                compute_seventh_arg_offset
                lea rsp, QWORD [rsp + r15]
                mov rax,  QWORD [rbp + r13] ; varargs already placed so rax is free
                add rax, 8
                mov rax, QWORD [rax]
                call QWORD [rax]
                neg r15
                lea rsp, QWORD [rsp + r15]
%endmacro