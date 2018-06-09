from misc import MyEnum
from kset import KSet, STR, LengthUnsupportedError

from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum, auto
from typing import List, Iterable, Set, Callable, Dict, Union
from anytree import NodeMixin, Resolver, ResolverError


class MathObj(ABC, NodeMixin):
    def __init__(self, role):
        self.role = role

    def get_role(self, path: str):
        r = Resolver('role')
        return r.get(self, path)

    def _equiv(self, other) -> bool:
        """Warning: placeholder code"""
        res = True
        if type(self) != type(other): res = False
        elif type(self) == Atom:
            res = (self.vals == other.vals)
        else:
            # They're both molecules
            if self.cons == other.cons:
                for child in self.children:
                    try:
                        same = other[child.role]
                        if not child._equiv(same): res = False; break
                    except PathDownError: res = False; break
        return res

    def _recur_test(func: Callable[..., bool], conj = True) -> bool:
        res = True if conj else False
        if type(self) == Atom: return func(self)
        else:
            for child in self.children:
                if conj:
                    if not MathObj._recur_test(child, func, conj): res = False; break
                else:
                    if MathObj._recur_test(child, func, conj): res = True; break
        return res

    def is_inconsistent(self) -> bool:
        func = lambda a: a.vals.is_empty()
        return self._recur_test(func, False)

    def is_complete(self) -> bool:
        func = lambda a: a.vals.is_singleton()
        return self._recur_test(func, True)

    @abstractmethod
    def clone(self):
        """Return a deep copy of this object."""
        pass

class Atom(MathObj):
    def __init__(self, role: str, vals: KSet, web: Iterable[str] = []):
        super().__init__(role)
        self.vals = vals
        self.web = web

    def _pre_attach(self, parent):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def __repr__(self) -> str:
        return '{} {}'.format(self.role, self.vals)

    @property
    def children(self):
        """No children allowed!"""
        return []
    @children.setter
    def children(self, value):
        raise Exception('Are you nuts? An atom can\'t reproduce!')

    def clone(self):
        # Gotta deep copy the mutable stuff
        web_clone, vals_clone = deepcopy(self.web), deepcopy(self.vals)
        res = Atom(role=self.role, vals=vals_clone, web=web_clone)
        return res


class Molecule(MathObj):
    propa_rules = []

    def __init__(self, role: str, type_: 'MathType', cons: KSet = STR, name: str=''):
        super().__init__(role)
        self.type = type_
        self.cons = cons
        self.name = name

    def __repr__(self) -> str:
        return '{} {} {} {}'.format(self.role, self.name, self.type, self.cons)

    def _pre_attach(self, parent: 'Molecule'):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def clone(self):
        cons_clone = deepcopy(self.cons)  # cons can be mutable
        res = Molecule(role=self.role, type_=self.type, cons=cons_clone)
        # Clone all the children, too
        for child in self.children:
            child.clone().parent = res
        return res


class MathType(MyEnum):
    WFF = auto()
    PROOF = auto()
