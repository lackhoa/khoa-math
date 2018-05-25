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
    '''
    def __init__(self, role=None, value=None, parent=None):
        self.parent = parent  # The only tree feature we need

    def __eq__(self, other):
        """
        Overrides the default implementation
        Compare the attributes of the object rather than the IDs
        """
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        else: return False

    def __hash__(self):
        '''
        We vow that MathObjects will never change once they're created
        '''
        return id(self)

    def __repr__(self):
        return self.text

    # Real code:
    def add_knowledge()

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