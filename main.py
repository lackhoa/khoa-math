from KSet import *
from khoa_math import *
from type_mgr import *
from misc import *

from anytree import PreOrderIter


def enumerate(root: Molecule, max_dep: int):
    if root.get('cons').is_complete():
        for comp in comp_dic[root.type][root.cons]:
            try: root.get(comp.path)
            except PathError: 
    else:
        for cons in (root.get('cons').values & cons_dic[root.type]):
            

