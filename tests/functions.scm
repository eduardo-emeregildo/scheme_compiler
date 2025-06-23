(define (one_arg x y) (define (inner z) 8) (inner 1))
(display (one_arg 1 2))

(define new_display display)
(new_display 27)

(display "testing calling function which was passed:")
(define (func op num) (op num))
(func display 3)
(display (func null? 3))
;example of a definition using more than one arg as a function: works!
(define (func2 op1 op2) (op1 (op2 3)))
(func2 display -)

(display "variadic functions:")
(define (variadic_func  foo . args) (foo args))
(variadic_func display 1 2 '(3 4) display +)
(define (add a b) b) ; "add" is lexed as a builtin
(display (+ 1 2))
(display add)
(display +)
(display (+ 1 2 3 4 5 6 7 8 9))
(display (+ 3.5 4))
(define x 3)
(display (+ x 1))