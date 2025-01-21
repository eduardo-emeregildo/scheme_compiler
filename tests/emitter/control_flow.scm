;if statements
;(display (if #t 1 2))
;(define (func op) (if #t (op 1 2 (op 3 4)) (op 3 4 (op 5 6))))
;(display (func +))

;recursion: should just print infinite 1's until stack runs out of memory
;(define (func1 op) (func1 (display 1)))
;(func1 #t)

;cond
;(define (cond_test x) 
    ;(cond ((= x 1) (display "x is one")) 
    ;((= x 2) (display "x is two"))))

;(define x 3)
;(cond ((= x 1) (display "main: x is one")) 
    ;((= x 2) (display "main: x is two")) (else (display "main: x is not one or two")))
;(cond_test 3)

;(cond (else (display "just an else!")))
;(display "After :D")

;and
(display "and tests:")
(display (and 1 2 3 4))
(display (and 1 2 3 #f))
(define x 21)
(if (and (> x 20) (< x 22)) (display "x must be 21") (display "x cant be 21"))
(define x 19)
(if (and (> x 20) (< x 22)) (display "x must be 21") (display "x cant be 21"))
(define x 22)
(if (and (> x 20) (< x 22)) (display "x must be 21") (display "x cant be 21"))
(display (and))

;the equivalent of above cond using only if
;(define x 1)
;(if (= x 1) 
    ;(display "x is one!") 
    ;(if (= x 2) (display "x is two!") (display "x is not 1 or 2")))
;(display "after")