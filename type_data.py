from khoa_math import MathT, Atom, Mole
from type_mgr import CI
from kset import KSet, KConst
from rel import Rel, RelT
import wff, wff_test


# Testing zone:
uni_dic = {}
uni_dic['ATOM'] = CI(
    args = [
        Atom(role='sub0', vals=KSet({frozenset({7,3,4,1}), frozenset({1,2,3,4})})),
        Atom(role='sub1', vals=KSet({frozenset({5,6}), frozenset(set())})),
        Atom(role='uni', vals=KConst.ANY.value,),],
    rels = [Rel(RelT.UNION, 'sub0', 'sub1', 'uni')])


cons_dic = {}

cons_dic[MathT.WFF] = wff.wff_dic
cons_dic['WFF_TEST'] = wff_test.wff_dic_test
cons_dic['UNI'] = uni_dic


