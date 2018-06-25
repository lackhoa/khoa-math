from misc import MyEnum
from typing import *
from khoa_math import wr, only


# Basic relation types:
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


def funo(fun, inp, out):
    return Rel(type_='FUN', fun=fun, inp=inp, out=out)


def iso(lr_fun, rl_fun, left, right):
    return (funo(fun=lr_fun, inp=[left], out=right),
            funo(fun=rl_fun, inp=[right], out=left))


def eq(left, right):
    iden = lambda x: x
    return iso(lr_fun=iden, rl_fun=iden, left=left, right=right)


def adapter(fun: Callable):
    """
    E.g: if f(a) = b then adapter(f)(KSet({a})) = KSet({b})
    """
    return lambda *args: wr(fun(*map(lambda s: only(s), args)))


def kfun(fun, inp, out):
    return funo(fun=adapter(fun), inp=inp, out=out)


def kiso(lr_fun, rl_fun, left, right):
    return (kfun(fun=lr_fun, inp=[left], out=right),
            kfun(fun=rl_fun, inp=[right], out=left))


def keq(left, right):
    iden = adapter(lambda x: x)
    return iso(lr_fun=iden, rl_fun=iden, left=left, right=right)
