import sys
import traceback

from kset import *
from misc import *
from khoa_math import *
from type_mgr import *
from type_data import *
from wff import *

import anytree
from typing import Set, Iterable
from itertools import product, starmap
from functools import partial


def custom_traceback(exc, val, tb):
    print("\n".join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def get_role(path: str) -> str:
    """Extract the role from `path`."""
    return path.split('/')[-1]


def get_parent(path: str) -> str:
    """Extract the path to the parent from `path`."""
    return '/'.join(path.split('/')[:-1])


def math_obj_from_data(t: Union[AtomData, MoleData]) -> MathObj:
    """Construct math objects from dataclasses."""
    if type(t) == AtomData:
        return Atom(role=get_role(t.path), values=t.values, web=t.web)
    else:
        return Molecule(role=get_role(t.path), type_=t.type_, cons=t.cons)


def list_cons(t: MathType) -> Set:
    return set(cons_dic[t].keys())


def get_args(m: Molecule) -> List[Union['AtomData', 'MoleData']]:
    """Return an argument list based on type `t` and constructor `c`"""
    return cons_dic[m.type][m.cur_con]


def unify_cons(m: Molecule):
    m.cons = m.cons & KSet(list_cons(m.type))
    m.cons.make_explicit()  # since there are few constructors


def k_enumerate(root: MathObj, max_dep: int):
    if type(root) == Atom:
        # Atom: Loop through potential values
        for val in root.values:
            res = root.clone()
            res.cur_val = val
            yield res

    else:
        # suply constructor
        cons = root.cons & KSet(list_cons(root.type))

        # Molecule: loop through potential constructors
        for con in cons:
            if max_dep <= 1:
                # check to prevent infinite loop:
                if any(map(lambda x: type(x) == MoleData, cons_dic[root.type][con])):
                    continue  # Try another constructor

            # Here is where the recursion begins:
            dec_dep = max_dep - 1
            recur = partial(k_enumerate, max_dep = dec_dep)
            # Turn data to real nodes:
            args_node = map(math_obj_from_data, cons_dic[root.type][con])
            possible_children_suit = product(*map(recur, args_node))
            for children_comb in possible_children_suit:
                res = root.clone()
                res.cur_con = con
                res.children = children_comb
                if con == 'CONDITIONAL' and len(res.children) < 2: print('Fuck')
                yield res


test_cons_dic = {}
test_cons_dic['ATOM'] = [AtomData(path = 'text', values = KSet({'P', 'Q', 'R'}))]
# test_cons_dic['NEGATION'] = [MoleData(path='body_f', type_='WFF_TEST')]
test_cons_dic['CONDITIONAL'] = [MoleData(path='ante', type_='WFF_TEST'),
                                MoleData(path='conse', type_='WFF_TEST')]
cons_dic['WFF_TEST'] = test_cons_dic

start = Molecule(role='root', type_ = 'WFF_TEST', cons = KSet({'ATOM', 'CONDITIONAL'}))


for i, t in enumerate(k_enumerate(start, 3)):
    print('#', i)
    print(anytree.RenderTree(t), end='\n')
