(display "basic closure example:")
(define (make_closure) (define local 3)(define (closure) (display local)) closure)
(define closure (make_closure))
(closure) ; should print 3

(display "closing over different values:")
(define (make_closure1 val) (define (closure1) (display val)) closure1)
(define doughnut (make_closure1 "doughnut"))
(define bagel (make_closure1 "bagel"))
(doughnut) ; should print doughnut
(bagel) ; should print bagel

(display "nested closures, should print 10:")
(define (outer) 
    (define a 1) 
    (define b 2) 
    (define (middle) 
        (define c 3) 
        (define d 4) 
        (define (inner) (+ a b c d)) 
        (inner)) 
    (middle))
(display (outer)) ; should print out 10

(display "testing resizing of upvalues:")
(define (outer5) 
    (define a 1)
    (define b 2)
    (define c 3)
    (define d 4)
    (define e 5)
    (define f 6)
    (define g 7)
    (define h 8)
    (define i 9)
    (define (inner5) (+ a b c d e f g h i))
    (inner5))
(display (outer5)) ; should resize twice


(display "testing that compiler closes over values, not variables:")
(define (make_adder x) (define (inner3 y) (+ x y)) inner3) ;same as lambda below

(define add_5 (make_adder 5))
(display (add_5 10)) ; Outputs 15
(define new_x 20)
(define add_20 (make_adder new_x))
(display (add_20 10)) ; Outputs 30
(set! new_x 50)
(display (add_20 10)) ; prints 30, meaning add_20 captured new_x and set! did not
;overwrite it, so it captured it by value


;similar example to the above one, but with lists:
(define (make_appender x) (define (inner4 y) (append x y)) inner4)

(define add_5_lst (make_appender '(5)))
(display (add_5_lst '(10))) ; should print '(5 10)

(define new_x_lst '(20))
(define add_20_lst (make_appender new_x_lst))
(display (add_20_lst '(10))) ; should print '(20 10)

(set! new_x_lst '(50))
(display (add_20_lst '(10))) ; prints '(20 10)

(display "tests where upvalue is not in immediately enclosing scope:")
(define (outer1) 
    (define local 7) 
    (define (middle1) 
        (define (inner1) 
            (+ local 1)) 
        (inner1)) 
    (middle1))
(display (outer1)) ; should print out 8

;more complicated test, inner gets an upvalue from outer and from middle
(define (outer2) 
    (define local 6) 
    (define (middle2) 
        (define mlocal 7) 
        (define (inner2) 
            (+ local mlocal)) 
        (inner2)) 
    (middle2))
(display (outer2)) ; should print out 13