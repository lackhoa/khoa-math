from misc import MyEnum
from kset import KSet, KConst

from abc import ABC, abstractmethod
from copy import deepcopy
from enum import Enum, auto
from typing import List, Iterable, Set, Callable, Dict, Union
from anytree import NodeMixin, Resolver, ResolverError, ChildResolverError


class MathObj(ABC, NodeMixin):
    @abstractmethod
    def __init__(self, role, name=''):
        self.role, self.name = role, name

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

    def _recur_test(self, func: Callable[..., bool], conj = True) -> bool:
        res = True if conj else False
        if type(self) == Atom: return func(self)
        else:
            for child in self.children:
                if conj:
                    if not child._recur_test(func, conj): res = False; break
                elif not conj:
                    if child._recur_test(func, conj): res = True; break
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
    def __init__(self, role: str, vals: KSet, name: str=''):
        super().__init__(role, name)
        self.vals = vals

    def _pre_attach(self, parent):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def __repr__(self) -> str:
        return 'A({}, {}, {})'.format(self.role, self.vals, self.name)

    @property
    def children(self):
        """No children allowed!"""
        return []
    @children.setter
    def children(self, value):
        raise Exception('Atoms cannot have children')

    def clone(self) -> 'Atom':
        res = Atom(role=self.role, vals=self.vals.clone())
        return res

    def __eq__(self, other) -> bool:
        return (type(self) == type(other)) and (self.vals == other.vals)

    def __hash__(self) -> int:
        return hash((self.role, self.vals))


class Mole(MathObj):
    def __init__(self, role: str, type_: 'MathT',
                 cons: KSet = KConst.STR.value,
                 name: str='', parent=None, children: Iterable[Union[Atom, 'Mole']]=[]):
        super().__init__(role, name)
        self.type, self.cons = type_, cons
        self.parent, self.children = parent, tuple(children)

    def __repr__(self) -> str:
        return 'M({}, {}, {}, {})'.format(self.role, self.name, self.type, self.cons)

    def _pre_attach(self, parent: 'Mole'):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def has_path(self, role: str) -> bool:
        try: self.get_path(role); return True
        except ChildResolverError: return False

    def kattach(self, node: Union[Atom, 'Mole'], mode='unify'):
        """Attach `node` to this molecule"""
        if type(node) == Atom:
            if self.has_path(node.role):
                same = self.get_path(node.role)
                same.vals = same.vals & node.vals
            else: node.parent = self
        elif type(node) == Mole:
            if self.has_path(node.role):
                same = self.get_path(node.role)
                same.cons = same.cons & node.cons
                for node_child in node.children:
                    same.kattach(node_child)
            else: node.parent = self

    def spec(self, path: str) -> bool:
        try:
            child = self.get_path(path)
            if type(child) == Atom: return child.vals.is_singleton()
            else: return child.cons.is_singleton()
        except ChildResolverError: return False

    def clone(self) -> 'Mole':
        res = Mole(role=self.role, type_=self.type, cons=self.cons.clone())
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
        return hash((self.role, self.type, self.cons, self.children))

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
