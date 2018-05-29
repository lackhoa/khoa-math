from kset import *

from enum import Enum, auto
from typing import List, Set, Callable
from anytree import NodeMixin, RenderTree, find_by_attr

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

    A Math Object is 'inconsistent' either when its value is empty, or when one of its
    children is inconsistent.

    Note that the tree NEVER adds new nodes on its own. The user controls everything.

    Mental note: 'type' can be reduced to just a value: an object has type A if its children
    with role 'type' has value A. If we can replace two concepts with one, do it.
    """
    # Class variables
    separator = '.'
    propa_rules = []

    def __init__(self, id_='', role: str='root', value: Set=None,
            parent=None):
        """
        :param queue: The queue is for new knowledge. All children inherit the queue from the root. Items
        in the queues are formatted as tuples with the node on the left and the parent on the right.

        :param id: How you want to call this node in your program (mainly for roots).
        """
        self.id = id_
        self.__role = role
        self.__value = value
        self.parent = None  # We don't attach nodes willy-nilly, see 'kattach' for more
        self.__queue = []
        self.__root = self

    @property
    def role(self):
        return self.__role

    @property
    def value(self):
        return self.__value
    def clear_val(self):
        """Clear all values in the node except for UNKNOWN"""
        self.__value = {KSet.UNKNOWN} if KSet.UNKNOWN in self.value else set()

    @property
    def root(self):
        return self.__root

    @property
    def queue(self):
        return self.root.__queue  # The root manages the queue
    @queue.setter
    def queue(self, item):
        self.root.__queue = item

    def __repr__(self):
        txt = self.get('text') if self.get('text') else ''
        val = self.value if self.value else ''
        return '{}|{}|{}|{}'.format(self.role, txt, val, self.id)

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
        # Simply search for any node that have empty value
        return bool( find_by_attr(node=self, name='value', value=set()) )

    def clone(self):
        """Return a deep copy of this object."""
        # Make a new math object
        res = MathObj(role=self.role, value=self.value)

        # About the queue (Yikes!):
        # First take care of queue items with this node as the parent
        for child, parent in self.queue:
            if parent == self: res.queue += [(child.clone(), res)]

        # Clone all children and attach to this
        for child in self.children:
            child_clone = child.clone()
            child_clone.parent = res
            # Don't forget the queue items to attach to the cloned children!
            for c, p in self.queue:
                if p == child: queue_clone += [(c.clone(), child_clone)]

        return res

    @staticmethod
    def kattach(child, parent=None):
        """
        This is the gateway to changing the tree: by attaching nodes.
        """
        if parent is not None:
            assert(type(child) == MathObj), 'You can only kattach Math Objects!'
            assert(type(parent) == MathObj), 'You can only kattach to Math Objects!'

            same = parent.get(child.role)
            if same:  # If a node with the same role is present
                unified = unify(child.value, same.value)
                if unified != same.value:  # Did we learn something new?
                    same.__value = unified
                    MathObj._propagate_change(same, parent)
            else:
                # Do things normally here:
                child.parent = parent
                child.__root = parent.root
                MathObj._propagate_change(child, parent)

    @staticmethod
    def _propagate_change(child, parent):
        """
        Method called after attaching child to parent, this is the heart of the machine.
        This will populate the tree queue with (node, parent) tuples.
        """
        for func in MathObj.propa_rules:  # Note that we use the class variable
            func(child, parent)

class MathType(AutoName):
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
    KSET = auto()
    UNKNOWN = auto()
