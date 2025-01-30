(display "plain lambda tests:")
((lambda (x) (display x)) 21)

((lambda (one two three four five six seven) 
    (define funky 41)(display seven)) 1 2 3 4 5 6 7)
(display ((lambda (x) (x 1 2)) +))
((lambda (x) (define (loc op) (display op))(loc x)) 47)

(display "variadic lambda tests:")
((lambda (x . args) (display args)) 5 6 7 8)
((lambda (x . args) (define tmp 45)(display args)) 71 72 73)
((lambda (x . args) (define tmp 45)(display args)) 71)

(display "lambda with rest arg tests:")
((lambda x (display x)) 1 2 3 4 5)
((lambda x (display x)))
(display ((lambda x (cdr x)) 45 46 47))

;checking that user cant make a function of the name LA followed by a number
;(define (LA1) (display "hallooo"))
