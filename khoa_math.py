from kset import *

from enum import Enum, auto
from typing import List, Set, Callable, Dict
from anytree import NodeMixin, RenderTree, find_by_attr, find

# This file contains the basis of mathematics

class MathObj(NodeMixin):
    """
    This class is the base for all mathematical objects, that's why it doesn't do anything
    Most math objects are recursive, that's why they should be trees.

    Math Objects are unknown and 'invalid' by default, to become 'valid',
    they must be checked by a validating routine.

    The "content" of a Math Object can be described by either a single 'value'
    attribute (then we call the object 'atomic'), or by many MathObj as children
    (then we call it 'composite'). Each child node has its role. All leaves are atomic,
    and all atoms are leaves.

    All data are represented by the value attribute of some leaves.

    In this knowledge model, everything is a possibility, that's why all values must be
    a KSET. This is consistent with the paragraph above since knowledge sets can only
    contain data.

    Note that the tree NEVER adds new nodes on its own. The user controls everything.
    The only way to changing the object is via `nattach` or `kattach`.

    About propa_rules: these are functions that takes a (child, parent) tuple
    (child is a (role, value) Dict and parent is a MathObj) and return a list of queue items,
    minus the reference point, since it is defaulted to be the parent of the attachment.

    About the queue: The queue is for new knowledge. Queue item are dictionaries
    containing <value> <reference point>, and <path> (in UNIX style).
    The intended action is attaching the node to the parent indicated by
    'path' from 'reference point'

    Mental note: 'type' can be reduced to just a value: an object has type A if its children
    with role 'type' has value A. If we can replace two concepts with one, do it.
    """


    # Class variables
    separator = '.'
    propa_rules = []


    def __init__(self, role: str='root', value: Set=None, name=''):
        """
        :param name: How you want to call this node (unimportant,mainly for roots).
        """
        self.name = name
        self._role = role
        self._value = value
        self.parent = None  # We don't attach nodes willy-nilly, see 'kattach' for more
        self._queue = []

        # Some initial mandatory children for composite objects:
        if self.value is None:
            MathObj.nattach(MathObj(role='type', value={KSet.UNKNOWN}), self)


    @property
    def role(self):
        return self._role


    @property
    def value(self):
        return self._value


    def clear_val(self):
        """Clear all values in the node except for UNKNOWN"""
        self._value = {KSet.UNKNOWN} if KSet.UNKNOWN in self.value else set()


    @property
    def root(self):
        if self.parent == None: return self
        else: return self.parent.root


    @property
    def queue(self):
        return self.root._queue  # The root manages the queue


    @queue.setter
    def queue(self, q):
        self.root._queue = q


    def __repr__(self):
        val = str(self.value) if self.value else ''
        return '{}{}|{}'.format(self.role, self.name, val)


    def _pre_attach(self, parent):
        assert(parent.value == None), 'You cannot attach to a composite object.'


    def get(self, path=''):
        """
        Get a descendant of a this object, referenced by path.
        Paths are ultimately a series of movements, separated by forward slashes
        (in UNIX fashion, but instead of names, we use roles)
        """
        res = self

        # Walk down the path:
        if path:
            for n in path.split('/'):
                if n == '..':
                    if not res.parent: raise PathUpError(self, path)
                    else: res = res.parent
                else:
                    for child in res.children:
                        if child.role == n:
                            res = child; break
                    else: raise PathDownError(self, path)  # For-Else

        return res


    @staticmethod
    def _recur_test(node, func: Callable[..., bool], conj = True) -> bool:
        """
        Template for recursive tests on trees, written in conjunctive normal form.
        :param func: function to test on all nodes.
        :param conj: works as follow
        - set to True:  res = p1 & p2 & ... & pn
        - set to False: res = p1 v p2 v ... v pn
        """
        res = True if conj else False

        if node.value is not None: return func(node)
        else:
            for child in node.children:
                if conj:
                    if not MathObj._recur_test(child, func, conj): res = False; break
                else:
                    if MathObj._recur_test(child, func, conj): res = True; break

        return res


    def is_inconsistent(self) -> bool:
        """
        A Math Object is 'inconsistent' either when its value is empty,
        or when one of its children is inconsistent.
        """
        func = lambda n: n.value == set()
        return MathObj._recur_test(self, func, False)


    def is_constant(self) -> bool:
        """
        An object is constant when:
        1) its queue is empty, and
        2) its value is a singleton or all of its children are constant.
        """
        if self.queue: return False
        else:
            func = lambda n: len(n.value) == 1
            return MathObj._recur_test(self, func, True)


    def is_complete(self) -> bool:
        """
        Likewise, an object is complete when:
        1) its queue is empty, and
        2) its value is a singleton (but not {UNKNOWN}) or all of its children are complete.
        """
        if self.queue: return False
        else:
            func = lambda n: (len(n.value) == 1) and (n.value != {KSet.UNKNOWN})
            return MathObj._recur_test(self, func, True)


    def clone(self):
        """Return a deep copy of this object."""
        # Make a new math object
        res = MathObj(role=self.role, value=self.value)

        # About the queue (Yikes!):
        # Take care of queue items with this node as the reference
        for q in self.queue:
            if q['ref'] == self:
                res.queue += [dict(value=q['value'], ref=res, path=q['path'])]

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

        Unlike `kattach`, this method attaches a `MathObj` to parent.

        Note that the child's queue is propagated back to the root.

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

        :param child: A dictionary with role and value (like in a node).
        Why is it not a MathObj? Because MathObj can have child.
        """
        assert(type(parent) == MathObj), 'You can only kattach to Math Objects!'

        try:
            same = parent.get(child['role'])  # If a node with the same role is present
            if same.value:  # Only do work when it is a leaf
                unified = unify(child['value'], same.value)
                if unified != same.value:  # Did we learn something new?
                    same._value = unified
                    # Propagate the change:
                    for func in MathObj.propa_rules:
                        parent.queue += [dict(value = r['value'],
                            ref = parent, path=r['path']) for r in func(child, parent)]
        except PathDownError:
            # Convert child to MathObj representation, and add it to parent
            child_obj = MathObj(role=child['role'], value=child['value'])
            child_obj.parent = parent

            # Propagate the change:
            for func in MathObj.propa_rules:
                parent.queue += [dict(value = r['value'],
                    ref = parent, path=r['path']) for r in func(child, parent)]




class MathType(MyEnum):
    """
    All MathObj should have a type belonging to this enum
    But, since we're inventing, sometimes you can just use strings
    """
    PL_FORMULA = auto()
    PL_RULE_ANNOTATION = auto()
    PL_PROOF_LINE = auto()
    PL_CONNECTION = auto()
    PL_PROOF = auto()
    PL_THEOREM = auto()
    PL_TRUTH = auto()


class Error(Exception):
    """Base class for exceptions in this module."""
    pass


class PathUpError(Error):
    def __init__(self, ref, path, message='Error while traversing up path.'):
        self.message = message
        self.ref = ref
        self.path = path


class PathDownError(Error):
    def __init__(self, ref, path, message='Error while traversing down path.'):
        self.message = message
        self.ref = ref
        self.path = path
