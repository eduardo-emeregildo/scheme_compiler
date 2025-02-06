;(display "testing append with one arg:")
(display (append 4))
(display (append '(1 2 3)))
(display (append '()))
(display (append '#(4 5 6)))

(display "testing basic appends:")
(display (append '(1 2 3) 4)) ;(1 2 3 . 4)
(display (append '(1 2 3) '(4)))
(display (append '()  1))
(display (append '() '() 4))
(display (append '()  '(1 2 3)))
(display (append '(1 2 3) '(4) '(5 6 7)))
(display(append '(1 2 3) '(4) 7)) ;should return '(1 2 3 4 . 7)
(display (append '(1 2 3) '())) ;basically empty list is ignored
(display (append '(1 2 3) '() '(4 5)))
(display (append '() '(1 2 3) '(4))) ; returns '(1 2 3 4)
(display (append '(1 2 3) '#(4 5))) ; should be dot notation
(display "more complicated tests:")
(display (append (cdr '(1))  45)) ; should return second arg
(display (append (cdr '(1))  '(2 3 4))) ; should return second arg

(define x '(1 2 3))
(define y (append x '(4 5 6)))
(display (eq? x y))
(display (equal? x y))
(display y)
(define x '(11 12 13))
(display y) ; both prints should match: '(1 2 3 4 5 6)


;(display "errors:")
;(display (append '() 1 2))
;(display (append '(1 2 3 . 4) 5))
;(display (append '(1 2 3 4) 5 '(1 2)))
;(display (append '(1 2 3 4) '(4 5)' 6 7))