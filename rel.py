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

    def __repr__(self) -> str:
        if self.type == RelT.FUN:
            return '{} -> {}'.format(self.get('in'), self.get('out'))
        elif self.type == RelT.UNION:
            return '(UNION {}) = {}'.format(self.get('subs'), self.get('uni'))

    def get(self, key: str):
        if self.type == RelT.FUN:
            if key == 'fun': return self.slots[0]
            elif key == 'in': return self.slots[1:-1]
            elif key == 'out': return self.slots[-1]
        elif self.type == RelT.UNION:
            if key == 'subs': return self.slots[:-1]
            if key == 'uni': return self.slots[-1]
