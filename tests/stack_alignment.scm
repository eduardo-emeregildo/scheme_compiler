
(display "testing alignment of normal functions")
(define (funcn one two three four five six seven) 
    (display funcn) (display one) (display two) (display three) (display four) 
    (display five) (display six) (display seven))
(funcn 1 2 3 4 5 6 7.4)
(display '(1 2 3.4 4))
(define (funcn1 one two) (display one) (display two))
(funcn1 1 2)

(display "testing alignment of variadic functions")

;no alignment needed, 7th arg at an offset thats 16 byte aligned
(define (var_fun one two three four five six . seven) seven)
(display (var_fun 1 2 3 4 5 6))

;alignment needed, 7th arg not at an offset thats 16 byte aligned
(define (var_fun2 one two three four five six . seven) (display six))
(var_fun2 1 2 3 4 5 6.1 7)

(display "testing alignment for general function calls")

;general_function_call with a normal function. working
(define (foo one two three four five six) (display six))
(define (func op) (define x 3) (op 1 2 3 4 5 6.1))
(func foo)

;general_function_call with a variadic function,stackargs. working
(define (foo1 one two three four five . six) (display five))
(define (func1 op) (define x 3) (op 1 2 3 4 5.2 6))
(func1 foo1)

;general_function_call with a variadic function, no stackarg. working
(define (foo2 one . two) (display one))
(define (func2 op) (op 1.1 2))
(func2 foo2)


(display "stack alignment for lambdas:")
;plain lambdas:
((lambda (one two three four five six seven) (display seven)) 1 2 3 4 5 6 7.5)

;variadic lambdas:
((lambda (one two three four five six . seven) (display six)) 1 2 3 4 5 6.1 7)

;using lambdas in a general function call(non variadic)
(define (func3 op) (define x 3) (op 1 2 3 4 5 6.1))
(func3 (lambda (one two three four five six) (display six)))

;using lambdas in a general function call, variadic, no stack args
(define (func4 op) (op 1.1 2))
(func4 (lambda (one . two) (display one)))

;using lambdas in a general function call, variadic, with stack args
(define (func5 op) (define x 3) (op 1 2 3 4 5.2 6))
(func5 (lambda (one two three four five six) (display five)))

(display "stack alignment for lets:")
;using let, stack needs to be aligned. Working
(let ((one 1) (two 2) (three 3) (four 4) (five 5) (six 6.1)) (display six))

;stack is naturally aligned. Working
(let ((one 1) (two 2.3)) (display two))