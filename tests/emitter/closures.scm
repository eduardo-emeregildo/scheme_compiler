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