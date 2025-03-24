;example where closure is needed:
;(define (func op) (define (local f) (+ f op))(local 3))
;(display (func 2))

; the above should print 5. The problem is when you search f in symbol table, 
; the result has the offset with respect to its current environment, 
; so when a more local function tries to retrieve it, it doesnt know the offset 
; relative to its function

;example 2: should print 3.
;(define (make_closure) (define local 3)(define (closure) (display local)) closure)
;(define closure (make_closure))
;(closure)

;example 3: same nested function closes over different values
;(define (make_closure val) (define (closure) (display val)) closure)
;(define doughnut (make_closure "doughnut"))
;(define bagel (make_closure "bagel"))
;(doughnut) ; should print doughnut
;(bagel) ; should print bagel

;example 4:
;(define (outer) 
    ;(define a 1) 
    ;(define b 2) 
    ;(define (middle) 
        ;(define c 3) 
        ;(define d 4) 
        ;(define (inner) (+ a b c d)) 
        ;(inner)) 
    ;(middle))
;(outer) ; should print out 10

;example 5 would creating a lambda within a let. The variables that let declares
;should be usable in the lambda

;example 6: showing whether closures close over variables and not values
;think I need to implement set! to be able to test this...

;it seems like Scheme closes over values, not variables. I.e. there is not "one"
;upvalue, there are copies of it.
;(define (make_adder x) (define (inner y) (+ x y)) inner) ;same as lambda below

;(define make_adder
  ;(lambda (x)
    ;(lambda (y)
      ;(+ x y))))

;(define add_5 (make_adder 5))

;(display (add_5 10)) ; Outputs 15

;(define new_x 20)
;(define add_20 (make_adder new_x))

;(display (add_20 10)) ; Outputs 30

;(set! new_x 50)
;(display (add_20 10)) ; prints 30, meaning add_20 captured new_x and set! did not
;overwrite it, so it captured it by value


;similar example to the above one, but with lists:
;(define (make_appender x) (define (inner y) (append x y)) inner)

