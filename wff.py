from khoa_math import *
from typing import Dict, Iterable

# This file contains definitions of constructs of Well Formed Formulas

class PlCons(AutoName):
    ATOM = auto()
    NEGATION = auto()
    CONJUNCTION = auto()
    DISJUNCTION = auto()
    CONDITIONAL = auto()
    BICONDITIONAL = auto()

def wff_rules(child, p):
    """
    Default propagation rules for well-formed formulas.
    """
    role = child.role
    val = child.value
    pl_cons_set = set(list(PlCons))

    if role == 'type':
        if val == {MathType.PL_FORMULA}:
            child.queue += [( MathObj(role='cons', value=pl_cons_set), p )]

    elif role == 'cons':
        if val == {PlCons.ATOM}:
            # Atoms have texts
            child.queue += [( MathObj( role='text', value={None}), p )]

        elif val == {PlCons.NEGATION}:
            # Negations have bodies typed formula
            child.queue += [( MathObj(role='body'), p )]
            child.queue += [( MathObj(role='type', value={MathType.PL_FORMULA},)
                , p.get('body') )]




# Other things:
def ass_pl(form):
    return form.type == MathType.PL_FORMULA
