from khoa_math import *
from rel import *

from typing import *


#---------------Stuff to interface with the typing modules------------
class CI(NamedTuple):         # Constructor item
    form: Mole                # The model of the constructor
    rels: Iterable[Rel] = []  # The relations between different parts


#----------------------------DICTIONARY----------------------------
# Constructor Dictionary
cons_dic = {}


#----------------------------TYPES----------------------------
# Well-formed Formulas
cons_dic['WFF'] = {}
cons_dic['WFF']['ATOM'] = CI(form=Mole(_text=STR))

cons_dic['WFF']['NEGATION'] = CI(
    form=Mole(_text = STR, body = Mole(_types = wr('WFF'))),
    rels=[kfun(fun = lambda s: '(~{})'.format(s),
               inp = ['body/_text'],
               out = '_text')])

cons_dic['WFF']['CONJUNCTION'] = CI(
    form=Mole(_text   = STR,
              left_f  = Mole(_types= wr('WFF')),
              right_f = Mole(_types= wr('WFF'))),
    rels=[kfun(fun   = (lambda s1, s2: '({}&{})'.format(s1, s2)),
               inp   = ['left_f/_text', 'right_f/_text'],
               out   = '_text')])

# Proofs
cons_dic['PROOF'] = {}
cons_dic['PROOF']['PREM_INTRO'] = CI(
    form = Mole(formu  = Mole(_types = wr('WFF')),
                dep    = SINGLETON,
                _text  = STR),
    rels = [*iso(lr_fun = lambda f: wr(frozenset({f})),  # f is a molecule, d is a Atom
                 rl_fun = lambda d: list(only(d))[0],
                 left   = 'formu',
                 right  = 'dep'),
            *keq('_text', 'formu/_text')])

cons_dic['PROOF']['&E1'] = CI(
    form = Mole(formu  = Mole(_types = wr('WFF')),
                conj_p = Mole(_types = wr('PROOF'),
                              formu  = Mole(_types = wr('WFF'),
                                            _cons  = wr('CONJUNCTION'))),
                dep    = SET),
    rels = [*eq('conj_p/formu/left_f', 'formu'),
            *eq('conj_p/dep', 'dep'),
            kfun(fun = lambda x: '(&E1 {})'.format(x),
                 inp = ['conj_p/_text'],
                 out = '_text')])

cons_dic['PROOF']['&E2'] = CI(
    form = Mole(formu  = Mole(_types = wr('WFF')),
                conj_p = Mole(_types = wr('PROOF'),
                              formu  = Mole(_types = wr('WFF'),
                                            _cons  = wr('CONJUNCTION'))),
                dep    = SET),
    rels = [*eq('conj_p/formu/right_f', 'formu'),
            *eq('conj_p/dep', 'dep'),
            kfun(fun = lambda x: '(&E2 {})'.format(x),
                 inp = ['conj_p/_text'],
                 out = '_text')])

cons_dic['PROOF']['&I'] = CI(
    form = Mole(formu   = Mole(_types = wr('WFF'), _cons = wr('CONJUNCTION')),
                left_p  = Mole(_types = wr('PROOF')),
                right_p = Mole(_types = wr('PROOF')),
                dep     = SET),
    rels = [*eq('left_p/formu', 'formu/left_f'),
            *eq('right_p/formu', 'formu/right_f'),
            Rel(type_  = 'UNION',
                subs   = ['left_p/dep', 'right_p/dep'],
                sup    = 'dep'),
            kfun(fun = lambda l, r: '(&I {} {})'.format(l, r),
                 inp = ['left_p/_text', 'right_p/_text'],
                 out = '_text')])


#----------------------------TEST TYPES----------------------------
# Well-formed formulas testing
cons_dic['WFF_TEST'] = {}
cons_dic['WFF_TEST']['ATOM'] = CI(form=Mole(_text = Atom({'P', 'Q'})))

cons_dic['WFF_TEST']['NEGATION'] = CI(
    form=Mole(_text = STR, body = Mole(_types = wr('WFF_TEST'))),
    rels=[kfun(fun = lambda s: '(~{})'.format(s),
               inp = ['body/_text'],
               out = '_text')])

cons_dic['WFF_TEST']['CONJUNCTION'] = CI(
    form=Mole(_text   = STR,
              left_f  = Mole(_types= wr('WFF_TEST')),
              right_f = Mole(_types= wr('WFF_TEST'))),
    rels=[funo(fun   = adapter(lambda s1, s2: '({}&{})'.format(s1, s2)),
               inp   = ['left_f/_text', 'right_f/_text'],
               out   = '_text')])


# Union testing
cons_dic['UNI'] = {}
# Missing the superset
cons_dic['UNI']['ONE'] = CI(
    form = Mole(sub0  = SET, sub1  = SET, super = SET),
    rels = [Rel(type_ = 'UNION',
                subs  = ['sub0', 'sub1'],
                sup   = 'super')])


# Isomorphism testing
cons_dic['ISO_TEST'] = {}
cons_dic['ISO_TEST']['UNIQUE'] = CI(
    form = Mole(x = INT, y = INT),
    rels = [*iso(left   = 'x',
                 right  = 'y',
                 lr_fun = adapter(lambda x: x+1),
                 rl_fun = adapter(lambda y: y-1))])

# Multiple relations testing
cons_dic['MULTI'] = {}
cons_dic['MULTI']['ONE'] = CI(
    form = Mole(x = INT, y = INT, z = INT),
    rels = [*iso(left   = 'x',
                 right  = 'y',
                 lr_fun = adapter(lambda x: x+1),
                 rl_fun = adapter(lambda y: y-1)),
            funo(fun   = adapter(lambda x: x),
                 inp   = ['x'],
                 out   = 'z')])
