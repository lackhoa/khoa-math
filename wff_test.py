from khoa_math import MathT, Atom, Mole
from rel import Rel, RelT
from kset import KSet, KConst
from misc import MyEnum
from type_mgr import CI


from enum import auto
from typing import Dict, Iterable


wff_dic_test = {}
wff_dic_test['ATOM'] = CI(args=[Atom(role='text', vals=KSet({'P', 'Q'}))])
wff_dic_test['NEGATION'] = CI(
        args=[Atom(role='text', vals=KConst.STR.value),
              Mole(role='body_f', type_='WFF_TEST'),],
        rels=[Rel(RelT.FUN, lambda s: '(~{})'.format(s), 'body_f/text', 'text')])

wff_dic_test['CONDITIONAL'] = CI(
        args=[Mole(role='ante', type_='WFF_TEST'),
              Mole(role='conse', type_='WFF_TEST'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}->{})'.format(s1, s2),
            'ante/text', 'conse/text', 'text',)])
