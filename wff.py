from khoa_math import MathType
from kset import KSet, KConst
from misc import MyEnum

from enum import auto
from typing import Dict, Iterable


class WffCons(MyEnum):
    ATOM = auto()
    NEGATION = auto()
    CONJUNCTION = auto()
    DISJUNCTION = auto()
    CONDITIONAL = auto()
    BICONDITIONAL = auto()


AtomTup = namedtuple('AtomTuple', ['path', 'value'])
MoleTup = namedtuple('MoleculeTuple', ['path', 'type_'])

left_right_forms = [MoleTup(path='left_f', type_=MathType.WFF),
                    MoleTup(path='right_f', type_=MathType.WFF)]

wff_components = {}
wff_components[PlCons.ATOM] = [AtomTup(path='text', value=KConst.UNKNOWN)]
wff_components[PlCons.NEGATION] = [MoleTup(path='body_f', type_=MathType.WFF)]
wff_components[PlCons.CONJUNCTION] = left_right_forms
wff_components[PlCons.DISJUNCTION] = left_right_forms
wff_components[PlCons.BICONDITIONAL] = left_right_forms
wff_components[PlCons.CONDITIONAL] = [MoleTup(path='ante', type_=MathType.WFF),
                                      MoleTup(path='conse', type_=MathType.WFF)]


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

