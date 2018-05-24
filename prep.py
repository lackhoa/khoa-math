from khoa_math import *
from typing import Dict, Iterable
from itertools import product

# This file contains definitions of constructs in Prepositional Logic

class PlCons(AutoName):
    ATOM = auto()
    NEGATION = auto()
    CONJUNCTION = auto()
    DISJUNCTION = auto()
    CONDITIONAL = auto()
    BICONDITIONAL = auto()

def atom(text=''):
    '''
    Create an atomic pl formula
    :param text: (optional) English description of what the formula says
    '''
    p = MathObject(MathType.PL_FORMULA)
    p.cons = PlCons.ATOM
    p.text = text
    return p

def neg_assert(in_form, out_form):
    in_explicit = None
    out_explicit = None
    in_qualifier = None
    out_qualifier = None

    if in_form is unknown:
        out_qualifier = lambda x: x.type == MathType.PL_FORMULA and x.cons == PlCons.NEGATION
    else:
        out_explicit = {neg(in_form)}

    if out_form is unknown:
        in_qualifier = lambda x: x.type == MathType.PL_FORMULA
    else:
        in_explicit = lambda x: x.type == MathType.PL_FORMULA and x.cons == out_form.form

    return [my_set(in_explicit, in_qualifier), my_set(out_explicit, out_qualifier)]

def neg(body):
    '''
    Create a negation of a formula
    '''
    p = MathObject(MathType.PL_FORMULA)
    p.cons = PlCons.NEGATION
    p.body = body
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




# Utility function
def ass_pl(form):
    return form.type == MathType.PL_FORMULA