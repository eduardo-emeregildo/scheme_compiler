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

;fix this, its failing
(define (func) +)
(define (func2 . args) -)
(display ((func)))
(display ((func2 1 2 3 4) 4 1))


;(define (func op) (op 1 3 2))
;(func +)


; the problem is in the procedure call rule. After self.expression, you have to
; check at runtime what the value of the expression was, since operator can be any valid
; expression.
;Looks like the approach i took in param_function_call is the approach that should
;have been taken for all function calling since there's no way to know at compile
;time what the value of an expression.

; see if theres a way where i dont have to do things in the runtime, since that would
;be slower
;work on this after finishing up lambda

;but this works:
;(define func +)
;(func 1 2)


;(display ((func) 1 2))
;(define (func op) (+ 1 2))