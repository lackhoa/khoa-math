import sys
import traceback

from kset import *
from misc import *
from khoa_math import *
from type_mgr import *
from type_data import *
from wff import *

import anytree
from typing import Set, Iterable, FrozenSet
from itertools import product, starmap
from functools import partial


def custom_traceback(exc, val, tb):
    print("\n".join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def list_cons(t: MathType) -> FrozenSet:
    return frozenset(cons_dic[t].keys())


def k_enumerate(root: MathObj, max_dep: int):
    if type(root) == Atom and max_dep >= 0:
        # Atom: Loop through potential values
        if root.vals.is_explicit():
            for val in root.vals:
                res = root.clone()
                res.vals = KSet({val})
                yield res
        else: yield root.clone()

    elif max_dep != 0:
        # suply constructor
        cons = root.cons & KSet(list_cons(root.type))

        # Mole: loop through potential constructors
        for con in cons:
            if max_dep == 1:
                # mechanism to prevent infinite loop:
                if any(map(lambda x: type(x) == MoleData, cons_dic[root.type][con])):
                    continue  # Try another constructor

            # Here is where the recursion begins:
            recur = partial(k_enumerate, max_dep = max_dep-1)
            # Turn data to real nodes:
            args_node = map(math_obj_from_data, cons_dic[root.type][con])
            possible_children_suit = product(*map(recur, args_node))
            for children_suit in possible_children_suit:
                res = root.clone()
                res.cons = KSet({con})
                children_suit_clone = [n.clone() for n in children_suit]
                res.children = children_suit_clone
                # Now res is a well-formed tree, but it's not complete, so:
                for node in anytree.PostOrderIter(res):
                    if type(node) == Atom and (not node.vals.is_explicit()):
                        try:
                            get_val_from_path = lambda x: node.parent.get_path(x).vals[0]
                            node.vals = node.vals(*map(get_val_from_path, node.web))
                        except Exception as e:
                            print(e)  # Probably the inputs don't exist yet
                yield res


tdic = {}
tdic['ATOM'] = [FAtom(role='text', vals=KSet(['P']))]
tdic['NEGATION'] = [FMole(role='body_f', type_='WFF_TEST']

tdic['CONDITIONAL'] = [FMole(role='ante', type_='WFF_TEST'),
                       FMole(role='conse', type_='WFF_TEST'),
                       AtomData(role = 'text', vals = KConst.STR)]
cons_dic['WFF_TEST'] = tdic

start = Mole(role='root', type_ = 'WFF_TEST', cons = KSet({'ATOM', 'NEGATION'}))


store = []
for i, t in enumerate(k_enumerate(start, 3)):
    t.name = i; store.append(t)
    print(anytree.RenderTree(t), end='\n\n')

rt = lambda t: print(anytree.RenderTree(t))
