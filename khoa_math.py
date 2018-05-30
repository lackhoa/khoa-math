from kset import *

from enum import Enum, auto
from typing import List, Set, Callable
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

    About propa_rules: these are functions that takes a (child, parent) tuple
    (which signifies their attachment) and return a list of queue items,
    minus the reference point, since it is defaulted to be the parent of the attachment.

    Mental note: 'type' can be reduced to just a value: an object has type A if its children
    with role 'type' has value A. If we can replace two concepts with one, do it.
    """


    # Class variables
    separator = '.'
    propa_rules = []


    def __init__(self, id_='', role: str='root', value: Set=None,
            parent=None):
        """
        :param queue: The queue is for new knowledge. Queue elements are written
        in the form (<node>, <reference point>, <path>) The path is written in UNIX style.
        The intended action is attaching the node to the parent indicated by
        'path' from 'reference point'

        :param id: How you want to call this node in your program (mainly for roots).
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
        # First take care of queue items with this node as the reference
        for node, ref, path in self.queue:
            if ref == self:
                res.queue += [(node.clone(), res, path)]

        # Clone all children and nattach to this
        for child in self.children:
            child_clone = child.clone()
            MathObj.nattach(child_clone, res)
            # Don't forget the queue items that references the children!
            for node, ref, path in self.queue:
                if ref == child:
                    queue_clone += [(node.clone(), child_clone, path)]

        return res


    @staticmethod
    def nattach(child, parent=None):
        """
        'Normal attach':This is the gateway to changing the tree: by attaching nodes.
        Please don't invoke the API's normal way to attach nodes. Use either this or `kattach`
        """
        if parent is not None:
            assert(type(child) == MathObj), 'You can only nattach Math Objects!'
            assert(type(parent) == MathObj), 'You can only nattach to Math Objects!'

            same = parent.get(child.role)
            if same:  # If a node with the same role is present
                if same.value:  # Only do work when the value is present
                    unified = unify(child.value, same.value)
                    same._value = unified
            else:
                # Do things normally here:
                child.parent = parent


    @staticmethod
    def kattach(child, parent=None):
        """Like `nattach`, but adds new knowledge to the queue"""
        if parent is not None:
            assert(type(child) == MathObj), 'You can only kattach Math Objects!'
            assert(type(parent) == MathObj), 'You can only kattach to Math Objects!'

            same = parent.get(child.role)
            if same:  # If a node with the same role is present
                if same.value:  # Only do work when the value is present
                    unified = unify(child.value, same.value)
                    if unified != same.value:  # Did we learn something new?
                        same._value = unified
                        MathObj._propagate_change(same, parent)
            else:
                # Do things normally here:
                child.parent = parent
                MathObj._propagate_change(child, parent)


    @staticmethod
    def _propagate_change(child, parent):
        """
        Method called after attaching child to parent, this is the heart of the machine.
        This method will populate the root's queue. If you want to change this method, add
        items to the class variable `propa_rules`
        """
        for func in MathObj.propa_rules:  # Note that we use the class variable
            returned = func(child, parent)
            queue_items = [(r[0], parent, r[1]) for r in returned]
            child.queue += queue_items


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
