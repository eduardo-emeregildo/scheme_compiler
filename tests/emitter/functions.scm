;(define (func) 5)
;(define (one x y z) (define (two y) y)(define f 5) two)
;(define (monkey a b c d e f g) g)

;(define (one_arg x y) (define (inner z) 8) (inner 1))
;(display (one_arg 1 2))

;(define (outer) (define (middle) (define (inner) 2)(inner)) (inner))
;(outer) ;should throw error, inner was defined inside on in outer's scope

;(define monkey 21)
;(define (one_arg x) (define f "hey") func)
;(define (my_func one two three four five six seven eight) (define f 7)eight)
;(define yeo '(1 . 2))
;(define (my_func1 x) '(1 2 3 4))
;(define (my_func x) '#((1 2) 3 #f "yarr" x (3 4)))
;(define (func one two three four five six seven . args) args)
;(func)

;(define (monkey x y) x)
;(define (func one two three four five six seven eight) eight)
;(func 1 2 3 4 5 6 7 8)


;(define (yeo x) (display x))
;(yeo 21)
;(yeo '(1 2 3 4 5))
;(yeo '(1 2 #(3 4)))
;(display '(1 2 3))
;(display '#())
;(display '())
;(display #t)
;(define new_display display)
;(new_display 27)
;(display '(1))
;(display '( () 1 2))
;(display '( ()))
;(define (yeo x) x)

;(define (func op num) (op num))
;(func display 3)
;(define (func one two) two)
;(display (func 1 2))
;(define (func one two three four) four)
;(display (func 1 2 3 4))
;(define (func x)  (define (op y) (display y))(op x))
;(func 4)

;(define (yeo one two three four five six seven eight) 
        ;(define x 21)
        ;(display eight))
;(define (func op) (op 1 2 3 4 5 6 7 '(41 #f 2 3)))
;(func yeo)

;(define (yes a) '(1 2 3))
;(define (func op) (yes 3))
;(display (func 1) )

;(define (func op) op)

;(define (func op) (op 1 2))
;(func display) ; should give error, works!

;testing general_function_call
;(define (func) +)
;(define (func2 one . args) -)
;(display ((func) 1 2))
;(display ((func2 1) 4 1))

;example of a definition using more than one arg as a function: works!
;(define (func op1 op2) (op1 (op2 3)))
;(define (arg2 val) 4)
;(func display arg2)

;Also, stuff like this should work: works!
;(define (func1 op) (op (op 2)))
;(func1 display)

; Another more complex variation of the above is:
;(define (func2 op) (op 1 2 (op 3 4) (op 5 6)))
;(display (func2 +))

;variadic functions:
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

;(define (yeo arg1 arg2 arg3 ) (+ arg1 arg2 arg3 7))
;(display (yeo 1 2 3))

;make this work next:
;(define (yeo arg1 arg2 arg3) (arg1 arg2 arg3))
;(yeo + 2 3)
;(define (func op) (op 1))
;(func '#(1 2 3 4 #t))
;(display (func 1))
;(func display)
;(func +)
;test area
;(define (func arg1 arg2) arg2)
;(func 1 2)
;(display (func 7 8))

;(define (test one two three four five six . seven) (display seven))
;(define (func op ) (define (local yeo) (+ yeo 1))(op 1 2 3 4 5 6 7 8 (local 8)))
;(func test)
;(display (func +))
;(test 1 2 3 4 5 6 7 8 9 '(1 2))
;(define aaa "hello")

;a variation of this
;(define (func op) (define (local f) (display op))(local 3))
;(func "outer")