from khoa_math import MathType
from misc import MyEnum

from enum import auto
from typing import Dict, Iterable

# This file contains the definitions Well Formed Formulas

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


def wff_str(obj):
    """Print out well-formed-formulas"""
    res = ''

    if obj.get('type').value == {MathType.PL_FORMULA}:
        cons = obj.get('cons').value
        if cons == {PlCons.ATOM}:
            res = list(obj.get('text').value)[0]

        elif cons == {PlCons.NEGATION}:
            res = '(~{})'.format( wff_str(obj.get('body')) )

        elif cons == {PlCons.CONJUNCTION}:
            res = '({}&{})'.format( wff_str(obj.get('left_f')), wff_str(obj.get('right_f')) )

        elif cons == {PlCons.CONDITIONAL}:
            res = '({}->{})'.format( wff_str(obj.get('ante')), wff_str(obj.get('conse')) )

        elif cons == {PlCons.DISJUNCTION}:
            res = '({}v{})'.format( wff_str(obj.get('left_f')), wff_str(obj.get('right_f')) )

        elif cons == {PlCons.BICONDITIONAL}:
            res = '({}<->{})'.format( wff_str(obj.get('left_f')), wff_str(obj.get('right_f')) )

    return res


def wff_rules(child, parent):
    """
    Default propagation rules for well-formed formulas.
    """
    new_nodes = []
    role = child['role']
    val = child['value']

    if role == 'type':
        # This clause lists all constructors for wff
        if val == {MathType.PL_FORMULA}:
            new_nodes += [dict(value=set(list(PlCons)), path='cons')]

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
            new_nodes += [dict(value=None, path='left_f')]
            new_nodes += [dict(value=None, path='right_f')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='left_f/type')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='right_f/type')]

        elif val == {PlCons.DISJUNCTION}:
            # Disjunction has left and right formulas
            new_nodes += [dict(value=None, path='left_f')]
            new_nodes += [dict(value=None, path='right_f')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='left_f/type')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='right_f/type')]

        elif val == {PlCons.BICONDITIONAL}:
            # Biconditional has left and right formulas
            new_nodes += [dict(value=None, path='left_f')]
            new_nodes += [dict(value=None, path='right_f')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='left_f/type')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='right_f/type')]

        elif val == {PlCons.CONDITIONAL}:
            # Conditional has antecedent and consequent
            new_nodes += [dict(value=None, path='ante')]
            new_nodes += [dict(value=None, path='conse')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='ante/type')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='conse/type')]



    return new_nodes
