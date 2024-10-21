from environment import *
class Pair():
    #Pair class used to represent pairs and lists.
    # car and cdr are both either Identifier Objects or None
    # car = None indicates empty list as car elt
    # cdr = None indicates end of list
    #The EMPTY LIST is indicated when both card and cdr are None
    # if cdr has IdentifierType.PAIR, this is basically a list, since you have a nested pair here
    #A list is a pair whose cdr is also pair. This is how to check if obj is a list or pair: by checking the IdentifierType of the cdr

    def __init__(self,car = None, cdr = None):
        self.car = car
        self.cdr = cdr
        
    def set_car(self,car):
        self.car = car 
        
    def set_cdr(self,cdr):
        self.cdr = cdr
        
    def is_empty_list(self):
        return self.car is None and self.cdr is None
    
    def get_car(self):
        return self.car
    
    def get_car_value(self):
        if self.car is None:
            return
        return self.car.value
    
    def is_pair(self,ident_type):
        return ident_type == IdentifierType.PAIR
    
    def get_cdr(self):
        return self.cdr
    
    def get_cdr_value(self):
        if self.cdr is None:
            return
        return self.cdr.value
    
    def print(self):
        if self.car is None and self.cdr is None:
            print("This is an empty list")
            return
        if self.car is None:
            print("The car of the pair is empty list: ()")
        # print("PRINTING PAIR:")
        elif self.is_pair(self.car.typeof):
            self.car.value.print()
        else:
            print(self.car.value)
            
        if self.cdr is None:
            return
        if self.is_pair(self.cdr.typeof):
            self.cdr.value.print()
        else:
            print(self.cdr.value)
        # print("END OF PAIR:")

# a = Pair(Identifier(IdentifierType.INT,"1"),  Identifier(IdentifierType.PAIR,Pair(Identifier(IdentifierType.INT,"2"), Identifier(IdentifierType.PAIR,Pair(Identifier(IdentifierType.INT,"3"),None)))))
# b = Pair(Identifier(IdentifierType.INT,"1"),Identifier(IdentifierType.INT,"2"))
# print("PRINTING A: '(1 2 3)")
# a.print()
# a_ident_obj = Identifier(IdentifierType.PAIR,a)
# b_ident_obj = Identifier(IdentifierType.PAIR,b)
# print("length of a in bytes is: ",a_ident_obj.get_size())
# print("PRINTING B: (cons 1 2)")
# b.print()
# print("length of b in bytes is: ",b_ident_obj.get_size())
# c = Identifier(IdentifierType.VECTOR,[Identifier(IdentifierType.INT,"1"),Identifier(IdentifierType.STR,'"yes"'),Identifier(IdentifierType.BOOLEAN,"#f")])
# print("getting size of vector c. Should be 13. Is: ", c.get_size())