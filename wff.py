from khoa_math import MathType
from kset import KSet, STR
from misc import MyEnum
from type_mgr import AtomData, MoleData


from enum import auto
from typing import Dict, Iterable


left_right_forms = [MoleData(path='left_f', type_=MathType.WFF),
                    MoleData(path='right_f', type_=MathType.WFF)]

wff_cons_dic = {}
wff_cons_dic['ATOM'] = [AtomData(path = 'text', values = STR)]
wff_cons_dic['NEGATION'] = [MoleData(path='body_f', type_=MathType.WFF)]
wff_cons_dic['CONJUNCTION'] = left_right_forms
wff_cons_dic['DISJUNCTION'] = left_right_forms
wff_cons_dic['BICONDITIONAL'] = left_right_forms
wff_cons_dic['CONDITIONAL'] = [MoleData(path='ante', type_=MathType.WFF),
                               MoleData(path='conse', type_=MathType.WFF)]
