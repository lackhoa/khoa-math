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
from copy import deepcopy


logging.basicConfig(format='%(message)s', filename='logs/debug.log',
                    level=logging.DEBUG, filemode='w')

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)
# set a format which is simpler for console use
formatter = logging.Formatter('%(message)s')
# tell the handler to use this format
console.setFormatter(formatter)
# add the handler to the root loggingger
logging.getLogger('').addHandler(console)

def custom_traceback(exc, val, tb):
    print("\n".join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def rt(t): return anytree.RenderTree(t)


def kenumerate(root: ATMO, max_dep: int, phase=0, trace:tuple = ()) -> Iterable[ATMO]:
    """
    This function does NOT alter the root.
    Return the same type that it receives.
    If a child exists, it must be legit.
    """
    logging.debug('#'*30 + '\nMain function here!')
    logging.debug('\nThe root is:'); logging.debug(rt(root))
    if type(root) == Atom and max_dep >= 0:
        logging.debug('\nIt\'s an atom')
        logging.debug('Considering all potential values')
        if root.vals.is_explicit():
            for choice, val in enumerate(root.vals):
                trace.append[chr(97+choice)]
                logging.debug('\nCurrent trace is: {}'.format('.'.join(trace)))
                res = res.clone()
                res.vals = KSet({val})
                logging.debug('Got new value: {}'.format(val))
                logging.debug(rt(res))
                logging.debug('\nYielding this atom:')
                yield res
        else:
            raise Exception('What the hell am I supposed to loop through now?')

    elif max_dep == 0:
        logging.debug('Ran out of level for this molecule')
    else:
        logging.debug('It\'s a molecule')
        phases = (constructor_phase, relation_phase, finishing_phase)
        if phase == len(phases):
            logging.debug('\nYielding from main since all phases are complete')
            yield root.clone()
        else:
            logging.debug('\nLet\'s get the tree through phase {}'.format(phase))
            for choice, new_root in enumerate(phases[phase](root=root, max_dep=max_dep)):
                trace += (chr(97+choice),)
                logging.debug('\nCurrent trace is: {}'.format('.'.join(trace)))
                logging.debug('\nTo the next phases we go!')
                for res in kenumerate(new_root, max_dep, phase+1, trace):
                    yield res


def constructor_phase(root, max_dep):
    """Assure that the root is well-formed (for one immediate level)"""
    logging.debug('#'*30 + '\nWelcome to the Constructor phase')
    logging.debug('\nUnifying constructor')
    cons = root.cons & KSet(cons_dic[root.type].keys())
    logging.debug('Possible constructors are: {}'.format(cons))
    for choice, con in enumerate(cons):
        logging.debug('\nChosen constructor {}'.format(con))
        res = root.clone()
        res.cons = KSet({con})
        args, rels = cons_dic[root.type][con]

        logging.debug('\nRoutine to prevent infinite loop:')
        if max_dep == 1 and any(map(lambda x: type(x) is Mole, args)):
            logging.debug('Out of level, try another constructor')
            continue

        logging.debug('This constructor is fine')
        logging.debug('\nAttaching children according to constructor')
        for arg in args:
            res.kattach(arg)
        logging.debug('\nResult is:'); logging.debug(rt(res))
        logging.debug('Yielding from constructor phase')
        yield res


def relation_phase(root: Mole, phase=0, max_dep=0):
    """Apply all relations to root"""
    logging.debug('#'*30 + '\nWelcome to the Relation phase')
    rels = cons_dic[root.type][root.cons[0]].rels
    try: rel = take_index(rels, phase)
    except IndexError:
        logging.debug('\nNo more relations, relation phase over')
        logging.debug('Yielding from relation phase')
        yield root.clone()
        raise StopIteration

    logging.debug('\nWorking with relation {}'.format(rel))
    if rel.type == RelT.FUN:
        logging.debug('It\'s a functional relation')
        in_args = []
        for slot in rel.get('in'):
            in_args += [n for n in root.children if n.role == car(slot)]

        logging.debug('\nThe inputs needed are:')
        logging.debug(in_args)
        recur = partial(kenumerate, max_dep = max_dep-1)
        all_input_suits = product(*map(recur, in_args))
        logging.debug('\nLet\'s see what input suits there are:')
        for choice, input_suit in enumerate(all_input_suits):
            res = root.clone()
            for inp in input_suit: res.kattach(inp)
            logging.debug('\nAttached input suit:'); logging.debug(rt(res))

            get_first_of_path = lambda p: res.get_path(p).vals[0]
            output = rel.get('fun')\
                    (*map(get_first_of_path, rel.get('in')))
            out_atom = Atom(role=car(rel.get('out')), vals=KSet({output}))
            res.kattach(node=out_atom, path=cdr(rel.get('out')))
            logging.debug('\nAttached output:'); logging.debug(rt(res))

            for k in relation_phase(res, phase+1):
                yield k


def finishing_phase(root, max_dep=0):
    """Enumerate all children that haven't been enumerated"""
    logging.debug('#'*30 + '\nWe are now in the Finishing phase')
    if [n for n in root.children if not n.is_complete()]:
        logging.debug('\nThere are incomplete children')
        recur = partial(kenumerate, max_dep = max_dep-1)
        all_children_suits = product(*map(recur, root.children))
        logging.debug('\nTrying out all possible children suits:')
        for choice, children_suit in enumerate(all_children_suits):
            res = root.clone()
            for n in children_suit:
                res.kattach(n.clone())
            logging.debug('\nAttached children suit:')
            logging.debug(rt(res))
            assert(res.is_complete())
            logging.debug('\nLet\'s yield from the finishing phase:')
            yield res
    else:
        logging.debug('\nGreat! No children missing')
        logging.debug('Let\'s yield the root from the finishing phase:')
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


LEVEL_CAP = 4
for t in kenumerate(root=start, max_dep=LEVEL_CAP):
    logging.info('\nRETURNED {}'.format(anytree.RenderTree(t)))
