from misc import MyEnum
from typing import Iterable, Union, Callable, Optional

from itertools import takewhile
from enum import auto


class KConst(MyEnum):
    UNKNOWN = auto()


class KSet:
    def __init__(self,
                 content: Union[Iterable, Callable[..., bool], KConst],
                 user_len: Optional[int] = None):
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

    def has_len(self) -> bool:
        try: len(self); return True
        except LengthUnsupportedError: return False

    def __getitem__(self, index: int):
        for i, v in enumerate(self.content):
            if i == index: return v

    def __iter__(self):
        return iter(self.content)

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

    def __and__(self, other: 'KSet'):
        res = KSet(content = KConst.UNKNOWN)
        k1, k2, e1, e2 = self.is_known(), other.is_known(), self.is_explicit(), other.is_explicit()
        if e1:
            res = self
            if e2:
                if type(self.content) == type(other.content) == set:
                    # Special treatment for embedded sets
                    res = KSet(content = self.content & other.content)
                else:
                    in_other = lambda x: x in other
                    unified_len = min(len(self), len(other))
                    res = KSet(content = takewhile(in_other, self),
                               user_len = unified_len)
            elif k2:
                in_other = lambda x: other.content(x)
                unified_len = min(len(self), len(other)) if other.has_len() else len(self)
                res = KSet(content = takewhile(in_other, self),
                           user_len = unified_len)
        elif e2:
            res = other
            if k1:
                in_self = lambda x: self.content(x)
                unified_len = min(len(self), len(other)) if self.has_len() else len(other)
                res = KSet(content = takewhile(in_self, other),
                           user_len = unified_len)
        elif k1:
            res = self
            unified_len = min(len(self), len(other)) if self.has_len()\
                          and other.has_len() else None
            if k2:
                res = KSet(content = lambda x: k1.content(x) and k2.content(x),
                           user_len = unified_len)
        elif k2: res = other
        return res

class KSetError(Exception):
    pass

class LengthUnsupportedError(KSetError):
    def __init__(self, ks: KSet, msg: str = 'Length cannot be calculated.'):
        self.ks = ks
        self.message = msg
