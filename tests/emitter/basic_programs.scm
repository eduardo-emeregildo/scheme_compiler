;sum first n elements, n >= 1
(define (sum n)
    (if (= n 1) 
    1
    (+ n (sum (- n 1)))))

(display (sum 10)) ;55
(display (sum 9)) ;45
(display (sum 5)) ;15
(display (sum 5.0)) ;15.0