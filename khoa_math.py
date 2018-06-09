from misc import MyEnum
from kset import KSet, STR, LengthUnsupportedError

from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Iterable, Set, Callable, Dict, Union
from anytree import NodeMixin, Resolver, ResolverError


class MathObj(ABC, NodeMixin):
    def __init__(self, role):
        self.role = role

    # def __getitem__(self, path: str):
    #     r = Resolver('role')
    #     return r.get(self, path)

    def _equiv(self, other) -> bool:
        """Warning: placeholder code"""
        res = True
        if type(self) != type(other): res = False
        elif type(self) == Atom:
            res = (self.values == other.values)
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
        func = lambda a: a.values.is_empty()
        return self._recur_test(func, False)

    def is_complete(self) -> bool:
        func = lambda a: a.values.is_singleton()
        return self._recur_test(func, True)

    @abstractmethod
    def clone(self):
        """Return a deep copy of this object."""
        pass

class Atom(MathObj):
    def __init__(self, role: str, values: KSet, web: Iterable[str] = []):
        super().__init__(role)
        self.values = values
        self.web = web

    def _pre_attach(self, parent):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def __repr__(self) -> str:
        cur_val = self.cur_val if hasattr(self, 'cur_val') else ''
        return '{} | {}'.format(self.role, cur_val)

    @property
    def children(self):
        """No children allowed!"""
        return []
    @children.setter
    def children(self, value):
        raise Exception('Are you nuts? An atom can\'t reproduce!')

    def clone(self):
        res = Atom(role=self.role, values=self.values, web=self.web)
        if hasattr(self, 'cur_val'): res.cur_val = self.cur_val
        return res


class Molecule(MathObj):
    propa_rules = []

    def __init__(self, role: str, type_: 'MathType', cons: KSet = STR):
        super().__init__(role)
        self.type = type_
        self.cons = cons

    def __repr__(self) -> str:
        name = self.name if hasattr(self, 'name') else ''
        cur_con = self.cur_con if hasattr(self, 'cur_con') else ''
        return '{} | {} | {} | {}'.format(self.role, name, self.type, cur_con)

    def _pre_attach(self, parent: 'Molecule'):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def clone(self):
        res = Molecule(role=self.role, type_=self.type, cons=self.cons)
        if hasattr(self, 'cur_con'): res.cur_con = self.cur_con
        for child in self.children:
            child.clone().parent = res
        return res


class MathType(MyEnum):
    WFF = auto()
    PROOF = auto()
