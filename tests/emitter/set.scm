; (display "using set! on globals, should print 5,4:")
; (define x 5)
; (display x)
; (set! x 4)
; (display x)


; (display "using set! on a captured variable,should print 3,4,4,4:")
; (define (outer)
;   (define loc 3)
;   (define (inner)
;     (display loc)
;     (set! loc 4)
;     (display loc))
;   inner)
; (define yeo (outer))
; (yeo)
; (yeo)


;same as example below, but with lambdas/lets
; (define (make_counter)
;   ; bind count and create a new procedure that will (when
;   ; called) increment that binding and return its value
;   (let ((count 0))
;     (lambda ()
;       (set! count (+ count 1))
;       count)))

;here c1,c2,c3 are 3 independent counters, meaning they each captured their own count
; (display "testing encapsulation, should print 1\n2\n1\n2\n1\n2:")
; (define (make_counter)
;     (define count 0)
;     (define (add1) (set! count (+ count 1)) count)
;     add1)
; (define c1 (make_counter))
; (define c2 (make_counter))
; (define c3 (make_counter))
; (display (c1))
; (display (c1))
; (display (c2))
; (display (c2))
; (display (c3))
; (display (c3))


;here both setter and getter should refer to the same a, this is why its failing
;setter and getter have their own a.

;what I realized is that during the execution of main_func, the variable a is captured,
;i.e. there is only one a. Even if say main_func sets a to something else, calling setter
; should reflect this change.
; (display "example from crafting interpreters, should print updated:")
; (define globalSet 0)
; (define globalGet 1)
; (define (main_func)
;   (define a "initial")
;   (define (setter) (set! a "updated"))
;   (define (getter) (display a))
;   (set! globalSet setter) (set! globalGet getter))
; (main_func)
;(globalSet)
;(globalGet)

; (define (outer) 
; (define x "outside")
; (define (inner) (display x))
; (inner))
; (outer)

;example in 25.4:
; (define (outer) 
; (define x "outside")
; (define (inner) (display x))
; inner)
; (define close (outer))
; (close)

;some more interesting stuff:
;this still prints out initial, because in inner, its referencing its arg.
;this means that in this case, must pass a copy. this can be solved by making args
;pass by value in all cases.

; (define globalSet 0)
; (define globalGet 1)
; (define (main_func a)
;   ;(define a "initial")
;   (define (setter) (set! a "updated"))
;   (define (getter) (display a))
;   (define (inner op) (set! op "inner!!"))
;   (set! globalSet setter) (set! globalGet getter) (inner a) (display a))
; (main_func "initial")

; pass by value test, addresses should be different
(define (x) (+ 1 2))
(define (func op) (display op))
(display x)
(func x)
;(func 1)

;should print out initial, rn its working, but for the wrong reasons. Since set!
;creates a new obj and returns it, it works. Once I change set!, test this again
; (define outer "initial")
; (define (func op) (set! op 3))
; (func outer)
; (display outer)