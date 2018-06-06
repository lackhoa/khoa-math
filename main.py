from khoa_math import *
from type_mgr import *
from misc import *

from anytree import PreOrderIter


def enumerate(root: Molecule, max_dep: int):
    if root.has_cons:
        for comp in comp_dic[root.type][root.cons]:
            try: root.get(comp.path)
            except PathError: 

