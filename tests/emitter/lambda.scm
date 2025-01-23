;(define (func one two three four five six seven) (display seven))
;(func 1 2 3 4 5 6 7)

;(define (func one) (display 1))
;(func 1)

;((lambda (x) (display x)) 21)
;((lambda (one two three four five six seven) 
    ;(define funky 41)(display seven)) 1 2 3 4 5 6 7)
;(display ((lambda (x) (x 1 2)) +))
;((lambda (x) (define (loc op) (display op))(loc x)) 47)

;variadic:
(define (func req . args) (display args))
(func 1 2 3)
(func 2 3)
(func 3 4 5)

;(func 1 2 3 4)
;(lambda () (+ 1 2))

;(define (func op) (+ 1 2))