from misc import MyEnum
from kset import KSet, KConst

from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum, auto
from typing import List, Iterable, Set, Callable, Dict, Union
from anytree import NodeMixin, Resolver, ResolverError, ChildResolverError


class MathObj(ABC, NodeMixin):
    @abstractmethod
    def __init__(self, role):
        self._role = role

    def __check_loop(self, node):
        if node is not None:
            if node is self:
                msg = "Cannot set parent. %r cannot be parent of itself."
                raise LoopError(msg % self)
            if any([n is self for n in node.path]):
                msg = "Cannot set parent. %r is parent of %r."
                raise LoopError(msg % (self, node))

    def __attach(self, parent):
        if parent is not None:
            self._pre_attach(parent)
            parentchildren = parent.__children_
            assert not any ([child is self for child in parentchildren]),\
                    "Tree internal data is corrupt."
            # ATOMIC START
            parentchildren.append(self)
            self.__parent = parent
            # ATOMIC END
            self._post_attach(parent)


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
        self.role, self.vals = role, vals

    def _pre_attach(self, parent):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def __repr__(self) -> str:
        return '{}({}, {})'.format(self.__class__.__name__, self.role, self.vals)

    @property
    def children(self):
        """No children allowed!"""
        return []
    @children.setter
    def children(self, value):
        raise Exception('Atoms cannot have children')

    def clone(self) -> 'Atom':
        res = Atom(role=self.role, vals=self.vals)
        return res

    def __eq__(self, other) -> bool:
        return (type(self) == type(other)) and (self.vals == other.vals)

    def __hash__(self) -> int:
        return hash((self.role, self.vals))


class Mole(MathObj):
    def __init__(self, role: str, type_: 'MathT',
                 cons: KSet = KConst.STR.value, rels: Iterable['Rel'] = [],
                 name: str='', parent=None, children: Iterable[Union[Atom, 'Mole']]=[]):
        self.role, self.type, self.cons, self.rels = role, type_, cons, rels
        self.name, self.parent, self.children = name, parent, tuple(children)

    def __repr__(self) -> str:
        return '{}({}, {}, {}, {})'.format(self.__class__.__name__,
                                           self.role, self.name,
                                           self.type, self.cons)

    def _pre_attach(self, parent: 'Mole'):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def has_path(self, role: str) -> bool:
        try: self.get_path(role); return True
        except ChildResolverError: return False

    def clone(self) -> 'Mole':
        res = Mole(role=self.role, type_=self.type, cons=self.cons, rels=self.cons)
        # Clone all the children, too
        for child in self.children:
            child.clone().parent = res
        return res

    def __eq__(self, other) -> bool:
        res = True
        if type(self) == type(other) and len(self.children) == len(other.children):
            for child in self.children:
                if (not other.has_path(child.role)) or (child != other.get_path(child.role)):
                    res = False; break
        else: res = False
        return res

    def __hash__(self) -> int:
        """Hopefully this does not take too much time"""
        return hash((self.role, self.type, self.cons, self.children, self.rels))


ATMO = Union[Atom, Mole]


class MathT(MyEnum):
    WFF = auto()
    PROOF = auto()




# ===Testing zone===
if __name__ == '__main__':
    a = Atom('sub', KSet(frozenset()))
    m = Mole('root', MathT.WFF, KSet(frozenset()))
    a.parent = m
    fa = FAtom(a)
    fm = FMole(m)
