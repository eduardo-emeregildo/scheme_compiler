;testing alignment of normal functions

;(define (func one two three four five six seven) 
    ;(display func) (display one) (display two) (display three) (display four) 
    ;(display five) (display six) (display seven))
;(func 1 2 3 4 5 6 7.4)
;(display '(1 2 3.4 4))
;(define (func2 one two) (display one) (display two))
;(func2 1 2)

;testing alignment of variadic functions:

;no alignment needed, 7th arg at an offset thats 16 byte aligned
;(define (var_fun one two three four five six . seven) seven)
;(display (var_fun 1 2 3 4 5 6))

;alignment needed, 7th arg not at an offset thats 16 byte aligned
;(define (var_fun2 one two three four five six . seven) (display six))
;(var_fun2 1 2 3 4 5 6.1 7)

;testing alignment for general function calls

;general_function_call with a normal function. working
;(define (st one two three four five six) (display six))
;(define (func op) (define x 3) (op 1 2 3 4 5 6.1))
;(func st)

;general_function_call with a variadic function,stackargs. working
;(define (st one two three four five . six) (display five))
;(define (func op) (define x 3) (op 1 2 3 4 5.2 6))
;(func st)

;general_function_call with a variadic function, no stackarg. working
;(define (st one . two) (display one))
;(define (func op) (op 1.1 2))
;(func st)

;stack alignment for lambdas:

;plain lambdas:
((lambda (one two three four five six seven) (display seven)) 1 2 3 4 5 6 7.5)

;variadic lambdas:
((lambda (one two three four five six . seven) (display six)) 1 2 3 4 5 6.1 7)

;using lambdas in a general function call(non variadic)
(define (func op) (define x 3) (op 1 2 3 4 5 6.1))
(func (lambda (one two three four five six) (display six)))

;using lambdas in a general function call, variadic, no stack args
(define (func1 op) (op 1.1 2))
(func1 (lambda (one . two) (display one)))

;using lambdas in a general function call, variadic, with stack args
(define (func2 op) (define x 3) (op 1 2 3 4 5.2 6))
(func2 (lambda (one two three four five six) (display five)))