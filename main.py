from kset import *
from misc import *
from khoa_math import *
from type_mgr import *
from type_data import *
from wff import *
from rel import *
from call_tree import *

import anytree, anytree.exporter
from typing import Set, Iterable, FrozenSet, Union
from itertools import product, starmap
from functools import partial
import sys, logging, traceback
from graphviz import Digraph


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


def rt(t): return str(anytree.RenderTree(t))


def kenum(root: ATMO, max_dep: int, phase=0, orig=None):
    if phase == 0:
        orig.log(30*'#'); orig.log('Welcome to kenum!')
        orig.log_rt('The root is:', root)
    if type(root) == Atom and max_dep >= 0:
        orig.log('It\'s an atom')
        vals_orig = orig.call('Considering all potential values')
        if root.vals.is_explicit():
            for val in root.vals:
                res = root.clone()
                res.vals = KSet({val})
                vals_orig.log_rt('Chosen a new value for the atom:', res)
                vals_orig.log('Yielding this atom')
                yield res
        else:
            raise Exception('What the hell am I supposed to loop through now?')

    else:
        if phase == 0:
            orig.log('It\'s a molecule')

        phases = (con_p, rel_p, fin_p)
        if phase == len(phases):
            orig.log('All phases are complete, yielding from main')
            yield root.clone()
        else:
            this_phase_orig = orig.call('Let\'s get to phase {}'.format(phase))
            for new_root in phases[phase](root=root, max_dep=max_dep, orig=this_phase_orig):
                next_phases_orig = orig.call('To the next phases we go!')
                for res in kenum(new_root, max_dep, phase+1, next_phases_orig):
                    yield res


def con_p(root, max_dep, orig):
    """Assure that the root is well-formed (for one immediate level)"""
    orig.log('#'*30); orig.log('Welcome to Constructor phase')
    cons = root.cons & KSet(cons_dic[root.type].keys())
    orig.log('Possible constructors after unified are: {}'.format(cons))
    orig.log('Exploring all constructors')
    for con in cons:
        con_orig = orig.call('Chosen constructor {}'.format(con))
        res = root.clone()
        res.cons = KSet({con})
        args, rels = cons_dic[root.type][con]

        if max_dep == 1 and any(map(lambda x: type(x) is Mole, args)):
            con_orig.log('Out of level, try another constructor')
            continue

        con_orig.log('We still have enough level for this molecule')
        ill_formed = False
        for child in res.children:
            if child.role not in [arg.role for arg in args]:
                ill_formed = True; break
        if ill_formed:
            con_orig.log('This molecule has too many children for this constructor')
            continue
        else: con_orig.log('Good, there is no redundant components')

        for arg in args:
            res.kattach(arg)
        con_orig.log_rt('Attached all missing components', res)

        con_orig.log('Yielding from constructor phase')
        yield res


def rel_p(root: Mole, max_dep, orig=None):
    """Apply all relations to root"""
    orig.log('#'*30); orig.log('Welcome to Relation phase')
    rels = cons_dic[root.type][root.cons[0]].rels

    if rels:
        for rel in rels:
            rel_orig = orig.call('Working with relation {}'.format(rel))
            if rel.type == RelT.FUN:
                rel_orig.log('It\'s a functional relation')
                in_args = []
                for slot in rel.get('in'):
                    in_args += [n for n in root.children if n.role == car(slot)]

                rel_orig.log('The inputs needed are:'); rel_orig.log(in_args)

                in_args_enum = []
                for in_arg in in_args:
                    in_arg_enum_orig = rel_orig.call('Enumerating argument {}'.format(in_arg))
                    in_args_enum.append(kenum(in_arg, max_dep = max_dep-1, orig=in_arg_enum_orig))

                input_suits = product(*in_args_enum)
                for input_suit in input_suits:
                    res = root.clone()
                    for inp in input_suit:
                        res.kattach(inp)
                    input_suit_orig = rel_orig.call('Chosen input suit: {}'.format(input_suit))
                    input_suit_orig.log_rt('Attached input suit:', res)

                    get_first_of_path = lambda p: res.get_path(p).vals[0]
                    output = rel.get('fun')\
                            (*map(get_first_of_path, rel.get('in')))
                    out_atom = Atom(role=car(rel.get('out')), vals=KSet({output}))
                    res.kattach(node=out_atom, path=cdr(rel.get('out')))
                    input_suit_orig.log_rt('Attached output:', res)
                    input_suit_orig.log('Yielding!')
                    yield res
    else:
        orig.log('There are no relations, yielding right now')
        yield root.clone()


def fin_p(root, max_dep, orig):
    """Enumerate all children that haven't been enumerated"""
    orig.log('#'*30); orig.log('We are now in Finishing phase')
    if [n for n in root.children if not n.is_complete()]:
        orig.log('There are incomplete children')
        enum_children_orig = orig.call('Calling kenum to find possible children suits:')
        recur = partial(kenum, max_dep = max_dep-1, orig=enum_children_orig)

        children_enum = []
        for child in root.children:
            child_orig = orig.call('Enumerating child {}'.format(child))
            children_enum.append(kenum(child, max_dep = max_dep-1, orig=child_orig))

        all_children_suits = product(*children_enum)
        for children_suit in all_children_suits:
            res = root.clone()
            for n in children_suit:
                res.kattach(n.clone())
            child_orig = orig.call('Chosen children suit: {}'.format(children_suit))
            child_orig.log_rt('Attached children suit:', res)
            assert(res.is_complete())
            child_orig.log('Confirmed that the tree is complete')
            child_orig.log('Let\'s yield!')
            yield res
    else:
        orig.log('Great! No children missing')
        orig.log('Let\'s yield!')
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
debug_root = LogNode('Start Debug')  # For describing the program run
info_root = LogNode('Start Info')  # For output
for t in kenum(root=start, max_dep=LEVEL_CAP, orig=debug_root):
    info_root.log_rt('RETURNED:', t)

# Writing logs
logging.debug(str(rt(debug_root)))
logging.info(str(rt(info_root)))

# Got some sick graphs, too:
# anytree.exporter.DotExporter(debug_root).to_dotfile('logs/debug.dot')
