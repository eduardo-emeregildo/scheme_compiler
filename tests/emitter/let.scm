(display (let ((a 1) (b 2) (c 3) (d 4) (e 5) (f 6) (g 7)) g))

;answer should be 13
(define glob 1)
(display (let ((x 5) (y 7)) (+ x y glob)))

;with this syntax, basically giving the function a temporary name
;fix this, currently not working
;(display (let x ((y 10)) x))

;check that default value 10 is overriden by 1
;(define func (let x ((y 10)) (display y)x))
;(func 1)