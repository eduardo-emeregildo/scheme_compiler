; '#(1 2 3 (4 5 6)) ; wasnt freeing the inner pair. Now works!
; (display '#(1 2 3 (4 5 6))) ;works!

;(define dont_collect_me '#(4 5))
;(define loc 5.3)
;(display dont_collect_me)

;freeing closure example with lambda
; ((lambda (x) 
;     (define (local) (define foo "test")(display x))
;     (local)) 5)
; (define malecon "hello :D")

;closure with upvalues is a global, so dont free upvalues. works!
; (define (outer x)
;     (define (inner) (display x))
;     (inner))
; (outer 5)
; (define malecon "hello")

;(display (- 1))
;(display (- 2))
; (display (- 5 3 4))
; (display (- 5 3.0 4))

;test to see if general_function_call marks args that are processed so they dont get collected:
; (define (adder one two) (+ one two))
; (define (func op) (display (op 2.3 4)))
; (func adder)

;scratch
; (define foo "foo")
; (define (bar one two . three)
;     (define local "bar")
;     (define local2 "aaa")
;     (define (loc_fun) 3)
;     three)
; (display (bar 1 2 3))
;scratch end

;to test normal function calls after pushing args to live_locals
; (define (foo first second) first)
; (display (foo 1.1 2))

; (define (foo first second) (= first second))
; (display (foo 1.1 2))

;to test variadic function calls after pushing args to live_locals
; (define (foo first second) (+ first second))
; (display (foo 1.1 2))


;to test general function calls after pushing args to live_locals
; (define (foo op arg) (op arg 1))
; (display (foo + 1.1))
; (display (foo eq? '(1 2 3 4 5 6)))


;below is a more simplified example of the problem with closures_lambda_let.
;since inner invokes the gc, it frees outer's definitions
; (define (outer) 
;     (define x 3.5)
;     (define y 4)
;     (define (inner)
;         (define foo "hallo")
;         (display "inner called"))
;     (inner)
;     (+ x y))
; (display (outer))

;once you replace args_for_function with using the live_locals stack use the 
;example below to test. works!
; (define (one)
;     (define h "in one")
;     5.3)

; (define (two arg1 arg2 arg3) (+ arg1 arg2 arg3))
; (display (two 1.1 (one) 3))

(display (let ((a 1) (b 2) (c 3) (d 4) (e 5) (f 6) (g 7)) g))

;lambda test
; (define glob 1)
; (display (let ((x 5) (y 7)) (+ x y glob)))

; ((lambda (x) 
;     (define (local) (+ x 1))
;     (local)) 5)
; (define malecon "hello :D")

;freeing closure with define
; (define (outer) 
;     (define loc 7)
;     (define (inner) loc)
;     (inner))
; (outer)
; (define malecon "hello :D")


;(define y "omg")
;(define z "hard")
;(define foo "yar")
;(define f 5)
;(define g 6)

; (define glob 4.3)
; (define (func x y z) (define local 1.3) (define foo "foo") z)
; (func "oh" "my" "god")

; (define (foo) 
;     (define c "loc")
;     (+ 1 2))
; (foo)

;closure example
; (define (func op) (define (local) (define f "hey") op) (local))
; display (func 1)