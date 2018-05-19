from enum import Enum, auto
from typing import Dict

# This file contains definitions of constructs in Prepositional Logic

class MathObject():
    '''
    This class is the base for all mathematical objects, that's why it doesn't do anything
    '''
    def __init__(self, type_, text: str = ''):
        assert(type(type_) == MathType)
        self.text = text
        self.type = type_
    def __eq__(self, other):
        """
        Overrides the default implementation
        Compare the attributes of the object rather than the IDs
        """
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return self.text

class MathType(Enum):
    PL_FORMULA = auto()
    PL_RULE_ANNOTATION = auto()
    PL_PROOF_LINE = auto()
    PL_CONNECTION = auto()
    PL_PROOF = auto()

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
    p = MathObject(MathType.PL_FORMULA)
    p.cons = PlCons.ATOM
    p.text = text
    return p

def neg(form):
    '''
    Create a negattion of a formula
    '''
    ass_pl(form)
    p = MathObject(MathType.PL_FORMULA)
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
    p = MathObject(MathType.PL_FORMULA)
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
    p = MathObject(MathType.PL_FORMULA)
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

    p = MathObject(MathType.PL_FORMULA)
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

    p = MathObject(MathType.PL_FORMULA)
    p.cons = PlCons.BICONDITIONAL
    p.left = left
    p.right = right
    p.text = '({} <-> {})'.format(left.text, right.text)
    return p
