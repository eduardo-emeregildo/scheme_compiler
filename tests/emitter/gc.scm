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

(define (make_counter)
  ; bind count and create a new procedure that will (when
  ; called) increment that binding and return its value
  (let ((count 0))
    (lambda ()
      (set! count (+ count 1))
      count)))
(define c1 (make_counter))
(define c2 (make_counter))
(define c3 (make_counter))
(display (c1))
(display (c1))
(display (c2))
(display (c2))
(display (c3))
(display (c3))

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