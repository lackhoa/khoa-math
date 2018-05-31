from khoa_math import *
from kset import *
from typing import Dict, Iterable

# This file contains definitions of constructs of Well Formed Formulas

class PlCons(MyEnum):
    ATOM = auto()
    NEGATION = auto()
    CONJUNCTION = auto()
    DISJUNCTION = auto()
    CONDITIONAL = auto()
    BICONDITIONAL = auto()


def extract(val):
    if len(val) == 1 and val != {KSet.UNKNOWN}:
        return list(val)[0]
    else: return None


def wff_rules(child, parent):
    """
    Default propagation rules for well-formed formulas.
    """
    new_nodes = []
    role = child['role']
    val = child['value']
    pl_cons_set = set(list(PlCons))

    if role == 'type':
        # This clause takes care of listing constructors for types:
        if val == {MathType.PL_FORMULA}:
            new_nodes += [dict(role='cons', value=pl_cons_set, path='')]

    elif role == 'text':
        # This clause takes care of all the text
        if extract(val):
            text1 = extract(val)
            if parent.parent:
                grandpa = parent.parent
                if grandpa.get('cons').value == {PlCons.NEGATION}:
                    new_nodes += [dict(role='text', value={'(~{})'.format(text1)}, path='..')]

                elif grandpa.get('cons').value == {PlCons.CONJUNCTION}:
                    other_role = 'right' if (parent.role == 'left') else 'left'
                    if extract( grandpa.get(other_role).get('text').value ):
                        text2 = extract( grandpa.get(other_role).get('text').value )
                        if other_role == 'right':
                            new_nodes += [dict(role='text',
                                value={r'({}&{})'.format(text1, text2)}, path='..')]
                        else:
                            new_nodes += [dict(role='text',
                                value={r'({}&{})'.format(text2, text1)}, path='..')]

    elif role == 'cons':
        # This clause provides constructors
        if val == {PlCons.ATOM}:
            pass  # Atoms have nothing

        elif val == {PlCons.NEGATION}:
            # Negations have bodies typed formula
            new_nodes += [dict(role='body', value=None, path='')]
            new_nodes += [dict(role='type', value={MathType.PL_FORMULA}, path='body')]

        elif val == {PlCons.CONJUNCTION}:
            # Conjunction has left and right formulas
            new_nodes += [dict(role='left', value=None, path='')]
            new_nodes += [dict(role='right', value=None, path='')]
            new_nodes += [dict(role='type', value={MathType.PL_FORMULA}, path='left')]
            new_nodes += [dict(role='type', value={MathType.PL_FORMULA}, path='right')]

    return new_nodes



# Other things:
def ass_pl(form):
    return form.type == MathType.PL_FORMULA
