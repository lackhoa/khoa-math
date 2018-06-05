from misc import MyEnum
from kset import unify, KSet

from abc import ABC
from enum import Enum, auto
from typing import List, Set, Callable, Dict
from anytree import NodeMixin, RenderTree, find_by_attr, find


class MathObj(ABC):
    def __init__(self, role):
        self.role = role

    def get(self, path: str):
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

    def path(self, origin) -> str:
        res = ''
        node = self
        while node != origin:
            res = '/{}'.format(node.role) + res
            node = node.parent
            assert(node is not None),
            'You\'re probably asking for a path from a node of a different tree.'
        if res: res = res[1:]   # Get rid of the first slash if it's there
        return res

    def __eq__(self, other) -> bool:
        res = True
        if type(self) != type(other): res = False
        elif type(self) == Atom:
            res = (self.values == other.values)
        else:  # They're both molecules
            for child in self.children:
                try:
                    same = other.get(child.role)
                    if child != same: res = False; break
                except PathDownError: res = False; break
        return res

    @staticmethod
    def _recur_test(node, func: Callable[..., bool], conj = True) -> bool:
        res = True if conj else False
        if type(node) == Atom: return func(node)
        else:
            for child in node.children:
                if conj:
                    if not MathObj._recur_test(child, func, conj): res = False; break
                else:
                    if MathObj._recur_test(child, func, conj): res = True; break
        return res

    def is_inconsistent(self) -> bool:
        func = lambda n: n.values == []
        return MathObj._recur_test(self, func, False)

    def is_constant(self) -> bool:
        if self.queue: return False
        else:
            func = lambda n: len(n.values) == 1
            return MathObj._recur_test(self, func, True)

    def is_complete(self) -> bool:
        if self.queue: return False
        else:
            func = lambda n: (len(n.values) == 1) and (n.values != {KSet.UNKNOWN})
            return MathObj._recur_test(self, func, True)

class Atom(MathObj):
    def __init__(self, role: str, values={KSet.UNKNOWN}, web=[]):
        super().__init__(role)
        self.values = values
        self.web = web

    def _pre_attach(self, parent):
        assert(type(parent) != Atom), 'You cannot attach to an atom!'


class Molecule(MathObj):
    separator = '.'
    propa_rules = []

    def __init__(self, role: str, type_, cons, name=''):
        super().__init__(role)
        self.type = type_
        self.cons = cons
        self.name = name

    def __repr__(self):
        val = str(self.values) if self.values else ''
        return '{}:{}|{}:{}'.format(self.role, self.name, self.type, self.cons)

    def _pre_attach(self, parent):
        assert(type(parent) != Atom), 'You cannot attach to an atom!'

    def clone(self):
        """Return a deep copy of this object."""
        # Make a new math object
        res = MathObj(role=self.role, values=self.values)

        # Clone all children and nattach to the result
        # Note that the queue items that reference the children
        # are already handled by `nattach`
        for child in self.children:
            child_clone = child.clone()
            MathObj.nattach(child_clone, res)

        return res


    @staticmethod
    def kattach(child, parent, overwrite=True):
        if parent is not None:
            assert(type(child) == MathObj),
                'You can only kattach Math Objects!'
            assert(type(parent) == Molecule),
                'You can only kattach to Molecules!'
            try:
                same = parent.get(child.role)
                if overwrite:
                    same.parent = None
                    child.parent = parent
            except PathDownError:
                child.parent = parent


class MathType(MyEnum):
    PL_FORMULA = auto()
    PL_PROOF = auto()

class MathError(Exception):
    """Base class for exceptions in this module."""
    pass

class PathUpError(MathError):
    def __init__(self, ref, path, message='There is no way up.'):
        self.message = message
        self.ref = ref
        self.path = path

class PathDownError(MathError):
    def __init__(self, ref, path, message='There is no way down.'):
        self.message = message
        self.ref = ref
        self.path = path
