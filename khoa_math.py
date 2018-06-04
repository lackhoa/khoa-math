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
                        if child.role == n:
                            res = child; break
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

        # About the queue (Yikes!):
        # Take care of queue items with this node as the reference
        for q in self.queue:
            if q['ref'] == self:
                res.queue += [dict(values=q['values'], ref=res, path=q['path'])]

        # Clone all children and nattach to the result
        # Note that the queue items that reference the children
        # are already handled by `nattach`
        for child in self.children:
            child_clone = child.clone()
            MathObj.nattach(child_clone, res)

        return res


    @staticmethod
    def nattach(child, parent, overwrite=True):
        """
        'Normal attach': attaching nodes, in a straightforward way that cares about roles.
        Please don't invoke the API's normal way to attach nodes. Use either this or `kattach`

        Unlike `kattach`, this method attaches a `MathObj` to parent. The child's queue is
        propagated back to the root.

        :param overwrite: If set to True, if there is already another node with the same role,
        delete that node and attach the argument instead. If set to False, don't do anything.
        """
        if parent is not None:
            assert(type(child) == MathObj), 'You can only nattach Math Objects!'
            assert(type(parent) == MathObj), 'You can only nattach to Math Objects!'

            try:
                same = parent.get(child.role)
                if overwrite:  # If a node with the same role is present
                    parent.queue.extend(child.queue)  # Preserve child's queue items
                    same.parent = None  # Remove the same-role node
                    child.parent = parent  # Attach the new node

            except PathDownError:
                # Do things normally here:
                parent.queue.extend(child.queue)  # Preserve child's queue items
                child.parent = parent


    @staticmethod
    def kattach(child: Dict, parent):
        """
        Like `nattach`, but adds new knowledge to the queue,
        and intended for single node only.

        :param child: A dictionary with role and values (like in a node).
        Why is it not a MathObj? Because MathObj can have child.
        """
        assert(type(parent) == MathObj), 'You can only kattach to Math Objects!'

        try:
            same = parent.get(child['role'])  # If a node with the same role is present
            if same.values:  # Only do work when it is a leaf
                unified = unify(child['values'], same.values)
                if unified != same.values:  # Did we learn something new?
                    same._values = unified
                    # Propagate the change:
                    for func in MathObj.propa_rules:
                        parent.queue += [dict(values = r['values'],
                            ref = parent, path=r['path']) for r in func(child, parent)]
        except PathDownError:
            # Convert child to MathObj representation, and add it to parent
            child_obj = MathObj(role=child['role'], values=child['values'])
            child_obj.parent = parent

            # Propagate the change:
            for func in MathObj.propa_rules:
                parent.queue += [dict(values = r['values'],
                    ref = parent, path=r['path']) for r in func(child, parent)]


class MathType(MyEnum):
    PL_FORMULA = auto()
    PL_PROOF = auto()


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class PathUpError(Error):
    def __init__(self, ref, path, message='There is no way up.'):
        self.message = message
        self.ref = ref
        self.path = path


class PathDownError(Error):
    def __init__(self, ref, path, message='There is no way down.'):
        self.message = message
        self.ref = ref
        self.path = path
