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
    """
    new_nodes = []
    role = child.role
    val = child.value
    pl_cons_set = set(list(PlCons))

    if role == 'type':
        if val == {MathType.PL_FORMULA}:
            new_nodes += [(MathObj( role='cons', value=pl_cons_set ), '')]

    elif role == 'cons':
        if val == {PlCons.ATOM}:
            # Atoms have texts
            new_nodes += [( MathObj( role='text', value={KSet.UNKNOWN} ), '')]

        elif val == {PlCons.NEGATION}:
            # Negations have bodies typed formula
            new_nodes += [(MathObj( role='body' ), '')]
            new_nodes += [(MathObj( role='type', value={MathType.PL_FORMULA} ), 'body')]
    elif role == 'text':
        if len(val) == 1 and type(list(val)[0]) is str:
            grandpa = parent.parent
            the_text = list(val)[0]
            if grandpa:
                if grandpa.get('cons').value == {PlCons.NEGATION}:
                    new_nodes += [(MathObj( role='text', value={'(~{})'.format(the_text)} ), '..')]

    return new_nodes



# Other things:
def ass_pl(form):
    return form.type == MathType.PL_FORMULA
