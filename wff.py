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
            new_nodes += [dict(value=pl_cons_set, path='cons')]

    elif role == 'text':
        # This clause takes care of all the text
        if extract(val):
            text1 = extract(val)
            if parent.parent:
                grandpa = parent.parent
                if grandpa.get('cons').value == {PlCons.NEGATION}:
                    # Text of negation
                    new_nodes += [dict(value={'(~{})'.format(text1)}, path='../text')]

                elif grandpa.get('cons').value == {PlCons.CONJUNCTION}:
                    # Text of conjunction
                    switch = (parent.role == 'left')
                    other_role = 'right' if switch else 'left'
                    if extract( grandpa.get('{}/text'.format(other_role) ).value ):
                        text2 = extract( grandpa.get('{}/text'.format(other_role) ).value )
                        left_txt, right_txt = (text1, text2) if switch else (text2, text1)
                        new_nodes += [
                            dict(value={r'({}&{})'.format(left_txt, right_txt)}, path='../text')]

                elif grandpa.get('cons').value == {PlCons.CONDITIONAL}:
                    # Text of conditional
                    switch = (parent.role == 'ante')
                    other_role = 'conse' if switch else 'ante'
                    if extract( grandpa.get('{}/text'.format(other_role) ).value ):
                        text2 = extract( grandpa.get('{}/text'.format(other_role) ).value )
                        ante_txt, conse_txt = (text1, text2) if switch else (text2, text1)
                        new_nodes += [
                            dict(value={r'({}->{})'.format(ante_txt, conse_txt)}, path='../text')]

    elif role == 'cons':
        # This clause provides constructors
        if val == {PlCons.ATOM}:
            pass  # Atoms have nothing

        elif val == {PlCons.NEGATION}:
            # Negations have bodies typed formula
            new_nodes += [dict(value=None, path='body')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='body/type')]

        elif val == {PlCons.CONJUNCTION}:
            # Conjunction has left and right formulas
            new_nodes += [dict(value=None, path='left')]
            new_nodes += [dict(value=None, path='right')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='left/type')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='right/type')]

        elif val == {PlCons.CONDITIONAL}:
            # Conditional has antecedent and consequent
            new_nodes += [dict(value=None, path='ante')]
            new_nodes += [dict(value=None, path='conse')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='ante/type')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='conse/type')]

    return new_nodes
