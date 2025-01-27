;(define (func one two three four five six seven) (display seven))
;(func 1 2 3 4 5 6 7)

;(define (func one) (display 1))
;(func 1)

;((lambda (x) (display x)) 21)
;((lambda (one two three four five six seven) 
    ;(define funky 41)(display seven)) 1 2 3 4 5 6 7)
;(display ((lambda (x) (x 1 2)) +))
;((lambda (x) (define (loc op) (display op))(loc x)) 47)

;variadic lambda 
;((lambda (x . args) (display args)) 5 6 7 8)
;((lambda (x . args) (define tmp 45)(display args)) 71 72 73)
;((lambda (x . args) (define tmp 45)(display args)) 71)

;rest arg lambda
;((lambda x (display x)) 1 2 3 4 5)
;((lambda x (display x)))
;(display ((lambda x (cdr x)) 45 46 47))