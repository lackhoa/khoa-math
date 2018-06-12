import sys
import logging
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


logging.basicConfig(format='\n%(message)s', stream=sys.stderr, level=logging.DEBUG)


def custom_traceback(exc, val, tb):
    logging.debug("\n".join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def list_cons(t: MathT) -> FrozenSet:
    return frozenset(cons_dic[t].keys())


def tlr(path: str) -> str:
    """Find top-level role"""
    return path.split('/')[0]


def dt(t): logging.debug(anytree.RenderTree(t))
def rt(t): logging.info(anytree.RenderTree(t))


count = 0
bag = []
def save(t, tag=''):
    global count
    t.name = str(count) + tag
    count += 1
    bag.append(t)


def kenumerate(root: ATMO, max_dep: int, tags=(), checked_rel=()) -> Iterable[ATMO]:
    """
    This function does NOT alter the root.
    Return the same type that it receives.
    If a child exists, it must be legit.
    """
    # Atom route
    if type(root) == Atom and max_dep >= 0:
        logging.debug('\nEnumerating this atom:')
        dt(root)
        # Atom: Loop through potential values
        if root.vals.is_explicit():
            for val in root.vals:
                res = res.clone()
                res.vals = KSet({val})
                save(res); yield res
        else:


            raise Exception('What the hell am I supposed to loop through now?')

    # Molecule route
    elif max_dep != 0:
        logging.debug('\nEnumerating this molecule')
        dt(root)
        if 'choose_con' not in tags:
            logging.debug('Constructor choosing phase')
            tags += ('choose_con',)
            cons = root.cons & KSet(list_cons(root.type))

            for con in cons:
                logging.debug('Chosen {}'.format(con))
                res = root.clone()
                res.cons = KSet({con})
                args, rels = cons_dic[root.type][con]

                # mechanism to prevent infinite loop:
                if max_dep == 1:
                    if any(map(lambda x: type(x) is Mole, args)):
                        logging.debug('Out of level, try another constructor')
                        continue

                logging.debug('The tree right now:')
                dt(res)
                for arg in args:
                    res.kattach(arg)
                logging.debug('Out tree is now full:')
                dt(res)
                logging.debug('With this decision in mind, let\'s go again!')
                for k in kenumerate(res, max_dep, tags):
                    yield k
            raise StopIteration

        rels = cons_dic[root.type][root.cons[0]].rels
        try: rel = [r for r in rels if r not in checked_rel][0]
        except IndexError: rel = None
        if rel:
            logging.debug('Relation phase')
            logging.debug('Checking relation {}'.format(rel))
            checked_rel += (rel,)
            if rel.type == RelT.FUN:
                logging.debug('It\'s a functional relation')
                in_args = []
                for slot in rel.get('in'):
                    in_args += [n for n in root.children if n.role == tlr(slot)]

                logging.debug('The inputs needed are:')
                logging.debug(in_args)
                recur = partial(kenumerate, max_dep = max_dep-1)
                all_input_suits = product(*map(recur, in_args))
                logging.debug('Got all input suits. Reminder: we are dealing with:')
                dt(root)
                for input_suit in all_input_suits:
                    res = root.clone()
                    for inp in input_suit: res.kattach(inp)

                    logging.debug('Attached input suit:')
                    dt(res)
                    get_first_of_path = lambda p: res.get_path(p).vals[0]
                    output = rel.get('fun')\
                            (*map(get_first_of_path, rel.get('in')))
                    out_atom = Atom(role=rel.get('out'), vals=KSet({output}))
                    res.kattach(out_atom)
                    logging.debug('Attached output:')
                    dt(res)

                    logging.debug('Done with this relation, restart!')
                    for k in kenumerate(res, max_dep, tags, checked_rel):
                        save(k); yield k
            raise StopIteration

        logging.debug('We are now in the finishing phase')
        recur = partial(kenumerate, max_dep = max_dep-1)
        missing_children = [n for n in root.children if not n.is_complete()]
        if missing_children:
            logging.debug('There are still children missing')
            all_children_suits = product(*map(recur, root.children))
            logging.debug('Looping through all children suit')
            for children_suit in all_children_suits:
                res = root.clone()
                for n in children_suit:
                    res.kattach(n.clone())
                logging.debug('Attached children suit')
                dt(res)
                assert(res.is_complete())
                logging.debug('Let\'s yield this!')
                save(res); yield res
        else:
            logging.debug('No children missing')
            logging.debug('Let\'s yield this!')
            yield root.clone()


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


LEVEL_CAP = 2
for t in kenumerate(root=start, max_dep=LEVEL_CAP):
    logging.info('RETURNED {}\n\n'.format(anytree.RenderTree(t)))
