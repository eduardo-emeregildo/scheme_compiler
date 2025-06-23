;sum first n elements
(define (sum n)
    (if (<= n 1) 
    n
    (+ n (sum (- n 1)))))

(display (sum 10)) ;55
(display (sum 9)) ;45
(display (sum 5)) ;15
(display (sum 5.0)) ;15.0
(display (sum 1))


(define (fact n)
    (if (= n 1)
    n
    (* n (fact (- n 1)))))

(display (fact 1))
(display (fact 2))
(display (fact 3))
(display (fact 5))
(display (fact 5.0))

(define (fib n)
  (if (< n 2)
      n
      (+ (fib (- n 1)) (fib (- n 2)))))

(display (fib 10)) ; Output: 55
