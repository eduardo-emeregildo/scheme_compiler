(display (let ((a 1) (b 2) (c 3) (d 4) (e 5) (f 6) (g 7)) g))

;answer should be 13
(define glob 1)
(display (let ((x 5) (y 7)) (+ x y glob)))

;with this syntax, basically giving the function a temporary name
(display (let named_let ((y 10))  (define local 5) named_let))

;should print 5 forever
;(display (let infinite ((y 10))  (display y) (infinite 5)))

;check that default value 10 is overriden by 1
(define func (let x ((y 10)) (display y) x))
(func 1)

;checking that let with name doesnt conflict with other definitions
(define (hallo) (display "global hallo"))
(hallo)
(let hallo ((x 10)) (display x))

;using let inside body of a define
(define (ffgg) (let local_let((x 10) (y 20)) (+ x y)))
(display (ffgg))

;complicated let, should print 120
(display (let fact ((n 5)) (if (= n 1)
    n
    (* n (fact (- n 1))))))