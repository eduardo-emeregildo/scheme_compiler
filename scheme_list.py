from environment import *
class Pair():
    #Pair class used to represent pairs and lists.
    # car and cdr are both either Identifier Objects or None
    # car = None indicates empty list
    # cdr = None indicates end of list
    # if cdr has IdentifierType.PAIR, this is basically a list, since you have a nested pair here
    #A list is a pair whose cdr is also pair. This is how to check if obj is a list or pair: by checking the IdentifierType of the cdr

    def __init__(self,car = None, cdr = None):
        self.car = car
        self.cdr = cdr
        
    def set_car(self,car):
        self.car = car 
        
    def set_cdr(self,cdr):
        self.cdr = cdr
    
    def get_car(self):
        return self.car
    
    def get_car_value(self):
        if self.car is None:
            return
        return self.car.value
    
    def is_object(self,ident_type):
        return ident_type in [IdentifierType.PAIR,IdentifierType.VECTOR]
    
    def get_cdr(self):
        return self.cdr
    
    def get_cdr_value(self):
        if self.cdr is None:
            return
        return self.cdr.value
    
    def print(self):
        if self.car is None:
            print("Empty List: ()")
            return
        # print("PRINTING PAIR:")
        if self.is_object(self.car.typeof):
            self.car.value.print()
        else:
            print(self.car.value)
            
        if self.cdr is None:
            return
        if self.is_object(self.cdr.typeof):
            self.cdr.value.print()
        else:
            print(self.cdr.value)
        # print("END OF PAIR:")

# a = Pair(Identifier(IdentifierType.INT,"1"),  Identifier(IdentifierType.PAIR,Pair(Identifier(IdentifierType.INT,"2"), Identifier(IdentifierType.PAIR,Pair(Identifier(IdentifierType.INT,"3"),None)))))
# b = Pair(Identifier(IdentifierType.INT,"1"),Identifier(IdentifierType.INT,"2"))
# print("PRINTING A: '(1 2 3)")
# a.print()
# print("PRINTING B: (cons 1 2)")
# b.print()

