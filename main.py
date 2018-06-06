from KSet import *
from misc import *
from khoa_math import *
from k_math_more import *
from type_mgr import *

from anytree import PreOrderIter


def normalize(root: MathObj):
    if type(root) == Atom:
        pass
    else:
        if node.get('cons').is_complete():
            for comp in comp_dic[node.type][node.get('cons').values[0]]:
                try: node.get(comp.path)
                except PathError:
                    new_node = math_obj_from_data(comp)
                    new_node.parent = node.get(get_parent(comp.path))
        elif node


def enumerate(root: Molecule, max_dep: int):
    for node in PreOrderIter(root):
        if node.get('cons').is_complete():
            # check the object according to the constructor
        else:
            # Unify the node's constructor and the constructor list
            for cons in (root.get('cons').values & cons_dic[root.type]):
