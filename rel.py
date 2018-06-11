from misc import MyEnum
from enum import auto


class RelT(MyEnum):
    """Each relation's value is its arity"""
    EQ = auto()
    FUN = auto()  # (func input1 ... input_k output)
    UNION = auto()  # (subset_1 ... subset_k union)


class Rel:
    def __init__(self, type_: RelT, *slots):
        self.type = type_
        self.slots = slots
    
    def get(self, attr: str):
        if self.type == RelT.FUN:
            if attr == 'fun': return self.slots[0]
            elif attr == 'in': return self.slots[1:-1]
            elif attr == 'out': return self.slots[-1]
