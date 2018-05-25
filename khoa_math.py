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

        Every change in the system must go through the method _post_attach,
        which is why we want to detach and re-attach the node if it changes
        '''
        assert(self.value is not None), 'Cannot add knowledge to a composite object!'
        old_value = self.value
        self.value = unify(self.value, kset_)

        if self.value != old_value:
            old_parent = self.parent
            self.parent = None
            self.parent = old_parent  # Tada! Same parent!

    'Overridden because I need same-role handling'
    @parent.setter
    def parent(self, p):
        if p is not None and not isinstance(p, NodeMixin):
            msg = "Parent node %r is not of type 'NodeMixin'." % (p)
            raise TreeError(msg)
        try:
            parent = self.__parent
        except AttributeError:
            parent = None
        # BOOKMARKED! I WAS HERE!
        # if parent is not p:  # Condition removed
        self.__check_loop(p)
        self.__detach(parent)
        self.__attach(p)


    def _post_attach(self, parent):
        """Method call after attaching to `parent`."""
        queue = []

        role = self.role
        if role == 'type':
            if self.value == kset({MathType.PL_FORMULA}):
                if not parent.get('cons'):
                    MathObject(role='cons', value=kset(), parent=parent)
                parent.get('cons').add_knowledge( kset(list(PlCons)) )
        elif role == 'cons':
            if self.value == kset({PlCons.ATOM}):
                # Atoms have texts
                if not parent.get('text'):
                    MathObject(role='text', value=kset(), parent=parent)
            elif self.value == kset({PlCons.NEGATION}):
                # Negations have bodies typed formula
                if not parent.get('body'):
                    MathObject(role='body', value=kset(), parent=parent)

                MathObject(role='type', value=kset({PL_FORMULA}), parent=parent.get('body'))
            elif self.value == kset({PlCons.CONJUNCTION}):
                # Conjunctions have left and right typed formula
                if not parent.get('left'):
                    MathObject(role='left', value=kset(), parent=parent)
                MathObject(role='type', value=kset({PL_FORMULA}), parent=parent.get('left'))

                if not parent.get('right'):
                    MathObject(role='right', value=kset(), parent=parent)
                MathObject(role='type', value=kset({PL_FORMULA}), parent=parent.get('right'))




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