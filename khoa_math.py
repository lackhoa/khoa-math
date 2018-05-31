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
    containing <role>, <value> <reference point>, and <path> (in UNIX style).
    The intended action is attaching the node to the parent indicated by
    'path' from 'reference point'

    Mental note: 'type' can be reduced to just a value: an object has type A if its children
    with role 'type' has value A. If we can replace two concepts with one, do it.
    """


    # Class variables
    separator = '.'
    propa_rules = []


    def __init__(self, id_='', role: str='root', value: Set=None):
        """
        :param id: How you want to call this node (unimportant,mainly for roots).
        """
        self.id = id_
        self._role = role
        self._value = value
        self.parent = None  # We don't attach nodes willy-nilly, see 'kattach' for more
        self._queue = []


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
    def queue(self, item):
        self.root._queue = item

    def __repr__(self):
        val = str(self.value) if self.value else ''
        return '{}{}|{}'.format(self.role, self.id, val)

    def _pre_attach(self, parent):
        assert(parent.value == None), 'You cannot attach to a composite object.'


    # 'Real' code:
    def get(self, role: str):
        """Get an attribute of a math object."""
        list = [n for n in self.children if n.role == role]

        assert(len(list) <= 1),\
            'Many nodes with the same role detected for {}'.format(role)

        if list: return list[0]
        else: return None

    def is_inconsistent(self) -> bool:
        """
        A Math Object is 'inconsistent' either when its value is empty,
        or when one of its children is inconsistent.
        """

        # Simply search for any node that have empty value
        if self.value is not None: return self.value == set()
        else:
            for child in self.children:
                if child.is_inconsistent(): return True
            return False


    def is_complete(self) -> bool:
        """
        An object is complete when:
        1) its queue is empty, and
        2) its value is a singleton or all of is children are complete.
        """
        res = False
        if not self.queue:
            if self.value: res = (len(self.value) == 1)
            else:
                for child in self.children:
                    if not child.is_complete(): break
                else: res = True  # For-Else clause usage here

        return res

    def clone(self):
        """Return a deep copy of this object."""
        # Make a new math object
        res = MathObj(role=self.role, value=self.value)

        # About the queue (Yikes!):
        # Take care of queue items with this node as the reference
        for q in self.queue:
            if q['ref'] == self:
                res.queue += [dict(role=q['role'],
                    value=q['value'],
                    ref=res,
                    path=q['path'])]

        # Clone all children and nattach to the result
        # Note that the queue items that reference the children
        # are already handled by `nattach`
        for child in self.children:
            child_clone = child.clone()
            MathObj.nattach(child_clone, res)

        return res


    @staticmethod
    def nattach(child, parent=None, overwrite=True):
        """
        'Normal attach': attaching nodes, in a straightforward way that cares about roles.
        Please don't invoke the API's normal way to attach nodes. Use either this or `kattach`

        :param overwrite: If set to True, if there is already another node with the same role,
        delete that node and attach the argument instead. If set to False, don't do anything.
        """
        if parent is not None:
            assert(type(child) == MathObj), 'You can only nattach Math Objects!'
            assert(type(parent) == MathObj), 'You can only nattach to Math Objects!'

            same = parent.get(child.role)
            if same:
                if overwrite:  # If a node with the same role is present
                    parent.queue.extend(child.queue)  # Preserve child's queue items
                    same.parent = None  # Remove the same-role node
                    child.parent = parent  # Attach the new node
            else:
                # Do things normally here:
                parent.queue.extend(child.queue)  # Preserve child's queue items
                child.parent = parent


    @staticmethod
    def kattach(child: Dict, parent=None):
        """
        Like `nattach`, but adds new knowledge to the queue,
        and intended for single node only.

        :param child: A dictionary with role and value (like in a node).
        Why is it not a MathObj? Because MathObj can have child.
        """
        if parent is not None:
            assert(type(parent) == MathObj), 'You can only kattach to Math Objects!'

            same = parent.get(child['role'])
            if same:  # If a node with the same role is present
                if same.value:  # Only do work when it is a leaf
                    unified = unify(child['value'], same.value)
                    if unified != same.value:  # Did we learn something new?
                        same._value = unified
                        # Propagate the change:
                        for func in MathObj.propa_rules:
                            parent.queue += [dict(role = r['role'], value = r['value'],
                                ref = parent, path = r['path']) for r in func(child, parent)]
            else:
                # Convert child to MathObj representation, and add it to parent
                child_obj = MathObj(role=child['role'], value=child['value'])
                child_obj.parent = parent

                # Propagate the change:
                for func in MathObj.propa_rules:
                    parent.queue += [dict(role = r['role'], value = r['value'],
                        ref = parent, path = r['path']) for r in func(child, parent)]


    @staticmethod
    def path_resolve(ref, path: str):
        """Return the node by the path from the reference."""
        assert(type(ref) == MathObj), 'Reference must be MathObj!'
        path = path.split('/')
        res = ref

        # Process the path UNIX style:
        for n in path:
            if n == '': continue
            elif n == '..':
                if not res: raise Exception('Path cannot be resolved')
                else: res = res.parent
            else:
                if not res: raise Exception('Path cannot be resolved')
                else: res = res.get(n)

        return res


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
