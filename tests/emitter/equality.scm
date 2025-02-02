;testing eq? eqv? equal? and =
(display "testing eq?")
(display (eq? 1 2))
(display (eq? #t #f))
(display (eq? '(1 2 3) '(1 2 3)))
(display (eq? 1 (cdr '(1 4 5 6))))
(display (eq? #t #t))
(display (eq? '() '()))
(display (eq? 1 (car '(1 4 5 6))))
(display "more complex eq? tests:")
(define x '( 2 3))
(define y '( 2 3))
(display "should be false")
(display (eq? x y))
(define y x)
(display "should be true")
(display (eq? x y))
(define a '())
(define b '())
(display "should be true")
(display (eq? a b))
(define foo 3.5)
(define bar 3.5)
(display (eq? foo bar))
(display "eq? on two lambdas:")
(display (eq? (lambda (x) (* x x)) (lambda (x) (* x x)))) ; should be f
(display "implementation specific tests:")
;first should be true, the next two should be false since there is no string 
;interning currently
(display (eq? 2 2)) 
(display (eq? "ab" "ab"))
(display (eq? '\a '\a))
(display (eq? #\a #\a))
(display (eq? 2.5 2.5))
(display (eq? #t #t))
(display (eq? 3 3.0))
;since eq? already works as intended for non ptr types, eqv? will basically
;be a copy of eq?
(display (eq? eq? eqv?))
(display "eqv? tests:")
(define (func1) (+ 1 2))
(define (func2) (+ 3 4))
(display (eqv? func1 func2))
(define func1 func2)
(display (eqv? func1 func1))
(display (func1)); should be 7
(display "equal? tests:")
;(display (equal? 'a 'a)) ; should be true
;(display (equal? "a" "a")) ; true
;(display (equal? '(1 2 3) '(1 2 3))) ; true