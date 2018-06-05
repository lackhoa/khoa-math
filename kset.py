from misc import MyEnum
from khoa_math import *
from typing import Iterable, Union

from itertools import takewhile
from enum import auto


class KConst(MyEnum):
    UNKNOWN = auto()


class KSet:
    def __init__(self,
                 content: Union[Iterable, Callable[..., bool], KConst],
                 user_len=None: Union[int, NoneType]):
        self.content = content
        if user_len is not None: self.user_len = user_len

    def __len__(self) -> int:
        if has_attr(self, 'user_len'):
            return self.user_len
        elif has_attr(self.content, '__len__'):
            return len(self.content)
        elif self.is_explicit():
            return sum(1 for _ in self.content)
        else: raise LengthUnsupportedError

    def is_known(self): return (self.content != KConst.UKNOWN)

    def is_explicit(self):
        try: iter(self); return True
        except TypeError: return False

    def is_empty(self):
        try: return (len(self) == 0)
        except LengthUnsupportedError: return False

    def is_singleton(self):
        try: return (len(self) == 1)
        except LengthUnsupportedError: return False

    @staticmethod
    def unify(kset1: KSet, kset2: KSet):
        res = KSet(content = KConst.UNKNOWN)
        k1, k2, e1, e2 = kset1.is_known(), kset2.is_known(), kset1.is_explicit(), kset2.is_explicit()
        if e1:
            res = e1
            if e2:
                in_kset2 = lambda x: x in kset2
                res = KSet(content = takewhile(in_kset2, kset1))
            elif k2:
                in_kset2 = lambda x: kset2.content(x)
                res = KSet(content = takewhile(in_kset2, kset1))
        elif e2:
            res = e2
            if k1:
                in_kset1 = lambda x: kset1.content(x)
                res = KSet(content = takewhile(in_kset1, kset2))
        elif k1:
            res = k1
            if k2:
                res = KSet(lambda x: k1.content(x) and k2.content(x))
        elif k2: res = k2
        return res

class KSetError(Exception):
    pass

class LengthUnsupportedError(KSetError):
    def __init__(self, ks: KSet, msg='Length cannot be calculated.': str):
        self.ks = ks
        self.message = msg

class ContentNotIterableError(KSetError):
    def __init__(self, ks: KSet, msg='Content cannot be iterated.': str):
        self.ks = ks
        self.message = msg
