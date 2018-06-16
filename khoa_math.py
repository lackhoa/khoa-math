from misc import MyEnum, car, cdr, rcar, rcdr
from kset import KSet, KConst

from abc import ABC, abstractmethod
from copy import deepcopy
from enum import *
from typing import *
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
        fields = (f for f in [self.name, self.role, 'vals='+str(self.vals)] if f != '')
        return 'A: {}'.format(', '.join(fields))

    @property
    def children(self):
        """No children allowed!"""
        return []
    @children.setter
    def children(self, value):
        raise Exception('Atoms cannot have children')

    @property
    def val(self):
        return self.vals[0]

    def clone(self) -> 'Atom':
        res = Atom(role=self.role, vals=self.vals.clone())
        return res

    def __eq__(self, other) -> bool:
        return (type(self) == type(other)) and (self.vals == other.vals)

    def __hash__(self) -> int:
        return hash((self.role, self.vals))


class Mole(MathObj):
    def __init__(self, role: str, type_: Optional['MathT'],
                 cons: KSet = KConst.STR.value,
                 name: str='', parent=None, children: Iterable[Union[Atom, 'Mole']]=[]):
        super().__init__(role, name)
        self.type, self.cons = type_, cons
        self.parent, self.children = parent, tuple(children)

    def __repr__(self) -> str:
        fields = (f for f in [self.name, self.role, str(self.type),
                              'cons='+str(self.cons)]
                  if f != '')
        return 'M: {}'.format(', '.join(fields))

    def _pre_attach(self, parent: 'Mole'):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    @property
    def con(self):
        return self.cons[0]

    def has_path(self, role: str) -> bool:
        try: self.get_path(role); return True
        except ChildResolverError: return False

    def pave_way(self, path: str):
        """Keep attaching unknown nodes until `self.has_path(path)` is True"""
        if not self.has_path(path):
            if not self.has_path(car(path)):
                new_child = Mole(role=car(path), type_=None)
            else: new_child = self.get_path(car(path))
            new_child.parent = self
            new_child.pave_way(cdr(path))

    def kattach(self, node: Union[Atom, 'Mole'], path: str = '', mode: str = 'merge'):
        """
        Attach `node` to this molecule, with optional path down the line
        """
        if path != '':
            self.pave_way(path)
            self.get_path(path).kattach(node, mode=mode)
        elif type(node) == Atom:
            if self.has_path(node.role):
                same = self.get_path(node.role)
                same.vals = same.vals & node.vals
            else: node.parent = self
        elif type(node) == Mole:
            if self.has_path(node.role):
                same = self.get_path(node.role)
                if same.type == None: same.type = node.type
                else: assert(same.type == node.type), 'Two type, one node?'
                same.cons = same.cons & node.cons
                for node_child in node.children:
                    same.kattach(node_child, mode=mode)
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
