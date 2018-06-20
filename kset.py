from misc import *
from typing import Iterable, Union, Callable, Optional

from enum import Enum


class KSet:
    def __init__(self,
                 content: Optional[Iterable] = None,
                 qualifier: Optional[Callable[..., bool]] = None,
                 custom_repr: Optional[str] = None):
        """Content should be set for better performance"""
        assert((content is None) ^ (qualifier is None)),\
                'One and only one of either content or qualifier should be present'
        self.content = content
        self.qualifier, self.custom_repr = qualifier, custom_repr

    @property
    def only(self):
        assert(self.is_singleton()), 'This set is NOT a singleton'
        return self[0]

    @property
    def content(self):
        if self._content is None: return None
        else:
            save, res = tee(self._content)
            # Iteration on the content property won't affect the original iterable
            self._content = save
            return res

    @content.setter
    def content(self, value):
        self._content = value

    def __eq__(self, other):
        if self.qualifier is None and other.qualifier is None:
            return set(self.content) == set(other.content)
        else:
            return self.qualifier == other.qualifier

    def __hash__(self) -> int:
        if self.content is not None:
            return hash(frozenset(self.content))
        else: return hash(self.qualifier)

    def clone(self) -> 'KSet':
        # Content is already a copy, qualifier and custom_repr are immutable
        return KSet(self.content, self.qualifier, self.custom_repr)

    def __repr__(self) -> str:
        left_sur, right_sur = '<', '>'
        core: str
        if self.custom_repr: core = self.custom_repr
        elif self.is_explicit(): core = ', '.join(map(str, list(self.content)))
        else: core = str(self.qualifier)
        return '{}{}{}'.format(left_sur, core, right_sur)

    def __len__(self) -> int:
        if hasattr(self.content, '__len__'): return len(self.content)
        else: return sum(1 for _ in self.content)

    def is_explicit(self):
        return (self.content is not None)

    def __getitem__(self, index: int):
        """For explicit ksets only."""
        res = nth(self.content, index)
        if res is not None: return res
        else: raise IndexError

    def __iter__(self):
        """For explicit ksets only."""
        return iter(self.content)

    def __call__(self, val):
        """Usable for all ksets."""
        if self.is_explicit(): return (val in self.content)
        else: return self.qualifier(val)

    def is_empty(self):
        return (len(self) == 0) if self.is_explicit() else False

    def is_singleton(self):
        return (len(self) == 1) if self.is_explicit() else False

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
                    res = KSet(content = filter(other, self))
            else:
                # Only `self` is explicit: result is explicit
                unified_len = min(len(self), len(other)) if other.is_explicit() else len(self)
                res = KSet(content = filter(other, self))
        elif e2:
            # Only `other` is explicit: result is explicit
            unified_len = min(len(self), len(other)) if self.is_explicit() else len(other)
            res = KSet(content = filter(self, other))
        else:
            # Either is explicit: result is implicit
            unified_len = min(len(self), len(other))\
                          if (self.is_explicit() and other.is_explicit())\
                          else None
            res = KSet(qualifier = lambda x: self(x) and other(x))
        return res


# Some handy ksets
class KConst(Enum):
    ANY  = KSet(qualifier = lambda x: True, custom_repr='ANY')
    NONE = KSet(qualifier = lambda x: False, custom_repr='NONE')
    STR  = KSet(qualifier = lambda x: type(x) is str, custom_repr='STR')
    SET  = KSet(qualifier = lambda x: type(x) is set or type(x) is frozenset,
                custom_repr='SET')
    INT  = KSet(qualifier = lambda x: type(x) is int, custom_repr='INT')
    

def ks(value):
    """Help make a quick kset based on a single value"""
    return KSet(content={value})

def adapter(fun: Callable):
    """
    Wrap a function's inputs and output with kset
    E.g: if f(a) = b then adapter(f)(KSet({a})) = KSet({b})
    """
    take_only = lambda s: s.only
    return lambda *args: ks(fun(*map(take_only, args)))

if __name__ == '__main__':
    s1 = KSet({2,3,5,1,4})
    s2 = KSet([1,2,3,4,5])
    assert(s1 == s2)
