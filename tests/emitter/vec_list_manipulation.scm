(display "testing append with one arg:")
(display (append 4))
(display (append '(1 2 3)))
(display (append '()))
(display (append '#(4 5 6)))

(display "testing basic appends:")
(display (append '(1 2 3) 4)) ;(1 2 3 . 4)
(display (append '(1 2 3) '(4)))
;(display (append '()  1))
;(display (append '()  '(1 2 3)))
;(display (append (cdr '(1))  45)) ; should return second arg
;(display (append (cdr '(1))  '(2 3 4))) ; should return second arg
;(display (append '(1 2 3) '(4) '(5 6 7)))
;(display(append '(1 2 3) '(4) 7)) ;should return '(1 2 3 4 . 7)
;(display (append '(1 2 3) '())) ;basically empty list is ignored
;(display (append '(1 2 3) '() '(4 5)))
;(display (append '() '(1 2 3) '(4))) ; returns '(1 2 3 4)

;(display (append '(1 2 3) '#(4 5))) ; should be dot notation

;(display (append '() 1 2)) ; error





;(define (func . op) op)
;(display (func '(1 2 3) 4 5))
; ^ returns ((1 2 3) 4 5) 