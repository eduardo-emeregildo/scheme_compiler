;given the varargs array in rax, 
;the arity in rbx, min_args in r10, and env depth at r11,
;r12 is reserved for counting cur_arg,initialized to 0
;r13 is the offset of the function
;Do the following asm:

;assume arity is 5, min_args is 4

;regs in use, rax,rbx,r10,r11,r12,r13

; ill use r14 reg and others for temporary storage
%define ith_regarg_offset (r11 + (8*(r12 + 1)))
%define ith_stackarg_offset (r11 + ((rbx - r12) * 8))
%define seventh_arg_offset (r11 + ((r14 + 1) * 8))

%macro move_to_reg 0
        cmove r9, QWORD [rbp - ith_regarg_offset]
        cmp r12,0
        cmove rdi, QWORD [rbp - ith_regarg_offset]
        cmp r12,1
        cmove rsi, QWORD [rbp - ith_regarg_offset]
        cmp r12,2
        cmove rdx, QWORD [rbp - ith_regarg_offset]
        cmp r12,3
        cmove rcx, QWORD [rbp - ith_regarg_offset]
        cmp r12,4
        cmove r8, QWORD [rbp - ith_regarg_offset]
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
                mov r14, QWORD [rbp - ith_regarg_offset]
                mov QWORD [rbp - ith_stackarg_offset], r14
                inc r12
                jmp %%loop
        %%varargs:
                ; mov varargs in rax to corresponding spot.
                ; basically itll put the varargs where the next arg would be on the stack
                ; and jumps back
                mov QWORD [rbp - ith_regarg_offset], rax
                jmp %%register_args
        %%function_call:
                ; subtrack the correct amt from rsp, do the function call, add rsp back
                mov r14, rbx
                sub r14, 7
                jge %%stack_args_function_call
                ; no stack args case
                lea rsp, QWORD [rsp - r11]
                mov rax,  QWORD [rbp - r13] ; varargs already placed so rax is free
                add rax, 8
                mov rax, QWORD [rax]
                call QWORD [rax]
                lea rsp, QWORD [rsp + r11]

                ;stack args case, rsp has to point to 7th arg
        %%stack_args_function_call:
                lea rsp, QWORD [rsp - seventh_arg_offset]
                mov rax,  QWORD [rbp - r13] ; varargs already placed so rax is free
                add rax, 8
                mov rax, QWORD [rax]
                call QWORD [rax]
                lea rsp, QWORD [rsp + seventh_arg_offset]
%endmacro