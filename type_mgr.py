from khoa_math import MathType
import wff


cons_dic = {}
cons_dic[MathType.WFF] = wff.wff_cons_dic


def list_cons(t: MathType):
    return cons_dic[t].keys()
