(+ 3 4 5 6)
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
(display (fast_square 5)) ;; Uses cache, doesnt print 