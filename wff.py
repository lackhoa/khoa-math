from khoa_math import MathType
from kset import KSet, KConst
from misc import MyEnum, AutomTup, MoleTup

from enum import auto
from typing import Dict, Iterable
from collections import namedtuple


class WffCons(MyEnum):
    ATOM = auto()
    NEGATION = auto()
    CONJUNCTION = auto()
    DISJUNCTION = auto()
    CONDITIONAL = auto()
    BICONDITIONAL = auto()


left_right_forms = [MoleTup(path='left_f', type_=MathType.WFF),
                    MoleTup(path='right_f', type_=MathType.WFF)]

wff_comp_dic = {}
wff_comp_dic[PlCons.ATOM] = [AtomTup(path='text', value=KConst.UNKNOWN)]
wff_comp_dic[PlCons.NEGATION] = [MoleTup(path='body_f', type_=MathType.WFF)]
wff_comp_dic[PlCons.CONJUNCTION] = left_right_forms
wff_comp_dic[PlCons.DISJUNCTION] = left_right_forms
wff_comp_dic[PlCons.BICONDITIONAL] = left_right_forms
wff_comp_dic[PlCons.CONDITIONAL] = [MoleTup(path='ante', type_=MathType.WFF),
                                    MoleTup(path='conse', type_=MathType.WFF)]


def wff_str(form: Molecule) -> str:
    assert(form.type == MathType.WFF), 'Cannot be printed since this object is not a wff'
    assert(form.is_complete()), 'Cannot be printed since this object is not complete'

    res: str
    if form.cons == PlCons.ATOM:
        res = form.get('text').value[0]
    elif cons == PlCons.NEGATION:
        res = '(~{})'.format(wff_str(form.get('body')))
    elif cons == {PlCons.CONJUNCTION}:
        res = '({}&{})'.format(wff_str(form.get('left_f')), wff_str(form.get('right_f')))
    elif cons == {PlCons.DISJUNCTION}:
        res = '({}v{})'.format(wff_str(form.get('left_f')), wff_str(form.get('right_f')))
    elif cons == {PlCons.BICONDITIONAL}:
        res = '({}<->{})'.format(wff_str(form.get('left_f')), wff_str(form.get('right_f')))
    elif cons == {PlCons.CONDITIONAL}:
        res = '({}->{})'.format(wff_str(form.get('ante')), wff_str(form.get('conse')))
    return res

