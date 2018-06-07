from misc import MyEnum
from typing import Iterable, Union, Callable, Optional

from itertools import takewhile
from enum import Enum


class KSet:
    def __init__(self,
                 content: Union[Iterable, Callable[..., bool]],
                 user_len: Optional[int] = None):
        self.content = content
        if user_len is not None: self.user_len = user_len

    def __len__(self) -> int:
        if hasattr(self, 'user_len'):
            return self.user_len
        elif hasattr(self.content, '__len__'):
            return len(self.content)
        elif self.is_explicit():
            return sum(1 for _ in self.content)
        else: raise LengthUnsupportedError(self)

    def has_len(self) -> bool:
        try: len(self); return True
        except LengthUnsupportedError(self): return False

    def __getitem__(self, index: int):
        for i, v in enumerate(self.content):
            if i == index: return v

    def __iter__(self):
        return iter(self.content)

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
        res: 'KSet'
        e1, e2 = self.is_explicit(), other.is_explicit()
        if e1:
            if e2:
                # Both are explicit
                if type(self.content) == type(other.content) == set:
                    # Special treatment for python sets as content
                    res = KSet(content = self.content & other.content)
                else:
                    in_other = lambda x: x in other
                    unified_len = min(len(self), len(other))
                    res = KSet(content = takewhile(in_other, self),
                               user_len = unified_len)
            else:
                # Only self is explicit
                in_other = lambda x: other.content(x)
                unified_len = min(len(self), len(other)) if other.has_len() else len(self)
                res = KSet(content = takewhile(in_other, self),
                           user_len = unified_len)
        elif e2:
            # Only other is explicit
            in_self = lambda x: self.content(x)
            unified_len = min(len(self), len(other)) if self.has_len() else len(other)
            res = KSet(content = takewhile(in_self, other),
                       user_len = unified_len)
        else:
            # None are explicit
            unified_len = min(len(self), len(other))\
                          if (self.has_len() and other.has_len())\
                          else None
            res = KSet(content = lambda x: self.content(x) and other.content(x),
                       user_len = unified_len)
        return res


# Some handy ksets to use
ANY = KSet(content = lambda x: True)
NONE = KSet(content = lambda x: False)
STR = KSet(content = lambda x: type(x) is str)


class KSetError(Exception):
    pass

class LengthUnsupportedError(KSetError):
    def __init__(self, ks: KSet, msg: str = 'Length cannot be calculated.'):
        self.ks = ks
        self.message = msg

