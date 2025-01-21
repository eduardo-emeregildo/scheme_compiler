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

;the equivalent of above cond using only if
;(define x 1)
;(if (= x 1) 
    ;(display "x is one!") 
    ;(if (= x 2) (display "x is two!") (display "x is not 1 or 2")))
;(display "after")

;and
(display "and tests:")
(display (and 1 2 3 4))
(display (and 1 2 3 #f))
(display (and 1 #f 3 4))
(display "starting...")
;should print 1,2 and then 0x0, skips 4
(display (and (display 1) (display 2) #f (display 4)))

(define x 21)
(if (and (> x 20) (< x 22)) (display "x must be 21") (display "x cant be 21"))
(define x 19)
(if (and (> x 20) (< x 22)) (display "x must be 21") (display "x cant be 21"))
(define x 22)
(if (and (> x 20) (< x 22)) (display "x must be 21") (display "x cant be 21"))
(display (and))

;or
(display "or tests:")
(display (or 1 2 3 4))
(display (or #f 2 3 4))
(display (or #f #f 3 4))
(display (or #f #f #f 4))
(define (check val) 
    (if (or (= val 10) (= val 11)) 
    (display "val is either 10 or 11") 
    (display "val is not 10 or 11")))
(check 10)
(check 11)
(check 42)
(display (or))