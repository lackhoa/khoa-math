from khoa_math import MathType
import wff


cons_dic = {}
cons_dic[MathType.WFF] = list(wff.WFFCons)


comp_dic = {}
comp_dic[MathType.WFF] = wff.wff_comp_dic


def math_str(m: Molecule) -> str:
    if m.type == MathType.WFF:
        return wff.wff_str(m)