;(define add_5 (make_appender '(5)))
;(display (add_5 '(10))) ; should print '(5 10)

;(define new_x '(20))
;(define add_20 (make_appender new_x))
;(display (add_20 '(10))) ; should print '(20 10)

;(set! new_x '(50))
;(display (add_20 '(10))) ; prints '(20 10)

;third example:
;should print:
;1
;2
;1
;2
;1
;2
;which indicates that there is not one reference of count, there are multiple

;an example with closure in let:
;(define (func x)(let ((a 1)) (+ a x)))
;(func 3) should print 4, the let is capturing x

;(define (make_counter)
  ;; bind count and create a new procedure that will (when
  ;; called) increment that binding and return its value
  ;(let ((count 0))
    ;(lambda ()
      ;(set! count (+ count 1))
      ;count)))
;(define c1 (make_counter))
;(define c2 (make_counter))
;(define c3 (make_counter))
;(display (c1))
;(display (c1))
;(display (c2))
;(display (c2))
;(display (c3))
;(display (c3))


;After recreating the example in crafting interpreters:
;(define globalSet 0)
;(define globalGet 1)
;(define (main_func)
  ;(define a "initial")
  ;(define (set) (set! a "updated"))
  ;(define (get) (display a))
  ;(set! globalSet set) (set! globalGet get))
;(main_func)
;(globalSet)
;(globalGet)
;this prints "updated" so within within main_func, there is one a.
; my guess is that set and get where defined within main_func, so refer to same
;a. 
;But in the example above this one, its not the case for c1,c2,c3

;testing that closure objects are being made/ are printable
;(define (closure) (display "works!"))
;(display closure)
;(closure)
;(define (variadic_closure arg1 . rest) (display (car rest)))
;(display variadic_closure)
;(variadic_closure 1 2 3)
;(define (lamb_closure) (lambda (x) (display x)))
;(display lamb_closure)

;closure tests with let:
;ex1:
;(define (func)
  ;(define free 5)
  ;(let named_let ((y 10))
    ;(define local 5)
    ;(display (+ local y free))(set! free (+ free 1)) named_let))
;(define glob (func))
;(glob 10); should print 20,21 and procedure


;ex2
;(define (func)
  ;(define free 5)
  ;(let named_let ((y 10))
    ;(display free)
    ;(set! free (+ free 1))
    ;(if (= y 1) (display "done") (named_let (- y 1)))))
;(func) ; should print numbers 5-14 followed by done

;testing that general function calls work after closure was introduced
;(define (add_one arg) (display (+ arg 1)))
;(define (sub_one arg) (display (- arg 1)))
;(define (change_by_one bool)(if bool add_one sub_one))
;((change_by_one #t) 3) ; should return 4
;((change_by_one #f) 3) ; should return 2
;(define (func op . args) (op args))
;(display (func car 1 2 3));should return 1
;nested function:
;(define (outer) (define (inner) 1) 2)

;upvalues tests:
;(define (func op) (define (local f) (+ f op))(local 3))
;(display (func 2))
;(define (outer) (define local 3) (define (inner) (+ 1 local)) (inner))
;(display (func))


;the function inner cant reference itself, its own closure obj must be passed.
;(define (outer) (define (inner) inner) (display (inner)))
;(outer)


;normal functions can reference themselves
;(define (func one two three) func)
;(display (func 1 2 3))
;(display func)



;testing that variadic functions can reference themselves
;(define (variadic_func one two . three) (display variadic_func)(display three))
;(variadic_func 1 2 3 4 5 6)
;(variadic_func 7 8)

;infinite
;(define (fank arg) (fank arg))
;(fank 1)

;testing that general function calls can reference themselves
;(define (add_one arg) (display (+ arg 1)))
;(define (sub_one arg) (display (- arg 1)))
;(define (change_by_one bool) (if bool add_one sub_one))
;(define (add_or_sub bool) (if bool + -))
;((change_by_one #t) 3) ; should return 4
;(display ((add_or_sub #t) 1 2))
;(display ((add_or_sub #f) 1 2))

;(+ 3 2.5)
;(display 10.37)
;2.5
;(display 2.5)
;(= 2.5 2.5)
;(display '(1 2 3))

;(define (func one) (display 3.5))
;(func 1)

;testing that builtins work after changing them to closures
;non-variadic
;(display 2)
;(display (= 3 2))
;(display (= 3 3))
;(display (cdr '(1 2 3 4 5)))
;(display (list? '(1 2)))
;(display (list? '(1 . 2)))
;;variadic
;(display "variadic tests:")
;(display (+ 1 2 3))
;(display (- 5 3))
;(display (append '(1 2) '(3 4)))
;(display (* 5 4 3 2))
;
;(display "general function calling:")
;(define (func op) (op 1 2))
;(display (func +))
;(display (func -))
;(display (func =))

;(display "tests where upvalue is located in immediately enclosing scope:")
;(define (outer) (define local 3) (define (inner) (+ 1 local)) (inner))
;(display (outer)) ; should print out 4

;naming bar inner causes problems since it overwrites inner of above definition in
;asm file. this needs to be fixed
;(define (foo) (define local1 3) (define local2 4) (define (bar) (+ local1 local2)) (bar))
;(display (foo)) ; should print out 7

;(define (func op) (define (loc f) (+ f op))(loc 3))
;(display (func 2)) ;should print out 5

(display "tests where upvalue is not in immediately enclosing scope:")
(define (outer) 
    (define local 6) 
    (define (middle) 
        (define (inner) 
            (+ local 1)) 
        (inner)) 
    (middle))


(display (outer)) ; should print out 7

;more complicated test, inner gets an upvalue from outer and from middle
;(define (outer) 
    ;(define local 6) 
    ;(define (middle) 
        ;(define mlocal 7) 
        ;(define (inner) 
            ;(+ local mlocal)) 
        ;(inner)) 
    ;(middle))