from kset import *

from enum import Enum, auto
from typing import List, Set
from anytree import NodeMixin, RenderTree

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

    A Math Object is 'grounded' either when its value is exclusive, or when all of its children
    are grounded.

    A Math Object is 'nailed' either when its value contains only a single item, or when all
    of its children are nailed. (that was super made up!)

    The queue is for new knowledge. All children share the same queue with the root. Items
    in the queues are formatted as tuples with the node on the left and the parent on the right.

    Mental note: 'type' can be reduced to just a value: an object has type A if its children
    with role 'type' has value A. Simplistic is the goal here.
    """
    separator = '.'

    def __init__(self, role: str=None, value: Set=None, parent=None, queue: List=None):
        self.role = role
        self.value = value
        self.parent = parent  # The only tree attribute we need
        self.queue = queue

    def __eq__(self, other):
        """
        Compare the attributes of the object rather than the IDs
        """
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        else: return False

    def __repr__(self):
        return self.text

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
                    MathObj._propagate_change(same, p)
            else:
                # Do things normally here:
                self.queue = p.queue  # queue inheritance
                self.parent = p
                MathObj._propagate_change(self, p)

    def _propagate_change(child, p):
        """
        Method called by the leaf after attaching to a parent, this is the heart of the machine.
        This will populate the tree queue with (node, parent) tuples.
        """
        role = child.role
        val = child.value
        pl_cons_set = kset(list(PlCons))
        math_type_formula_set = kset({MathType.PL_FORMULA})

        if role == 'type':
            if val == {MathType.PL_FORMULA}:
                child.queue += [( MathObj(role='cons', value=pl_cons_set, parent=None), p )]

        elif role == 'cons':
            if child.value == {PlCons.ATOM}:
                # Atoms have texts
                child.queue += [( MathObj( role='text', value=kset(), parent=None), p )]

            elif child.value == {PlCons.NEGATION}:
                # Negations have bodies typed formula
                child.queue += [( MathObj(role='body', parent=None), p )]
                child.queue += [( MathObj(role='type', value=math_type_formula_set,\
                        parent=None), p.get('body') )]



# Awesome class to name Enums
class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

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
