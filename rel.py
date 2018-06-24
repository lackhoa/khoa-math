from misc import MyEnum


# Relation types:
# FUN: (fun inp out)
# UNION: (subs sup)


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

def iso(lr_fun, rl_fun, left, right):
    return (Rel(type_='FUN', fun=lr_fun, inp=[left], out=right),
            Rel(type_='FUN', fun=rl_fun, inp=[right], out=left))

def eq(left, right):
    iden = lambda x: x
    return iso(lr_fun=iden, rl_fun=iden, left=left, right=right)

