; (define (outer) 
;     (define local 7)
;     (define (inner) (+ local 1))
;     (display (inner)))
; (outer)

; ((lambda (x) 
;     (define local 7)
;     (define (bar) (+ local x))
;     (display (bar))) 1)

; (display "example with counters but with only lambdas:")
; (define (make_counter)
;     ((lambda (count) (lambda () (set! count (+ count 1)) count)) 0))

; (define c1 (make_counter))
; (define c2 (make_counter))
; (define c3 (make_counter))
; (display (c1))
; (display (c1))
; (display (c2))
; (display (c2))
; (display (c3))
; (display (c3))


; (define (func arg)
;   ((lambda (x y) (+ x y arg)) 1 2))

; (display (func 3)) ; should print 6


; examples found in: https://piembsystech.com
; (display "example 1:")
; (define (make_adder x)
;   (lambda (y)
;     (+ x y)))

; (define add5 (make_adder 5)) ; Creates a closure where x = 5
; (display (add5 3)) ; Outputs 8 because it adds 5 (from closure) to 3

; (display "example 2:")
; (define x 10) ; Global environment

; (define (outer_function a)
;   (define b (+ a x)) ; Local environment of outer-function
;   (lambda (c)
;     (+ b c))) ; Local environment of the lambda (closure)

; (define inner_function (outer_function 20)) ; b = 30
; (display (inner_function 5)) ; Outputs 35 (b + c = 30 + 5)


; (display "lambdas with outer,middle,inner functions:")
; ((lambda ()
;   (define a 41)
;   ((lambda ()
;     ((lambda () (display (+ a 1))))))))



; (define (outer)
;     (define local 7)
;     (define (inner) ((lambda (x) (display (+ x local))) 1))
;     (inner))
; (outer)




;with lets

; (let tmp ((x 1)) 
;     (define (inner) 
;         (+ x 1)) 
;     (display (inner)))


; (define (outer)
;     (define local 7)
;     (define (inner) (let () (display (+ local 1))))
;     (inner))
; (outer)

; (define (make_counter)
;   ; bind count and create a new procedure that will (when
;   ; called) increment that binding and return its value
;   (let ((count 0))
;     (lambda ()
;       (set! count (+ count 1))
;       count)))

; (define c1 (make_counter))
; (define c2 (make_counter))
; (define c3 (make_counter))
; (display (c1))
; (display (c1))
; (display (c2))
; (display (c2))
; (display (c3))
; (display (c3))



;ex1:
; (define (func)
;   (define free 5)
;   (let named_let ((y 10))
;     (define local 5)
;     (display (+ local y free))(set! free (+ free 1)) named_let))
; (define glob (func))
; (glob 10); should print 20,21


;ex2
; (define (func)
;   (define free 5)
;   (let named_let ((y 10))
;     (display free)
;     (set! free (+ free 1))
;     (if (= y 1) (display "done") (named_let (- y 1)))))
; (func) ; should print numbers 5-14 followed by done

;ex3, another example with counters
; (define (make_counter initial)
;   (let ((count initial))
;     (lambda ()
;       (let ((v count))
;         (set! count (+ count 1))
;         v))))

; (define counter1 (make_counter 0))
; (define counter2 (make_counter 10))

; (display (counter1)) ; Output: 0
; (display (counter1)) ; Output: 1
; (display (counter2)) ; Output: 10
; (display (counter2)) ; Output: 11

;ex4
; (define (greater_than_predicate threshold)
;   (lambda (value) (> value threshold)))

; (define greater_than_5 (greater_than_predicate 5))

; (display (greater_than_5 6)) ; Output: #t
; (display (greater_than_5 3)) ; Output: #f

;::::: basic memoization example::::

;have to make assoc since I havent made it as a builtin
; alist is a list of of pairs, ex: '((a . 1) (b . 2) (c . 3))
(define (assoc val alist) 
    (if (null? alist) #f 
        (if (equal? val (car (car alist))) (car alist) (assoc val (cdr alist)))))


(define (memoize f)
  (let ((cache '()))
    (lambda (x)
      (let ((entry (assoc x cache)))
        (if entry
            (cdr entry)
            (let ((result (f x)))
              (set! cache (cons (cons x result) cache))
              result))))))

;; Usage
(define (slow_square x)
  (display "Computing...")
  (* x x))

(define fast_square (memoize slow_square))
(display (fast_square 4)) ;; Computes. Only prints computing once
(display (fast_square 4)) ;; Uses cache, doesnt print computing
(display (fast_square 5)) ;; Computes. Only prints computing once
(display (fast_square 5)) ;; Uses cache, doesnt print computing