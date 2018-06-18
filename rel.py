from misc import MyEnum
from enum import auto


class RelT(MyEnum):
    """Each relation's value is its arity"""
    EQ = auto()
    FUN = auto()  # (func input1 ... input_k output)
    UNION = auto()  # (subset_1 ... subset_k union)
    ISO = auto()  # (left_right_fun, right_left_fun, left, right)


class Rel:
    def __init__(self, type_: RelT, *slots):
        self.type = type_
        self.slots = slots

    def __repr__(self) -> str:
        if self.type == RelT.FUN:
            return '{} -> {}'.format(' '.join(self.get('in')), self.get('out'))
        elif self.type == RelT.UNION:
            return '(U {}) = {}'.format(' '.join(self.get('subs')), self.get('uni'))
        if self.type == RelT.ISO:
            return '{} <-> {}'.format(self.get('left'), self.get('right'))

    def get(self, key: str):
        if self.type == RelT.FUN:
            if key == 'fun': return self.slots[0]
            elif key == 'in': return self.slots[1:-1]
            elif key == 'out': return self.slots[-1]
        elif self.type == RelT.UNION:
            if key == 'subs': return self.slots[:-1]
            if key == 'uni': return self.slots[-1]
        elif self.type == RelT.ISO:
            if key == 'Lr_fun': return self.slots[0]
            if key == 'rL_fun': return self.slots[1]
            if key == 'left': return self.slots[2]
            if key == 'right': return self.slots[3]
