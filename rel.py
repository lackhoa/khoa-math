from misc import MyEnum
from enum import auto


# Relation types:
# EQ: (left right)
# FUN: (func input1 ... input_k output)
# UNION: (subset_1 ... subset_k union)
# ISO: (left_right_fun, right_left_fun, left, right)


class Rel:
    def __init__(self, type_: str, *slots):
        self.type = type_
        self.slots = slots

    def __repr__(self) -> str:
        if self.type == 'FUN':
            return '{} -> {}'.format(' '.join(self.get('in')), self.get('out'))
        elif self.type == 'UNION':
            return '(U {}) = {}'.format(' '.join(self.get('subs')), self.get('uni'))
        if self.type == 'ISO':
            return '{} <-> {}'.format(self.get('left'), self.get('right'))

    def get(self, key: str):
        if self.type == 'FUN':
            if key == 'fun': return self.slots[0]
            elif key == 'in': return self.slots[1:-1]
            elif key == 'out': return self.slots[-1]
        elif self.type == 'UNION':
            if key == 'subs': return self.slots[:-1]
            if key == 'uni': return self.slots[-1]
        elif self.type == 'ISO':
            if key == 'Lr_fun': return self.slots[0]
            if key == 'rL_fun': return self.slots[1]
            if key == 'left': return self.slots[2]
            if key == 'right': return self.slots[3]
