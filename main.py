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
import sys, logging, traceback



# Handler that writes debugs to a file
debug_handler = logging.FileHandler(filename='logs/debug.log', mode='w+')
debug_handler.setFormatter(IndentFormatter('%(indent)s%(function)s: %(message)s'))
debug_handler.setLevel(logging.DEBUG)

# Handler that writes info messages or higher to the sys.stderr
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
console_handler.setLevel(logging.INFO)

# Configure the root logger
logging.basicConfig(handlers = [console_handler, debug_handler], level = logging.DEBUG)


def custom_traceback(exc, val, tb):
    print('\n'.join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def rt(t): return anytree.RenderTree(t)


def kenum(root: ATMO, max_dep: int, phase=0, trace:tuple = (),):
    logging.debug('#'*30)
    logging.debug('Main function here!')
    logging.debug('The root is:\n{}'.format(rt(root)))
    if type(root) == Atom and max_dep >= 0:
        logging.debug('It\'s an atom')
        logging.debug('Considering all potential values')
        if root.vals.is_explicit():
            for choice, val in enumerate(root.vals):
                new_trace = trace + (chr(97+choice),)
                res = root.clone()
                res.vals = KSet({val})
                logging.debug('Got new value: {}:\n{}'.format(val, rt(res)))
                logging.debug('Current trace is: {}'.format('.'.join(new_trace)))
                logging.debug('Yielding this atom')
                yield res
        else:
            raise Exception('What the hell am I supposed to loop through now?')

    elif max_dep == 0:
        logging.debug('It\'s a molecule, but we ran out of level')
    else:
        logging.debug('It\'s a molecule')
        phases = (con_p, rel_p, fin_p)
        if phase == len(phases):
            logging.debug('All phases are complete, yielding from main')
            yield root.clone()
        else:
            logging.debug('Let\'s get to phase {}'.format(phase))
            for choice, new_root in enumerate(phases[phase](root=root, max_dep=max_dep, trace=trace)):
                new_trace = trace + (chr(97+choice),)
                logging.debug('Current trace is: {}'.format('.'.join(new_trace)))
                logging.debug('To the next phases we go!')
                for res in kenum(new_root, max_dep, phase+1, trace):
                    yield res


def con_p(root, max_dep, trace):
    """Assure that the root is well-formed (for one immediate level)"""
    logging.debug('#'*30)
    logging.debug('Welcome to Constructor phase')
    cons = root.cons & KSet(cons_dic[root.type].keys())
    logging.debug('Possible constructors after unified are: {}'.format(cons))
    for choice, con in enumerate(cons):
        logging.debug('Current trace is: {}'.format('.'.join(trace)))
        logging.debug('Chosen constructor {}'.format(con))
        res = root.clone()
        res.cons = KSet({con})
        args, rels = cons_dic[root.type][con]

        if max_dep == 1 and any(map(lambda x: type(x) is Mole, args)):
            logging.debug('Out of level, try another constructor')
            continue

        logging.debug('We still have enough level for this molecule')
        ill_formed = False
        for child in res.children:
            if child.role not in [arg.role for arg in args]:
                ill_formed = True; break
        if ill_formed:
            logging.debug('This molecule has too many children for this constructor')
            continue
        else: logging.debug('Good, there is no redundant children')

        for arg in args:
            res.kattach(arg)
        logging.debug('Attached children according to constructor:\n{}'.format(rt(res)))

        logging.debug('Yielding from constructor phase')
        yield res


def rel_p(root: Mole, max_dep, trace, phase=0):
    """Apply all relations to root"""
    logging.debug('#'*30)
    logging.debug('Welcome to Relation phase')
    rels = cons_dic[root.type][root.cons[0]].rels
    try: rel = take_index(rels, phase)
    except IndexError:
        logging.debug('No more relations, relation phase over')
        logging.debug('Yielding from relation phase')
        yield root.clone()
        raise StopIteration

    logging.debug('Working with relation {}'.format(rel))
    if rel.type == RelT.FUN:
        logging.debug('It\'s a functional relation')
        in_args = []
        for slot in rel.get('in'):
            in_args += [n for n in root.children if n.role == car(slot)]

        logging.debug('The inputs needed are:')
        logging.debug(in_args)
        logging.debug('Let\'s see what input suits there are:')
        recur = partial(kenum, max_dep = max_dep-1)
        all_input_suits = product(*map(recur, in_args))
        for choice, input_suit in enumerate(all_input_suits):
            res = root.clone()
            for inp in input_suit: res.kattach(inp)
            logging.debug('Current trace is: {}'.format('.'.join(trace)))
            logging.debug('Attached input suit:\n{}'.format(rt(res)))

            get_first_of_path = lambda p: res.get_path(p).vals[0]
            output = rel.get('fun')\
                    (*map(get_first_of_path, rel.get('in')))
            out_atom = Atom(role=car(rel.get('out')), vals=KSet({output}))
            res.kattach(node=out_atom, path=cdr(rel.get('out')))
            logging.debug('Attached output:\n{}'.format(rt(res)))

            logging.debug('Let\'s see if there are other relations')
            for k in rel_p(res, max_dep=max_dep, phase=phase+1, trace=trace):
                yield k


def fin_p(root, max_dep, trace):
    """Enumerate all children that haven't been enumerated"""
    logging.debug('#'*30)
    logging.debug('We are now in Finishing phase')
    if [n for n in root.children if not n.is_complete()]:
        logging.debug('There are incomplete children')
        logging.debug('Trying out all possible children suits:')
        recur = partial(kenum, max_dep = max_dep-1)
        all_children_suits = product(*map(recur, root.children))
        for choice, children_suit in enumerate(all_children_suits):
            res = root.clone()
            for n in children_suit:
                res.kattach(n.clone())
            logging.debug('Current trace is: {}'.format('.'.join(trace)))
            logging.debug('Attached children suit:\n{}'.format(rt(res)))
            assert(res.is_complete())
            logging.debug('Let\'s yield from the finishing phase:')
            yield res
    else:
        logging.debug('Great! No children missing')
        logging.debug('Let\'s yield from the finishing phase:')
        yield root.clone()


tdic = {}
tdic['ATOM'] = CI(args=[Atom(role='text', vals=KSet({'P', 'Q'}))])
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
for t in kenum(root=start, max_dep=LEVEL_CAP):
    logging.info('RETURNED:\n{}'.format(anytree.RenderTree(t)))
