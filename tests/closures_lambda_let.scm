(display "lambda examples:")
((lambda (x) 
    (define local 7)
    (define (bar) (+ local x))
    (display (bar))) 1)

(define (func arg)
  ((lambda (x y) (+ x y arg)) 1 2))
(display (func 3)) ; should print 6

(define (greater_than_predicate threshold)
  (lambda (value) (> value threshold)))
(define greater_than_5 (greater_than_predicate 5))
(display (greater_than_5 6)) ; Output: #t
(display (greater_than_5 3)) ; Output: #f


;nested lambdas
((lambda ()
  (define a 41)
  ((lambda ()
    ((lambda () (display (+ a 1)))))))) ; print 42


(display "example with counters but with only lambdas:")
(define (make_counter)
    ((lambda (count) (lambda () (set! count (+ count 1)) count)) 0))

(define c1 (make_counter))
(define c2 (make_counter))
(define c3 (make_counter))
(display (c1))
(display (c1))
(display (c2))
(display (c2))
(display (c3))
(display (c3))
(display (c3))

(display "let examples:")
(let tmp ((x 1)) 
    (define (inner_let_ex) 
        (+ x 1)) 
    (display (inner_let_ex))) ;should print 2

(define (func1)
  (define free 5)
  (let named_let ((y 10))
    (define local 5)
    (display (+ local y free))(set! free (+ free 1)) named_let))
(define glob (func1))
(glob 10); should print 20,21

(define (func2)
  (define free 5)
  (let named_let1 ((y 10))
    (display free)
    (set! free (+ free 1))
    (if (= y 1) (display "done") (named_let1 (- y 1)))))
(func2) ; should print numbers 5-14 followed by done

;::::: basic memoization example::::
;have to make assoc since I havent made it as a builtin
; alist is a list of of pairs, ex: '((a . 1) (b . 2) (c . 3))
(display "example that uses memoization:")
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