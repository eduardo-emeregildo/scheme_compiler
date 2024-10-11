from environment import *
class ListNode():
    #data holds Identifier class, next holds another ListNode
    def __init__(self,data = None, next = None):
        self.data = data
        self.next = next 
        
    def set_next(self,next_node):
        self.next = next_node
    
    def car(self):
        return self.data
    
    def cdr(self):
        return self.next
    
    #for debugging purposes(only prints 1d list for now)
    def print(self):
        print(self.data.value)
        cur_node = self.next
        while cur_node is not None:
            print(cur_node.data.value)
            cur_node = cur_node.next
            
# a = ListNode(Identifier(IdentifierType.INT,"1"),None)
# b = ListNode(Identifier(IdentifierType.INT,"2"),None)
# c = ListNode(Identifier(IdentifierType.INT,"3"),None)
# d = ListNode(Identifier(IdentifierType.INT,"4"),None)
# e = ListNode(Identifier(IdentifierType.INT,"5"),None)
# a.set_next(b)
# b.set_next(c)
# c.set_next(d)
# d.set_next(e)
# a.print()
# print("car of a is: ",a.car().value)
# print("cdr is:")
# a.cdr().print()

        
    