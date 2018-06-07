from misc import MyEnum
from kset import KSet, STR, LengthUnsupportedError

from abc import ABC
from enum import Enum, auto
from typing import List, Iterable, Set, Callable, Dict, Union
from anytree import NodeMixin


class MathObj(ABC, NodeMixin):
    def __init__(self, role):
        self.role = role

    def __getitem__(self, path: str):
        res = self
        if path:
            for n in path.split('/'):
                if n == '..':
                    if not res.parent: raise PathUpError(self, path)
                    else: res = res.parent
                else:
                    for child in res.children:
                        if child.role == n: res = child; break
                    else: raise PathDownError(self, path)
        return res

    def path_from(self, origin) -> str:
        res = ''
        node = self
        while node != origin:
            res = '/{}'.format(node.role) + res
            node = node.parent
            assert(node is not None),\
                'You\'re probably asking for a path from a node of a different tree.'
        if res: res = res[1:]   # Get rid of the first slash if it's there
        return res

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

    def clone(self):
        """Return a deep copy of this object."""
        res = None
        if type(self) == Atom:
            res = Atom(role=self.role, values=self.values, web=self.web)
        elif type(self) == Molecule:
            for child in self.children:
                res.parent += [child.clone()]
        return res

class Atom(MathObj):
    def __init__(self, role: str, values: KSet, web: Iterable[str] = []):
        super().__init__(role)
        self.values = values
        self.web = web

    def _pre_attach(self, parent):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'

    def __repr__(self) -> str:
        return str(self.values.content)

    @property
    def children(self):
        """No children allowed!"""
        return []
    @children.setter
    def children(self, value):
        raise Exception('Are you nuts? An atom can\'t reproduce!')


class Molecule(MathObj):
    separator = '.'
    propa_rules = []

    def __init__(self, role: str, type_: 'MathType', cons: KSet = STR):
        super().__init__(role)
        self.type = type_
        self.cons = cons

    def __repr__(self) -> str:
        name = self.name if hasattr(self, 'name') else ''
        return '{}:{}|{}:{}'.format(self.role, name, self.type,
                self.cons)

    def _pre_attach(self, parent: 'Molecule'):
        assert(type(parent) != Atom), 'Can\'t attach to an atom!'


class MathType(MyEnum):
    WFF = auto()
    PROOF = auto()

class PathError(Exception):
    """Base class for exceptions in this module."""
    pass

class PathUpError(PathError):
    def __init__(self, ref, path, message='There is no way up.'):
        self.message = message
        self.ref = ref
        self.path = path

class PathDownError(PathError):
    def __init__(self, ref, path, message='There is no way down.'):
        self.message = message
        self.ref = ref
        self.path = path
