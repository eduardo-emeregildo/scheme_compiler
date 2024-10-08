from enum import Enum
class IdentifierType(Enum):
    CHAR = 0
    STR = 1
    INT = 2
    FLOAT = 3
    BOOLEAN = 4
    LIST = 5
    VECTOR = 6
    FUNCTION = 7

class Identifier:
    def __init__(self,typeof,value):
        self.typeof = typeof
        self.value = value
    
    def update(self,new_type,new_value):
        self.typeof = new_type
        self.value = new_value

        



