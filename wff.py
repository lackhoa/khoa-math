from khoa_math import *
from typing import Dict, Iterable

# This file contains definitions of constructs of Well Formed Formulas

class PlCons(MyEnum):
    ATOM = auto()
    NEGATION = auto()
    CONJUNCTION = auto()
    DISJUNCTION = auto()
    CONDITIONAL = auto()
    BICONDITIONAL = auto()


def wff_rules(child, parent):
    """
    Default propagation rules for well-formed formulas.
    Just so you know, the queue element is written in the form (<node>, <refrence point>, <path>)
    The path is written in UNIX style
    """
    new_nodes = []
    role = child.role
    val = child.value
    pl_cons_set = set(list(PlCons))

    if role == 'type':
        if val == {MathType.PL_FORMULA}:
            new_nodes += [(MathObj(role='cons', value=pl_cons_set), parent, '')]

    elif role == 'cons':
        if val == {PlCons.ATOM}:
            # Atoms have texts
            new_nodes += [( MathObj( role='text', value={KSet.UNKNOWN}), parent, '')]

        elif val == {PlCons.NEGATION}:
            # Negations have bodies typed formula
            new_nodes += [(MathObj(role='body'), parent, '')]
            new_nodes += [(MathObj(role='type', value={MathType.PL_FORMULA},)
                , parent, 'body')]

    return new_nodes



# Other things:
def ass_pl(form):
    return form.type == MathType.PL_FORMULA
