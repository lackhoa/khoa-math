from misc import MyEnum
from enum import auto


# Relation types:
# EQ: (left right)
# FUN: (fun inp out)
# UNION: (subs uni)
# ISO: (Lr_fun, rL_fun, left, right)


class Rel(dict):
    def __init__(self, type_: str, **kwargs):
        self.type = type_
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        if self.type == 'FUN':
            return '{} -> {}'.format(' '.join(self['inp']), self['out'])
        elif self.type == 'UNION':
            return '(U {}) = {}'.format(' '.join(self['subs']), self['uni'])
        if self.type == 'ISO':
            return '{} <-> {}'.format(self['left'], self['right'])
