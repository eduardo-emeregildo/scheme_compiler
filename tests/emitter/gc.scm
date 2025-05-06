;(define malecon "hello :D")
;(define y "omg")
;(define z "soul drain")
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
(define (func op) (define (local) (define f "hey") op) (local))
(func 1)