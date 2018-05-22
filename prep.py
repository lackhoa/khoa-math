from khoa_math import *
from typing import Dict, Iterable
from itertools import product

# This file contains definitions of constructs in Prepositional Logic

class PlCons(Enum):
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

def neg(form):
    '''
    Create a negation of a formula
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




# Utility function
def ass_pl(form):
    assert(form.type == MathType.PL_FORMULA)

def unknown_form(type):
    return MathObject(type)

class my_set:
    def __init__(explicit: Iterable=None, qualifier: Callable[..., bool]=None):
        assert( bool(explicit) != bool(qualifier) ), 'You cannot supply both!'

        if explicit:
            # You can derive the qualifier from the explicit
            self.qualifier = lambda j: j in explicit

        # You can also derive the explicit if the qualifier is False
        if qualifier == False:
            self.explicit = set()

        self.explicit = explicit
        self.qualifier = qualifier

def update_unknown_form(unknown, attr, value):
    assert(attr in unknown.attrs)
    if attr == 'cons':
        if value == 'atom':
            unknown.cons = 'atom'
            unknown.text = my_set(qualifier = True)
        elif value == 'conj':
            unknown.cons = 'conj'
            unknown.left.narrow(qualifier = lambda l: l.type == PL_FORMULA))
            unknown.right = my_set(qualifier = lambda t: t.type == PL_FORMULA)
            def no_name():
                if unknown.left is known and unknown.right is known:
                    return conj(left, right)
                else: return
            unknown.value = my_set(qualifier = no_name)
        elif value == 'cond':
            unknown.cons = 'cond'
            unknown.ante = Any
            unknown.conse = Any





def enumerate(atoms):
    level1 = [atoms, conj]
    queue = level1

    while True:
        tmp_queue = []
        for u in queue:
            if u.type == PL_FORMULA:
                print(u)
            else:
                pools = map(universe, u.inputs)
                prod = product(pools)

                for p in prod:
                    tmp_queue.append(p)

        queue.extend(tmp_queue)