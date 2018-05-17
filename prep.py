from enum import Enum, auto
from typing import Dict

# This file contains definitions of constructs in Prepositional Logic

class MathObject:
    '''
    This class is the base for all mathematical objects, that's why it doesn't do anything
    '''
    def __init__(self):
        # The text acts like an identication to compare objects
        self.text = ''
        self.type = '' # If important, the type should be a value in MathType
    def __eq__(self, other):
        """
        Overrides the default implementation
        Compare the attributes of the object rather than the IDs
        """
        if isinstance(self, other.__class__):
            return self.text == other.text
        return False

    def __repr__(self):
        return self.text

class MathType(Enum):
    PL_FORMULA = auto()
    PL_RULE_ANNOTATION = auto()
    PL_PROOF_LINE = auto()
    PL_CONNECTION = auto()

class Truth(Enum):
    TRUE = True
    FALSE = False
    UNKNOWN = None

class PlCons(Enum):
    ATOM = auto()
    NEGATION = auto()
    CONJUNCTION = auto()
    DISJUNCTION = auto()
    CONDITIONAL = auto()
    BICONDITIONAL = auto()

def ass_pl(form):
    assert(form.type == MathType.PL_FORMULA)

def atom(text=''):
    '''
    Create an atomic pl formula
    :param text: (optional) English description of what the formula says
    '''
    p = MathObject()
    p.type = MathType.PL_FORMULA
    p.cons = PlCons.ATOM
    p.text = text # It's official: the text works as identification for a sentence now
    return p

def neg(form):
    '''
    Create a negattion of a formula
    '''
    ass_pl(form)
    p = MathObject()
    p.type = MathType.PL_FORMULA
    p.cons = PlCons.NEGATION
    p.form = form
    p.text = '(~{})'.format(form.text)
    return p

def conj(left, right):
    '''
    Create a conjunction
    '''
    ass_pl(left)
    ass_pl(right)
    p = MathObject()
    p.type = MathType.PL_FORMULA
    p.cons = PlCons.CONJUNCTION
    p.left = left
    p.right = right
    p.text = '({} /\ {})'.format(left.text, right.text)
    return p

def disj(left, right):
    '''
    Create a disjunction
    '''
    ass_pl(left)
    ass_pl(right)
    p = MathObject()
    p.type = MathType.PL_FORMULA
    p.cons = PlCons.DISJUNCTION
    p.left = left
    p.right = right
    p.text = '({} \/ {})'.format(left.text, right.text)
    return p

def cond(ante, conse):
    '''
    Create a conditional
    '''
    ass_pl(ante)
    ass_pl(conse)

    p = MathObject()
    p.type = MathType.PL_FORMULA
    p.cons = PlCons.CONDITIONAL
    p.ante = ante
    p.conse = conse
    p.text = '({} -> {})'.format(ante.text, conse.text)
    return p

def bicond(left, right):
    '''
    Create a biconditional
    '''
    ass_pl(left)
    ass_pl(right)

    p = MathObject()
    p.type = MathType.PL_FORMULA
    p.cons = PlCons.BICONDITIONAL
    p.left = left
    p.right = right
    p.text = '({} <-> {})'.format(left.text, right.text)
    return p

# Sequent
def sequent(conclusion, *premises):
    ass_pl(conclusion)
    for premise in premises:
        ass_pl(premise)
    result = MathObject()
    result.conclusion = conclusion
    result.premises = premises
    return result

