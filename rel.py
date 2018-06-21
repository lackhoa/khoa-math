from misc import MyEnum


# Relation types:
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
        elif self.type == 'ISO':
            return '{} <-> {}'.format(self['left'], self['right'])

def eq(left, right):
    iden = lambda x: x
    return Rel(type_='ISO', Lr_fun=iden, rL_fun=iden, left=left, right=right)

