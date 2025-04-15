; (define (outer) 
;     (define local 7)
;     (define (inner) (+ local 1))
;     (display (inner)))
; (outer)

; ((lambda (x) 
;     (define local 7)
;     (define (bar) (+ local x))
;     (display (bar))) 1)

; (display "example with counters but with only lambdas:")
; (define (make_counter)
;     ((lambda (count) (lambda () (set! count (+ count 1)) count)) 0))

; (define c1 (make_counter))
; (define c2 (make_counter))
; (define c3 (make_counter))
; (display (c1))
; (display (c1))
; (display (c2))
; (display (c2))
; (display (c3))
; (display (c3))


(define (func arg)
  ((lambda (x y) (+ x y arg)) 1 2))

(display (func 3)) ; should print 6


; examples found in: https://piembsystech.com
(display "example 1:")
(define (make_adder x)
  (lambda (y)
    (+ x y)))

(define add5 (make_adder 5)) ; Creates a closure where x = 5
(display (add5 3)) ; Outputs 8 because it adds 5 (from closure) to 3

(display "example 2:")
(define x 10) ; Global environment

(define (outer_function a)
  (define b (+ a x)) ; Local environment of outer-function
  (lambda (c)
    (+ b c))) ; Local environment of the lambda (closure)

(define inner_function (outer_function 20)) ; b = 30
(display (inner_function 5)) ; Outputs 35 (b + c = 30 + 5)


(display "lambdas with outer,middle,inner functions:")
((lambda ()
  (define a 41)
  ((lambda ()
    ((lambda () (display (+ a 1))))))))



; (define (outer)
;     (define local 7)
;     (define (inner) ((lambda (x) (display (+ x local))) 1))
;     (inner))
; (outer)


; (define (make_counter)
;   ; bind count and create a new procedure that will (when
;   ; called) increment that binding and return its value
;   (let ((count 0))
;     (lambda ()
;       (set! count (+ count 1))
;       count)))

; (define c1 (make_counter))
; (define c2 (make_counter))
; (define c3 (make_counter))
; (display (c1))
; (display (c1))
; (display (c2))
; (display (c2))
; (display (c3))
; (display (c3))

;(display (let tmp ((a 1) (b 2) (c 3) (d 4) (e 5) (f 6) (g 7)) g))

; (let tmp ((x 1)) 
;     (define (inner) 
;         (+ x 1)) 
;     (display (inner)))


;with lets
; (define (outer)
;     (define local 7)
;     (define (inner) (let () (display (+ local 1))))
;     (inner))
; (outer)

