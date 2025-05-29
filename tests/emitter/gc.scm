;'#(1 2 3 (4 5 6)) ; wasnt freeing the inner pair. Now works!
;(display '#(1 2 3 (4 5 6))) ;works!

;(define dont_collect_me '#(4 5))
;(define loc 5.3)
;(display dont_collect_me)

;freeing closure example with lambda
; ((lambda (x) 
;     (define (local) (display x))
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

; (define (assoc val alist) 
;     (if (null? alist) #f 
;         (if (equal? val (car (car alist))) (car alist) (assoc val (cdr alist)))))

; (define (memoize f)
;   (let ((cache '()))
;     (lambda (x)
;       (let ((entry (assoc x cache)))
;         (if entry
;             (cdr entry)
;             (let ((result (f x)))
;               (set! cache (cons (cons x result) cache))
;               result))))))
; (define (slow_square x)
;   (display "Computing...")
;   (* x x))

; (define fast_square (memoize slow_square))
; ; (display (fast_square 4)) ;; Computes. Only prints computing once
; (display (assoc 'a '((a . 1) (b . 2) (c . 3))))
; (display (assoc 'b '((a . 1) (b . 2) (c . 3))))
; (display (assoc 'c '((a . 1) (b . 2) (c . 3))))

;this is a more simplified example of the problem with closures_lambda_let.
;since inner invokes the gc, it frees outer's definitions
(define (outer) 
    (define x 3.5)
    (define y 4)
    (define (inner)
        (define foo "hallo")
        (display "inner called"))
    (inner)
    (+ x y))
(display (outer))


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
;(define (func op) (define (local) (define f "hey") op) (local))
;(func 1)