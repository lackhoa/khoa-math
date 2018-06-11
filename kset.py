from misc import MyEnum
from typing import Iterable, Union, Callable, Optional

from itertools import takewhile
from enum import Enum


class KSet:
    def __init__(self,
                 content: Optional[Iterable] = None,
                 qualifier: Optional[Callable[..., bool]] = None,
                 user_len: Optional[int] = None,
                 custom_repr: Optional[str] = None):
        assert((content is None) ^ (qualifier is None)),\
                'One and only one of either content or qualifier should be present'
        # Guarantee immutability for content (as far as I know)
        if type(content) == list or type(contet) == set:
            content = frozenset(content)
        self.content, self.qualifier, self.user_len, self.custom_repr =\
            content, qualifier, user_len, custom_repr

    def __eq__(self, other):
        return self.content == other.content and self.qualifier == other.qualifier

    def __hash__(self) -> int:
        return hash((self.content, self.qualifier))

    def __repr__(self) -> str:
        if self.custom_repr: return self.custom_repr
        elif self.is_singleton(): return str(self[0])
        elif self.is_explicit(): return str(self.content)
        else: return str(self.qualifier)

    def has_len(self) -> bool:
        return (self.user_len is not None) or self.is_explicit()

    def __len__(self) -> int:
        if self.user_len is not None:
            return self.user_len
        elif hasattr(self.content, '__len__'):
            return len(self.content)
        else:
            return sum(1 for _ in self.content)

    def is_explicit(self):
        return (self.content is not None)

    def __getitem__(self, index: int):
        """For explicit ksets only."""
        for i, v in enumerate(self.content):
            if i == index: return v
        # Getting out of the loop means failure
        raise IndexError

    def __iter__(self):
        """For explicit ksets only."""
        return iter(self.content)

    def __call__(self, val):
        """Usable for all ksets."""
        if self.is_explicit(): return (val in self.content)
        else: return self.qualifier(val)

    def make_explicit(self):
        """(For explicit ksets) Turn content to set. Be careful with this!"""
        self.content = set(self.content)

    def is_empty(self):
        return (len(self) == 0) if self.has_len() else False

    def is_singleton(self):
        return (len(self) == 1) if self.has_len() else False

    def __and__(self, other: 'KSet'):
        res: 'KSet'
        e1, e2 = self.is_explicit(), other.is_explicit()
        if e1:
            if e2:
                # Both are explicit: result is explicit
                try:
                    # Special treatment for types that implements union
                    res = KSet(content = self.content & other.content)
                except TypeError:
                    unified_len = min(len(self), len(other))
                    res = KSet(content = takewhile(other, self),
                               user_len = unified_len)
            else:
                # Only `self` is explicit: result is explicit
                unified_len = min(len(self), len(other)) if other.has_len() else len(self)
                res = KSet(content = takewhile(other, self),
                           user_len = unified_len)
        elif e2:
            # Only `other` is explicit: result is explicit
            unified_len = min(len(self), len(other)) if self.has_len() else len(other)
            res = KSet(content = takewhile(self, other),
                       user_len = unified_len)
        else:
            # Either is explicit: result is implicit
            unified_len = min(len(self), len(other))\
                          if (self.has_len() and other.has_len())\
                          else None
            res = KSet(qualifier = lambda x: self(x) and other(x),
                       user_len = unified_len)
        return res


# Some handy ksets
class KConst(Enum):
    ANY = KSet(qualifier = lambda x: True, custom_repr='ANY')
    NONE = KSet(qualifier = lambda x: False, custom_repr='NONE')
    STR = KSet(qualifier = lambda x: type(x) is str, custom_repr='STR')


class KSetError(Exception):
    pass

class KSetDataError(KSetError):
    def __init__(self, msg):
        self.message = msg
