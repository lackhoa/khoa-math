from kset import *

from enum import Enum, auto
from typing import List, Set
from anytree import NodeMixin, RenderTree, find_by_attr

# This file contains the basis of mathematics

class MathObj(NodeMixin):
    """
    This class is the base for all mathematical objects, that's why it doesn't do anything
    Most math objects are recursive, that's why they should be trees.

    Math Objects are UNKNOWN and 'invalid' by default, to become 'valid',
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

    :param queue: The queue is for new knowledge. All children inherit the queue from the root. Items
    in the queues are formatted as tuples with the node on the left and the parent on the right.

    :param propa_rules: The queue is populated using propagation rules, which are also shared by the root.

    :param id: How you want to call this thing in your program.

    Note that the tree NEVER adds new nodes on its own. The user controls everything.

    Mental note: 'type' can be reduced to just a value: an object has type A if its children
    with role 'type' has value A. Simplistic is the goal here.
    """
    separator = '.'

    def __init__(self, id_='', role: str='root', value: Set=None,\
            parent=None, queue: List=[], propa_rules: List=[]):
        self.id = id_
        self.role = role
        self.value = value
        self.parent = parent  # The only tree attribute we need
        self.queue = queue
        self.propa_rules = propa_rules

    def __repr__(self):
        txt = self.get('text') if self.get('text') else ''
        val = self.value if self.value else ''
        return '{}|{}|{}|{}'.format(self.role, txt, val, self.id)

    def _pre_attach(self, parent):
        assert(parent.value == None), 'You cannot attach to a composite object.'

    # Real code:
    def get(self, role: str):
        """Get an attribute of a math object."""
        list = [n for n in self.children if n.role == role]
        assert(len(list) <= 1),\
            'Many nodes with the same role detected for {}'.format(role)

        if list: return list[0]
        else: return None

    def is_inconsistent(self):
        # Simply search for any nodes that have empty value
        return find_by_attr(node=self, name='value', value=set())

    def add_rule(self, rule):
        """Add a propagation rule (root node exclusive)"""
        assert(self.parent is None), 'Please don\'t add rules to non-root!'
        self.propa_rules += [rule]

    def clone(self):
        """Return a deep copy of this object."""
        # Clone everything except parents and children
        res = MathObj(role=self.role, value=self.value,\
                parent=None, propa_rules=self.propa_rules)

        # About the queue (Ew!):
        queue_clone = []
        for child, parent in self.queue:
            if parent == self: queue_clone += [(child, res)]

        # Clone all children and attach to this
        for child in self.children:
            child_clone = child.clone()
            child_clone.parent = res
            # Don't forget the queue!
            for c, parent in self.queue:
                if parent == child: queue_clone += [(c, child_clone)]

        res.queue = queue_clone
        return res

    def kattach(self, p=None):
        """
        This is the gateway to changing the tree: by attaching nodes.
        """
        if p is not None:
            assert(type(p) == MathObj), 'You can only kattach to Math Objects!'
            same = p.get(self.role)
            if same:  # If a node with the same role is present
                unified = unify(self.value, same.value)
                if unified != same.value:  # Did we learn something new?
                    same.value = unified
                    same._propagate_change(same, p)
            else:
                # Do things normally here:
                self.parent = p
                self.queue = p.queue  # queue inheritance
                self.propa_rules = p.propa_rules  # propagation rules inheritance
                self._propagate_change(self, p)  # Warning: this line relies on propagation rules

    def _propagate_change(self, child, p):
        """
        Method called by the leaf after attaching to a parent, this is the heart of the machine.
        This will populate the tree queue with (node, parent) tuples.
        """
        for func in self.propa_rules:
            func(child, p)

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
