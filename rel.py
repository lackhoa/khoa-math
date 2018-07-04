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

    def __getattr__(self, name):
        if hasattr(self, name):
            return getattr(self, name)
        else:
            return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __repr__(self) -> str:
        if self.type == 'FUN':
            return '{} -> {}'.format(' '.join(self['inp']), self['out'])
        elif self.type == 'UNION':
            return '(U {}) = {}'.format(' '.join(self['subs']), self['sup'])
        elif self.type == 'ISO':
            return '{} <-> {}'.format(self['left'], self['right'])


def uno(subs, sup):
    return Rel(type_='UNION', subs=subs, sup=sub)


def funo(fun, inp, out):
    return Rel(type_='FUN', fun=fun, inp=inp, out=out)


def iso(lr_fun, rl_fun, left, right):
    return Rel(type_='ISO', lr_fun=lr_fun, rl_fun=rl_fun, left=left, right=right)


def eq(left, right):
    iden = lambda x: x
    return iso(lr_fun=iden, rl_fun=iden, left=left, right=right)
