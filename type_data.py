from khoa_math import *
from rel import Rel

from typing import *


#---------------Stuff to interface with the typing modules------------
class CI(NamedTuple):
    form: Mole                # The model of the constructor
    rels: Iterable[Rel] = []  # The relations between different parts


#----------------------------DICTIONARY----------------------------
# Constructor Dictionary
cons_dic = {}


#----------------------------TYPES----------------------------
# Well-formed Formulas
cons_dic['WFF'] = {}
cons_dic['WFF']['ATOM'] = CI(form=Mole(_text=KSet({'P', 'Q'})))

cons_dic['WFF']['NEGATION'] = CI(
    form=Mole(_text = STR, body = Mole(_types = wr('WFF'))),
    rels=[Rel(type_ = 'FUN',
              fun = adapter(lambda s: '(~{})'.format(s)),
              inp = ['body/_text'],
              out = '_text')])

cons_dic['WFF']['CONJUNCTION'] = CI(
    form=Mole(_text   = STR,
              left_f  = Mole(_types= wr('WFF')),
              right_f = Mole(_types= wr('WFF'))),
    rels=[Rel(type_ = 'FUN',
              fun = adapter(lambda s1, s2: '({}&{})'.format(s1, s2)),
              inp = ['left_f/_text', 'right_f/_text'],
              out = '_text')])

# Proofs
cons_dic['PROOF'] = {}
cons_dic['PROOF']['PREM_INTRO'] = CI(
    form = Mole(formu  = Mole(_types = wr('WFF')),
                dep    = SET),
    rels = [Rel(type_  = 'ISO',
                Lr_fun = lambda f: wr(frozenset({f})),  # f is a molecule, d is a KSet
                rL_fun = lambda d: list(only(d))[0],
                left   = 'formu',
                right  = 'dep')])

cons_dic['PROOF']['&I'] = CI(
    form = Mole(formu   = Mole(_types = wr('WFF'), _cons = wr('CONJUNCTION')),
                left_p  = Mole(_types = wr('PROOF')),
                right_p = Mole(_types = wr('PROOF')),
                dep     = SET),
    rels = [Rel(type_ = 'FUN',
                fun   = lambda l, r: Mole(left_f = l, right_f = r),
                inp   = ['left_p/formu', 'right_p/formu'],
                out   = 'formu'),
            Rel(type_  = 'UNION',
                subs   = ['left_p/dep', 'right_p/dep'],
                sup    = 'dep'),])


#----------------------------TEST TYPES----------------------------
# Well-formed formulas testing
cons_dic['WFF_TEST'] = {}
cons_dic['WFF_TEST']['ATOM'] = CI(form=Mole(_text = KSet({'P', 'Q'})))

cons_dic['WFF_TEST']['NEGATION'] = CI(
    form=Mole(_text = STR, body = Mole(_types = wr('WFF_TEST'))),
    rels=[Rel(type_ = 'FUN',
              fun = adapter(lambda s: '(~{})'.format(s)),
              inp = ['body/_text'],
              out = '_text')])

cons_dic['WFF_TEST']['CONJUNCTION'] = CI(
    form=Mole(_text   = STR,
              left_f  = Mole(_types= wr('WFF_TEST')),
              right_f = Mole(_types= wr('WFF_TEST'))),
    rels=[Rel(type_ = 'FUN',
              fun   = adapter(lambda s1, s2: '({}&{})'.format(s1, s2)),
              inp   = ['left_f/_text', 'right_f/_text'],
              out   = '_text')])


# Union testing
cons_dic['UNI'] = {}
# Missing one of the subsets
cons_dic['UNI']['ONE'] = CI(
    form = Mole(sub0  = SET,
                sub1  = KSet({frozenset({1,2}), frozenset({3})}),
                super = KSet({frozenset({1,2,3}), frozenset({2,3,4})})),
    rels = [Rel(type_ = 'UNION',
                subs  = ['sub0', 'sub1'],
                sup   = 'super')])
# Missing the superset
cons_dic['UNI']['TWO'] = CI(
    form = Mole(sub0  = KSet({frozenset({6,3,4})}),
                sub1  = KSet({frozenset({1,2}), frozenset({3})}),
                super = SET),
    rels = [Rel(type_ = 'UNION',
                subs  = ['sub0', 'sub1'],
                sup   = 'super')])


# Proof testing
cons_dic['PROOF_TEST'] = {}
cons_dic['PROOF_TEST']['PREM_INTRO'] = CI(
    form = Mole(formu  = Mole(_types = wr('WFF_TEST')),
                dep    = SET),
    rels = [Rel(type_  = 'ISO',
                Lr_fun = lambda f: wr(frozenset({f})),  # f is a molecule, d is a KSet
                rL_fun = lambda d: list(only(d))[0],
                left   = 'formu',
                right  = 'dep')])

# Isomorphism testing
cons_dic['ISO_TEST'] = {}
# Missing left
cons_dic['ISO_TEST']['ONE'] = CI(
    form = Mole(x = INT, y = KSet({4,5,8})),
    rels = [Rel(type_ = 'ISO',
            left   = 'x',
            right  = 'y',
            Lr_fun = adapter(lambda x: x+1),
            rL_fun = adapter(lambda y: y-1))])
# Missing right
cons_dic['ISO_TEST']['TWO'] = CI(
    form = Mole(x = KSet({4,5,8}), y = INT),
    rels = [Rel(type_ = 'ISO',
            left   = 'x',
            right  = 'y',
            Lr_fun = adapter(lambda x: x+1),
            rL_fun = adapter(lambda y: y-1))])

# Multiple relations testing
cons_dic['MULTI'] = {}
cons_dic['MULTI']['ONE'] = CI(
    form = Mole(x = INT, y = KSet({4,5,8}), z = INT),
    rels = [Rel(type_ = 'ISO',
                left   = 'x',
                right  = 'y',
                Lr_fun = adapter(lambda x: x+1),
                rL_fun = adapter(lambda y: y-1)),
            Rel(type_ = 'FUN',
                fun   = adapter(lambda x: x),
                inp   = ['x'],
                out   = 'z')])
