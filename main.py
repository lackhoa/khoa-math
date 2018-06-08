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
    elif type(t) == MoleData:
        return Molecule(role=get_role(t.path), type_=t.type_, cons=t.cons)


def list_cons(t: MathType) -> Set:
    return set(cons_dic[t].keys())


def get_args(m: Molecule) -> List[Union['AtomData', 'MoleData']]:
    """Return an argument list based on type `t` and constructor `c`"""
    return cons_dic[m.type][m.cur_con]


def unify_cons(m: Molecule):
    m.cons = m.cons & KSet(list_cons(m.type))
    m.cons.make_explicit()  # since there finitely many constructors


def k_enumerate(root: MathObj, max_dep: int):
    if type(root) == Atom:
        for val in root.values:
            root.cur_val = val
            yield root

    elif type(root) == Molecule:
        # suply constructor if not available
        unify_cons(root)
        for con in root.cons:
            root.cur_con = con
            # Empty children list to accept new constructor: weird behavior?
            root.children = []

            if max_dep == 1:
                # routine to prevent infinite loop:
                has_molecule = False
                for arg in get_args(root):
                    if type(arg) == MoleData:
                        has_molecule = True; break
                if has_molecule:
                    continue  # Take another constructor

            args_math = map(math_obj_from_data, get_args(root))
            recur = partial(k_enumerate, max_dep = max_dep-1)
            children_combs = product(*map(recur, args_math))
            for children_comb in children_combs:
                root.children = children_comb
                yield root


wff_test_cons_dic = wff_cons_dic
wff_test_cons_dic['ATOM'] = [AtomData(path = 'text', values = KSet({'P'}))]
cons_dic['WFF_TEST'] = wff_test_cons_dic

start = Molecule(role='root', type_ = 'WFF_TEST', cons = KSet({'ATOM', 'NEGATION'}))


for t in k_enumerate(start, 4):
    print(anytree.RenderTree(t), end='\n\n')
