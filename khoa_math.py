from kset import *

from enum import Enum, auto
from anytree import Anynode, RenderTree

# This file contains the basis of mathematics

class MathObject(NodeMixin):
    '''
    This class is the base for all mathematical objects, that's why it doesn't do anything
    Most math objects are recursive, that's why they should be trees.

    Math Objects are UNKNOWN and 'invalid' by default, to become 'valid',
    they must be checked by a validating routine.

    The "content" of a Math Object can be described by either a single 'value'
    attribute (then we call it 'atomic'), or by many MathObject as children
    (then we call it 'composite'). Each child node has its role.

    In this knowledge model, everything is a possibility, that's why all values must be
    a KSET. This is consistent with the paragraph above since knowledge sets can only
    contain data.

    A Math Object is 'grounded' either when its value is explicit, or when all of its children
    are grounded.

    A Math Object is 'nailed' either when its value contains only a single item, or when all
    of its children are nailed. (that was super made up!)

    Mental note: only none-tree (non-math) attributes can be accessed with the dot notation
    (the only exception is 'parent', because it cannot be a subtree)

    Mental note: We can override __attach later if needed.

    Mental note: value is the only attribute that can affect the state of the tree
    '''
    separator = '.'

    def __init__(self, role: str=None, value=None, parent=None):
        self.parent = parent  # The only tree attribute we need

    def __eq__(self, other):
        """
        Overrides the default implementation
        Compare the attributes of the object rather than the IDs
        """
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        else: return False

    def __repr__(self):
        return self.text

    # Real code:
    def get(self, role):
        list = [n for n in self.children if n.role == 'role']
        assert(len(list) <= 1),\
            'Many nodes with the same role detected for {}'.format(role)

        if list: return list[0]
        else: return None


    def add_knowledge(self, kset_):
        '''
        For atomic objects only.
        
        First we detach this node, and then we re-attach a better version,
        to make some noise for the attach/detach protocol.
        
        If parent is None, the notification protocol won't work, but it doesn't matter
        because there should be no change to the rest of the system.
        '''
        self.value = unify(self.value, kset_)
        old_parent = self.parent
        self.parent = None
        self.parent = old_parent  # Tada! Same parent!










# Awesome class to name Enums
class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class MathType(AutoName):
    '''
    All MathObject should have a type belonging to this enum
    But, since we're inventing, sometimes you can just use strings
    '''
    PL_FORMULA = auto()
    PL_RULE_ANNOTATION = auto()
    PL_PROOF_LINE = auto()
    PL_CONNECTION = auto()
    PL_PROOF = auto()
    PL_THEOREM = auto()
    PL_TRUTH = auto()
    KSET = auto()
    UNKNOWN = auto()