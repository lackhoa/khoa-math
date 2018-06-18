from khoa_math import MathT, Atom, Mole
from type_mgr import CI
from kset import KSet, KConst
from rel import Rel, RelT


#----------------------------TYPES----------------------------
# Well-formed Formulas
wff_dic = {}
wff_dic['ATOM'] = CI(args=[Atom(role='text', vals=KConst.STR.value)])

wff_dic['NEGATION'] = CI(
        args=[Atom(role='text', vals=KConst.STR.value),
              Mole(role='body_f', type_='WFF'),],
        rels=[Rel(RelT.FUN, lambda s: '(~{})'.format(s), 'body_f/text', 'text')])

wff_dic['CONDITIONAL'] = CI(
        args=[Mole(role='ante', type_='WFF'),
              Mole(role='conse', type_='WFF'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}->{})'.format(s1, s2),
            'ante/text', 'conse/text', 'text',)])

wff_dic['BICONDITIONAL'] = CI(
        args=[Mole(role='left', type_='WFF'),
              Mole(role='right', type_='WFF'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}<->{})'.format(s1, s2),
            'left/text', 'right/text', 'text',)])

wff_dic['CONJUNCTION'] = CI(
        args=[Mole(role='left', type_='WFF'),
              Mole(role='right', type_='WFF'),
              Atom(role = 'text', vals = KConst.STR.value),],
        rels=[Rel(
            RelT.FUN,
            lambda s1, s2: '({}&{})'.format(s1, s2),
            'left/text', 'right/text', 'text',)])

wff_dic['DISJUNCTION'] = CI(
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


# Union testing
uni_dic = {}
uni_dic['ATOM'] = CI(
    args = [
        Atom(role='sub0', vals=KConst.ANY.value),
        Atom(role='sub1', vals=KSet([frozenset({1,2,}), frozenset({3})])),
        Atom(role='uni', vals=KSet([frozenset({1,2,3}), frozenset({2,3,4})]))],
    rels = [Rel(RelT.UNION, 'sub0', 'sub1', 'uni')])


#----------------------------DICTIONARY----------------------------
# Constructor Dictionary
cons_dic = {}

cons_dic[MathT.WFF] = wff_dic
cons_dic['WFF_TEST'] = wff_dic_test
cons_dic['UNI'] = uni_dic
