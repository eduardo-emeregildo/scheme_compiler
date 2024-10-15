from environment import *
class ListNode():
    #data holds Identifier class, next holds another ListNode or None to denote end of list. Third option of next is a Pair object, if you make a list with the . notation
    # For lists it will store a ListNode as value field in data Identifier Obj
    #For empty list, data and next are None
    def __init__(self,data = None, next = None):
        self.data = data
        self.next = next
        
        
    def set_data(self,data):
        self.data = data 
        
    def set_next(self,next_node):
        self.next = next_node
    
    def get_car(self):
        return self.data
    
    def get_cdr(self):
        return self.next
    
    def print(self):
        if self.data is None:
            print("Empty List: ()")
            return
        print("PRINTING LIST:")
        cur_node = self
        while cur_node is not None:
            if cur_node.data.typeof == IdentifierType.LIST:
                cur_node.data.value.print()
            else: 
                print(cur_node.data.value)
            
            if isinstance(cur_node.next,Pair):
                cur_node.next.print()
                break
            cur_node = cur_node.next
        print("END OF LIST")

#Both and cdr are Identifier objects. One important fact is that a pair whose cdr is a list is a list.(Ex: (cons 1 '(2 3 4)) results in a list )
#car and cdr could be lists,vectors or pairs
class Pair():
    def __init__(self,car=None,cdr=None):
        self.car = car
        self.cdr = cdr
    
    def set_car(self,car):
        self.car = car
        
    def set_cdr(self,cdr):
        self.cdr = cdr
    
    def get_car(self):
        return self.car
    
    def get_cdr(self):
        return self.cdr
    
    def is_object(self,identifier):
        return identifier in [IdentifierType.LIST,IdentifierType.PAIR,IdentifierType.VECTOR]

   
    def print(self):
        print("PRINTING PAIR:")
        if self.is_object(self.car.typeof):
            self.car.value.print()
        else:
            print(self.car.value)
        print(".")  
        if self.is_object(self.cdr.typeof):
            self.cdr.value.print()
        else:
            print(self.cdr.value)
        print("END OF PAIR:")
        
    
    
            
# a = ListNode(Identifier(IdentifierType.INT,"1"),None)
# b = ListNode(Identifier(IdentifierType.INT,"2"),None)
# c = ListNode(Identifier(IdentifierType.INT,"3"),None)
# d = ListNode(Identifier(IdentifierType.INT,"4"),None)
# e = ListNode(Identifier(IdentifierType.INT,"5"),None)

# f = ListNode(Identifier(IdentifierType.INT,"7"),None)
# g = ListNode(Identifier(IdentifierType.INT,"21"),None)
# f.set_next(g)
# inside_list = ListNode(Identifier(IdentifierType.LIST,f),None)

# a.set_next(b)
# b.set_next(c)
# c.set_next(inside_list)
# inside_list.set_next(d)
# d.set_next(e)
# # e.set_next(inside_list)
# a.print()
# # print("car of a is: ",a.get_car().value)
# # print("cdr is:")
# # a.get_cdr().print()

# pair = Pair(Identifier(IdentifierType.INT,"1"),Identifier(IdentifierType.LIST,f))
# pair.print()    