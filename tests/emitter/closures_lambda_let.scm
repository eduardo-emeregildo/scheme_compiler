; (define (outer) 
;     (define local 7)
;     (define (inner) (+ local 1))
;     (display (inner)))
; (outer)

; ((lambda (x) 
;     (define local 7)
;     (define (bar) (+ local x))
;     (display (bar))) 1)

(display "example with counters but with only lambdas:")
(define (make_counter)
    ((lambda (count) (lambda () (set! count (+ count 1)) count)) 0))

(define c1 (make_counter))
(define c2 (make_counter))
(define c3 (make_counter))
(display (c1))
(display (c1))
(display (c2))
(display (c2))
(display (c3))
(display (c3))



;fix this. problem is inner isnt adding upvalue to lambda function
;this is because inner's body has a lambda and its not correctly handling this case
;what i can maybe do is while the lambda object is being made, add the upvalue there,
;because its the parent whose making the lambda

;thinking of adding a anonymous_requests dictionary for upvalue tracker, which 
; functions the same as upvalue_requests except its for anonymous functions i.e.
;lambdas and lets. 

;This is so that in lambda expression when searching for requests,
;you dont have to iterate every single request, just the anonymous ones.
;this means that when adding a request, must be added to the correct dictionary
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

