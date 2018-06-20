from khoa_math import Mole
from kset import KSet, KConst, adapter, ks
from rel import Rel

from typing import NamedTuple, Iterable, Union


#---------------Stuff to interface with the typing modules------------
class CI(NamedTuple):
    form: Mole                # The model of the constructor
    rels: Iterable[Rel] = []  # The relations between different parts


#----------------------------DICTIONARY----------------------------
# Constructor Dictionary
cons_dic = {}


#----------------------------TYPES----------------------------
# Well-formed Formulas
# cons_dic['WFF'] = {}
# cons_dic['WFF']['ATOM'] = CI(args={text})

# cons_dic['WFF']['NEGATION'] = CI(
#         args=[Atom(role='text', vals=KConst.STR.value),
#               Mole(role='body_f', type_='WFF'),],
#         rels=[Rel('FUN', lambda s: '(~{})'.format(s), 'body_f/text', 'text')])

# cons_dic['WFF']['CONDITIONAL'] = CI(
#         args=[Mole(role='ante', type_='WFF'),
#               Mole(role='conse', type_='WFF'),
#               Atom(role = 'text', vals = KConst.STR.value),],
#         rels=[Rel(
#             'FUN',
#             lambda s1, s2: '({}->{})'.format(s1, s2),
#             'ante/text', 'conse/text', 'text',)])

# cons_dic['WFF']['BICONDITIONAL'] = CI(
#         args=[Mole(role='left', type_='WFF'),
#               Mole(role='right', type_='WFF'),
#               Atom(role = 'text', vals = KConst.STR.value),],
#         rels=[Rel(
#             'FUN',
#             lambda s1, s2: '({}<->{})'.format(s1, s2),
#             'left/text', 'right/text', 'text',)])

# cons_dic['WFF']['CONJUNCTION'] = CI(
#         args=[Mole(role='left', type_='WFF'),
#               Mole(role='right', type_='WFF'),
#               Atom(role = 'text', vals = KConst.STR.value),],
#         rels=[Rel(
#             'FUN',
#             lambda s1, s2: '({}&{})'.format(s1, s2),
#             'left/text', 'right/text', 'text',)])

# cons_dic['WFF']['DISJUNCTION'] = CI(
#         args=[Mole(role='left', type_='WFF'),
#               Mole(role='right', type_='WFF'),
#               Atom(role = 'text', vals = KConst.STR.value),],
#         rels=[Rel(
#             'FUN',
#             lambda s1, s2: '({}v{})'.format(s1, s2),
#             'left/text', 'right/text', 'text',)])


# # Proofs
# cons_dic['PROOF'] = {}
# cons_dic['PROOF']['PREM_INTRO'] = CI(
#     args=[Mole(role='form', type_='WFF'),
#           Atom(role='dep')],
#     rels=[Rel('ISO',
#               lambda f: frozenset({f}), lambda d: list(d)[0],
#               'form', 'dep')])

# cons_dic['PROOF']['&I'] = CI(
#     args=[Mole(role='left', type_='WFF'),
#           Mole(role='right', type_='WFF'),
#           Atom(role='dep')],
#     rels=Rel('UNION', 'left/dep', 'right/dep', 'dep'))



#----------------------------TEST TYPES----------------------------
# Well-formed formulas testing
cons_dic['WFF_TEST'] = {}
cons_dic['WFF_TEST']['ATOM'] = CI(form=Mole(_text=KSet({'P', 'Q'})))

cons_dic['WFF_TEST']['NEGATION'] = CI(
    form=Mole(_text=KConst.STR.value, body=Mole(type_='WFF_TEST')),
    rels=[Rel(type_ = 'FUN',
              fun = adapter(lambda s: '(~{})'.format(s)),
              inp = ['body/_text'],
              out = '_text')])

cons_dic['WFF_TEST']['CONJUNCTION'] = CI(
    form=Mole(_text = KConst.STR.value,
              left  = Mole(type_='WFF_TEST'),
              right = Mole(type_='WFF_TEST')),
    rels=[Rel(type_ = 'FUN',
              fun = adapter(lambda s1, s2: '({}&{})'.format(s1, s2)),
              inp = ['left/_text', 'right/_text'],
              out = '_text')])


# Union testing
cons_dic['UNI'] = {}
# Missing one of the subsets
cons_dic['UNI']['ONE'] = CI(
    form = Mole(sub0  = KConst.SET.value,
                sub1  = KSet({frozenset({1,2}), frozenset({3})}),
                super = KSet({frozenset({1,2,3}), frozenset({2,3,4})})),
    rels = [Rel(type_ = 'UNION',
                subs  = ['sub0', 'sub1'],
                sup   = 'super')])
# Missing the superset
cons_dic['UNI']['TWO'] = CI(
    form = Mole(sub0  = KSet({frozenset({6,3,4})}),
                sub1  = KSet({frozenset({1,2}), frozenset({3})}),
                super = KConst.SET.value),
    rels = [Rel(type_ = 'UNION',
                subs  = ['sub0', 'sub1'],
                sup   = 'super')])


# # Proof testing
# cons_dic['PROOF_TEST'] = {}
# cons_dic['PROOF_TEST']['PREM_INTRO'] = CI(
#     args=[Mole(role='form', type_='WFF_TEST'),
#           Atom(role='dep')],
#     rels=[Rel('ISO',
#               lambda f: frozenset({f}), lambda d: list(d)[0],
#               'form', 'dep')])

# Isomorphism testing
cons_dic['ISO_TEST'] = {}
# Missing left
cons_dic['ISO_TEST']['ONE'] = CI(
    form = Mole(x = KConst.INT.value, y = KSet({4,5,8})),
    rels = [Rel(type_ = 'ISO',
            left   = 'x',
            right  = 'y',
            Lr_fun = adapter(lambda x: x+1),
            rL_fun = adapter(lambda y: y-1))])
# Missing right
cons_dic['ISO_TEST']['TWO'] = CI(
    form = Mole(x = KSet({4,5,8}), y = KConst.INT.value),
    rels = [Rel(type_ = 'ISO',
            left   = 'x',
            right  = 'y',
            Lr_fun = adapter(lambda x: x+1),
            rL_fun = adapter(lambda y: y-1))])
