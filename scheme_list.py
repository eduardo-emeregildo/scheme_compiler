from environment import *
class ListNode():
    #data holds Identifier class, next holds another ListNode or None to denote end of list
    # For lists it will store a ListNode as value field in data Identifier Obj
    #For empty list, data and next are None
    def __init__(self,data = None, next = None):
        self.data = data
        self.next = next
        
        
    def set_data(self,data):
        self.data = data 
        
    def set_next(self,next_node):
        self.next = next_node
    
    def car(self):
        return self.data
    
    def cdr(self):
        return self.next
    
    #for debugging purposes(only prints 1d list for now)
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
            cur_node = cur_node.next
        print("END OF LIST")
            
a = ListNode(Identifier(IdentifierType.INT,"1"),None)
b = ListNode(Identifier(IdentifierType.INT,"2"),None)
c = ListNode(Identifier(IdentifierType.INT,"3"),None)
d = ListNode(Identifier(IdentifierType.INT,"4"),None)
e = ListNode(Identifier(IdentifierType.INT,"5"),None)

f = ListNode(Identifier(IdentifierType.INT,"7"),None)
g = ListNode(Identifier(IdentifierType.INT,"21"),None)
f.set_next(g)
inside_list = ListNode(Identifier(IdentifierType.LIST,f),None)

a.set_next(b)
b.set_next(c)
c.set_next(inside_list)
inside_list.set_next(d)
d.set_next(e)
# e.set_next(inside_list)
a.print()
# print("car of a is: ",a.car().value)
# print("cdr is:")
# a.cdr().print()

        
    