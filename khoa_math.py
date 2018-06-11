from misc import MyEnum
from kset import KSet, KConst

from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum, auto
from typing import List, Iterable, Set, Callable, Dict, Union
from anytree import NodeMixin, Resolver, ResolverError


class MathObj(ABC, NodeMixin):
    @abstractmethod
    def __init__(self, role):
        self._role = role

    def get_path(self, path: str):
        r = Resolver('role')
        return r.get(self, path)

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
    def __init__(self, role: str, vals: KSet):
        self._role, self.vals = role, vals

    @property
    def role(self): return self._role

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
        raise Exception('Atoms cannot have children')

    def clone(self):
        # Gotta deep copy the mutable stuff
        vals_clone = deepcopy(self.vals)
        res = Atom(role=self.role, vals=vals_clone)
        return res


class Mole(MathObj):
    def __init__(self, role: str, type_: 'MathType', cons: KSet = KConst.STR, name: str=''):
        self._role, self._type, self.cons, self.name = role, type_, cons, name

    @property
    def role(self): return self._role

    @property
    def type(self): return self._type

    def __repr__(self) -> str:
        return '{} {} {} {}'.format(self.role, self.name, self.type, self.cons)

    def _pre_attach(self, parent: 'Mole'):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def clone(self):
        cons_clone = deepcopy(self.cons)  # cons can be mutable
        res = Mole(role=self.role, type_=self.type, cons=cons_clone)
        # Clone all the children, too
        for child in self.children:
            child.clone().parent = res
        return res


class FAtom(Atom):
    """Frozen Atom"""
    def __init__(self, atom: Atom):
        self._role, self._vals = atom.role, atom.vals

    @property
    def vals(self):
        return self._vals

    @property
    def parent(self):
        try: return self.__parent
        except AttributeError: return None

    @parent.setter
    def parent(self, value):
        raise AttributeError('Cannot change a frozen atom\'s parent')

    def __eq__(self, other) -> bool:
        return (type(self) == type(other)) and (self.vals == other.vals)

    def __hash__(self) -> int:
        return hash((self.role, self.vals))


class FMole(Mole):
    """Frozen Molecules"""
    def __init__(self, mole: Atom):
        self._role, self._type, self._cons, self.name = mole.role, mole.type,\
            mole.cons, mole.name
        self._children = tuple()
        for child in mole.children:
            if type(child) == Atom:
                self._children += (FAtom(child),)
            else:
                self._children += (FMole(child),)

    @property
    def cons(self): return self._cons

    @property
    def parent(self, value):
        try: return self.__parent
        except AttributeError: return None

    @parent.setter
    def parent(self, value):
        raise AttributeError('Cannot change a frozen molecule\'s parent')

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, value):
        raise AttributeError('Cannot change a frozen molecule\'s children')

    def __eq__(self, other) -> bool:
        if type(self) == type(other) and len(self.children) == len(other.children):
            for child in self.children:
                if child != other.get_path(child.role): break
            else: return True
        return False

    def __hash__(self) -> int:
        """Hopefully this does not take too much time"""
        return hash((self.role, self.type, self.cons, self.children))

class MathType(MyEnum):
    WFF = auto()
    PROOF = auto()




# ===Testing zone===
if __name__ == '__main__':
    a = Atom('sub', KSet(frozenset()))
    m = Mole('root', MathType.WFF, KSet(frozenset()))
    a.parent = m
    fa = FAtom(a)
    fm = FMole(m)
