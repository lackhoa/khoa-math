import sys
import traceback

from kset import *
from misc import *
from khoa_math import *
from type_mgr import *
from type_data import *
from wff import *
from rel import *

import anytree
from typing import Set, Iterable, FrozenSet, Union
from itertools import product, starmap
from functools import partial


def custom_traceback(exc, val, tb):
    print("\n".join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def list_cons(t: MathT) -> FrozenSet:
    return frozenset(cons_dic[t].keys())


def tlr(path: str) -> str:
    """Find top-level role"""
    return path.split('/')[0]


def k_enumerate(root: ATMO, max_dep: int) -> Iterable[ATMO]:
    """
    This function does NOT alter the root.
    Return the same type that it receives.
    If a child exists, it must be legit.
    """
    # recursion decreases by dep
    recur = partial(k_enumerate, max_dep = max_dep-1)

    if type(root) == Atom and max_dep >= 0:
        # Atom: Loop through potential values
        if root.vals.is_explicit():
            for val in root.vals:
                res = root.clone()
                res.vals = KSet({val})
                yield res
        # else: raise Exception('What the hell am I supposed to loop through now?')

    elif max_dep != 0:
        # suply constructor
        cons = root.cons & KSet(list_cons(root.type))

        # Mole: loop through all potential constructors, now that we have 'em
        for con in cons:
            # Now we know the exact constructor
            args, rels = cons_dic[root.type][con]

            if max_dep == 1:
                # mechanism to prevent infinite loop:
                if any(map(lambda x: type(x) is Mole, args)):
                    continue  # Try another constructor

            # Here is where the recursion begins:
            # Debating the relations:
            for rel in rels:
                if rel.type == RelT.FUN\
                    and (not root.has_path(rel.get('out'))
                         or (not root.get_path(rel.get('out')).vals.is_singleton())):
                    goals = []
                    for slot in rel.get('in'):
                        # Since the inputs are necessary, we must find them first
                        if not root.has_path(slot):
                            # There should be only one, btw
                            goals += [n for n in args if n.role == tlr(slot)]
                    all_input_suits = product(*map(recur, goals))
                    # Find the output
                    for input_suit in all_input_suits:
                        res = root.clone()
                        res.cons = KSet({con})
                        res.children = [n.clone() for n in input_suit]
                        get_first_of_path = lambda p: res.get_path(p).vals[0]
                        output = rel.get('fun')(*map(get_first_of_path, rel.get('in')))
                        # Attach the output node to `res`
                        Atom(role=rel.get('out'), vals=KSet({output})).parent = res
                        for k in k_enumerate(res, max_dep):
                            yield k

            # Done with relations
            # Gather all the args remaining, they should all be easy
            rem_args = [n for n in args if (not root.has_path(n.role))]
            all_rem_args_suit = product(*map(recur, rem_args))
            for rem_args_suit in all_rem_args_suit:
                res = root.clone()
                res.children = [n.clone() for n in rem_args_suit]
                yield res


tdic = {}
tdic['ATOM'] = CI(args=[Atom(role='text', vals=KSet(['P']))])
tdic['NEGATION'] = CI(args=[Atom(role='text', vals=KConst.STR.value),
                            Mole(role='body_f', type_='WFF_TEST')],
                      rels=[Rel(RelT.FUN,
                                lambda s: '(~{})'.format(s),
                                'body_f/text', 'text')])

# tdic['CONDITIONAL'] = CI(args=[Mole(role='ante', type_='WFF_TEST'),
#                                Mole(role='conse', type_='WFF_TEST'),
#                                Atom(role = 'text', vals = KConst.STR.value)],
#                          rels=[Rel(RelT.FUN,
#                                    lambda s1, s2: '(()&())'.format(s1, s2),
#                                    'ante/text', 'conse/text', 'text')])
cons_dic['WFF_TEST'] = tdic

start = Mole(role='root', type_ = 'WFF_TEST', cons = KSet({'ATOM', 'NEGATION'}))


store = []
LEVEL_CAP = 3
for i, t in enumerate(k_enumerate(root=start, max_dep=LEVEL_CAP)):
    t.name = i; store.append(t)
    print(anytree.RenderTree(t), end='\n\n')

rt = lambda t: print(anytree.RenderTree(t))
