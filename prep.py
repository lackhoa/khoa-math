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

def prep_propagate(child, p):
    """
    Default propagation rules for well-formed formulas.
    """
    role = child.role
    val = child.value
    pl_cons_set = set(list(PlCons))

    if role == 'type':
        if val == {MathType.PL_FORMULA}:
            child.queue += [( MathObj(role='cons', value=pl_cons_set, parent=None), p )]

    elif role == 'cons':
        if child.value == {PlCons.ATOM}:
            # Atoms have texts
            child.queue += [( MathObj( role='text', value={None}, parent=None), p )]

        elif child.value == {PlCons.NEGATION}:
            # Negations have bodies typed formula
            child.queue += [( MathObj(role='body', parent=None), p )]
            child.queue += [( MathObj(role='type', value={MathType.PL_FORMULA},\
                    parent=None), p.get('body') )]

    elif role == 'text':
        




# Utility function
def ass_pl(form):
    return form.type == MathType.PL_FORMULA
