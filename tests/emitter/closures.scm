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
(define (outer) (define (inner) inner) (display (inner)))
(outer)


;(define (func one two three) one)
;(func 1 2 3)

;after i fix the above, work on upvalues and making the below, and tests work:
;(define (outer) (define local 3) (define (inner) (+ 1 local)) (inner))
;(outer) ; should print out 4