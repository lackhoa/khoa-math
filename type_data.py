from khoa_math import MathT
from kset import KSet, KConst
import wff, wff_test


cons_dic = {}

cons_dic[MathT.WFF] = wff.wff_dic
cons_dic['WFF_TEST'] = wff_test.wff_dic_test


# Testing zone:
union = {}
union['UNI'] = CI(args = [
    Atom(role='sub0', vals={frozenset({1,2,3,4})}),
    Atom(role='sub1', vals={frozenset({5,6})}),
    Atom(role='uni', vals=KConst.ANY.value,]
