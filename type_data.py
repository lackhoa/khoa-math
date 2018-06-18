from khoa_math import Atom, Mole
from kset import KSet, KConst
from rel import Rel, RelT

from typing import NamedTuple, Iterable, Union


###Stuff to interface with the typing modules###
class CI(NamedTuple):
    args: Iterable[Union['Atom', 'Molecule']]
    rels: Iterable[Rel] = []


#----------------------------DICTIONARY----------------------------
# Constructor Dictionary
cons_dic = {}


#----------------------------TYPES----------------------------
# Well-formed Formulas
cons_dic['WFF'] = {}
cons_dic['WFF']['ATOM'] = CI(args=[Atom(role='text', vals=KConst.STR.value)])

cons_dic['WFF']['NEGATION'] = CI(
        args=[Atom(role='text', vals=KConst.STR.value),
              Mole(role='body_f', type_='WFF'),],
        rels=[Rel(RelT.FUN, lambda s: '(~{})'.format(s), 'body_f/text', 'text')])

cons_dic['WFF']['CONDITIONAL'] = CI(
        args=[Mole(role='ante', type_='WFF'),
              Mole(role='conse', type_='WFF'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}->{})'.format(s1, s2),
            'ante/text', 'conse/text', 'text',)])

cons_dic['WFF']['BICONDITIONAL'] = CI(
        args=[Mole(role='left', type_='WFF'),
              Mole(role='right', type_='WFF'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}<->{})'.format(s1, s2),
            'left/text', 'right/text', 'text',)])

cons_dic['WFF']['CONJUNCTION'] = CI(
        args=[Mole(role='left', type_='WFF'),
              Mole(role='right', type_='WFF'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}&{})'.format(s1, s2),
            'left/text', 'right/text', 'text',)])

cons_dic['WFF']['DISJUNCTION'] = CI(
        args=[Mole(role='left', type_='WFF'),
              Mole(role='right', type_='WFF'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}v{})'.format(s1, s2),
            'left/text', 'right/text', 'text',)])


# Proofs
proof_dic = {}
proof_dic['PREM_INTRO'] = CI(
    args=[Mole(role='form', type_='WFF'),
          Atom(role='dep')],
    rels=Rel(RelT.ISO,
             lambda f: frozenset({f}), lambda d: list(d)[0],
             'form', 'dep'))



#----------------------------TESTING----------------------------
# Well-formed formulas testing
cons_dic['WFF_TEST'] = {}
cons_dic['WFF_TEST']['ATOM'] = CI(args=[Atom(role='text', vals=KSet({'P', 'Q'}))])

cons_dic['WFF_TEST']['NEGATION'] = CI(
        args=[Atom(role='text', vals=KConst.STR.value),
              Mole(role='body_f', type_='WFF_TEST'),],
        rels=[Rel(RelT.FUN, lambda s: '(~{})'.format(s), 'body_f/text', 'text')])

cons_dic['WFF_TEST']['CONDITIONAL'] = CI(
        args=[Mole(role='ante', type_='WFF_TEST'),
              Mole(role='conse', type_='WFF_TEST'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}->{})'.format(s1, s2),
            'ante/text', 'conse/text', 'text',)])


# Union testing
cons_dic['UNI'] = {}
cons_dic['UNI']['ONE'] = CI(
    args = [
        Atom(role='sub0', vals=KConst.ANY.value),
        Atom(role='sub1', vals=KSet([frozenset({1,2,}), frozenset({3})])),
        Atom(role='uni', vals=KSet([frozenset({1,2,3}), frozenset({2,3,4})]))],
    rels = [Rel(RelT.UNION, 'sub0', 'sub1', 'uni')])


# Proof testing
cons_dic['PROOF_TEST'] = {}
cons_dic['PROOF_TEST']['PREM_INTRO'] = CI(
    args=[Mole(role='form', type_='WFF_TEST'),
          Atom(role='dep')],
    rels=[Rel(RelT.ISO,
              lambda f: frozenset({f}), lambda d: list(d)[0],
              'form', 'dep')])

# Isomorphism testing
cons_dic['ISO_TEST'] = {}
cons_dic['ISO_TEST']['ONE'] = CI(
    args=[Atom(role='x'), Atom(role='y', vals=KSet({4, 5, 8}))],
    rels=[Rel(RelT.ISO, lambda y: y+1, lambda x: x-1, 'x', 'y')])
