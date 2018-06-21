from misc import MyEnum


# Relation types:
# EQ: (left right)
# FUN: (fun inp out)
# UNION: (subs sup)
# ISO: (Lr_fun, rL_fun, left, right)


class Rel(dict):
    def __init__(self, type_: str, **kwargs):
        self.type = type_
        super().__init__(**kwargs)

    def __repr__(self) -> str:
        if self.type == 'FUN':
            return '{} -> {}'.format(' '.join(self['inp']), self['out'])
        elif self.type == 'UNION':
            return '(U {}) = {}'.format(' '.join(self['subs']), self['sup'])
        if self.type == 'ISO':
            return '{} <-> {}'.format(self['left'], self['right'])
