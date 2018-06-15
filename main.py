from kset import *
from misc import *
from khoa_math import *
from type_mgr import *
from type_data import *
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


class KEnumError(Exception):
    def __init__(self, node):
        self.message = 'Cannot enumerate this node'
        self.node = node


def kenum(root: ATMO, max_dep: int, phase=0, orig=None):
    if phase == 0:
        orig.log(30*'#'); orig.log('Welcome to kenum!')
        orig.log('The root is:', root.clone())
    if type(root) == Atom and max_dep >= 0:
        orig.log('It\'s an atom')
        if root.vals.is_explicit():
            for val in root.vals:
                res = root.clone()
                res.vals = KSet({val})
                orig.log('Yielding this atom:', res.clone())
                yield res
        else:
            raise KEnumError(self)

    else:
        if phase == 0:
            orig.log('It\'s a molecule')

        orig.log('Let\'s go to Formation Phase')
        for well_formed in form_p(root=root, max_dep=max_dep, orig=orig):
            this_wf_orig = orig.branch('Chosen this from Formation phase')
            this_wf_orig.log(txt='CHOICE', tree=well_formed.clone())
            this_wf_orig.log('Let\'s go to Relation Phase')

            rels = cons_dic[well_formed.type][well_formed.con].rels
            rel_iter = iter(rels)
            def repeat_rel_p(tree):
                nonlocal this_wf_orig, max_dep, rel_iter
                try:
                    this_rel = next(rel_iter)
                    for new_tree in rel_p(
                            root=root, max_dep=max_dep rel=this_rel, orig=this_wf_orig):
                        choice_orig = this_wf_orig.branch('Chosen ')
                        for res in repeat_rel_p(new_tree):
                            yield res
                except StopIteration:
                    yield node.clone()

            for relationed in repeat_rel_p(this_wf_orig):
                this_rel_orig = this_wf_orig.branch('Chosen this from Relation Phase:')
                this_rel_orig.log(txt='CHOICE', tree=relationed.clone())
                this_rel_orig.log('Let\'s go to Finishing Phase')

                for finished in fin_p(root=relationed, max_dep=max_dep, orig=this_rel_orig):
                    this_fin_orig = this_rel_orig.branch('Chosen this from Finishing Phase:')
                    this_fin_orig.log(txt='CHOICE', tree=finished.clone())
                    this_fin_orig.log('All phases are complete, yielding from main')
                    yield finished.clone()


def form_p(root, max_dep, orig):
    """Assure that the root is well-formed (for one immediate level)"""
    orig.log('#'*30); orig.log('Welcome to Formation Phase')
    cons = root.cons & KSet(cons_dic[root.type].keys())
    orig.log('Possible constructors after unified are: {}'.format(cons))
    orig.log('Exploring all constructors')
    for con in cons:
        con_orig = orig.branch('Chosen constructor {}'.format(con))
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
        con_orig.log('Attached all missing components', res.clone())

        con_orig.log('Yielding from constructor phase')
        yield res


def rel_p(root: Mole, max_dep, rel, orig=None):
    """Apply all relation `rel` to aid in root enumeration"""
    orig.log('#'*30); orig.log('Welcome to Relation Phase')

    orig.log('Working with relation {}'.format(rel))
    if rel.type == RelT.FUN:
        orig.log('It\'s a functional relation')
        in_args = [root.get_path(slot) for slot in rel.get('in')]

        orig.log('The inputs needed are:'); orig.log(in_args)

        in_args_enum = []
        for in_arg in in_args:
            in_arg_enum_orig = orig.log('Will enumerating argument {}'.format(in_arg))
            in_args_enum.append(kenum(in_arg, max_dep = max_dep-1, orig=orig))

        input_suits = product(*in_args_enum)
        for input_suit in input_suits:
            input_suit_orig = orig.branch('Chosen a new input suit')
            res = root.clone()
            for inp in input_suit:
                res.kattach(inp.clone())
            input_suit_orig.log('Attached input suit:', res.clone())

            function = rel.get('fun')
            get_first_of_path = lambda p: res.get_path(p).vals[0]
            arguments = map(get_first_of_path, rel.get('in'))
            output = function(*arguments)

            out_atom = Atom(role=car(rel.get('out')), vals=KSet({output}))
            res.kattach(node=out_atom, path=cdr(rel.get('out')))
            input_suit_orig.log('Attached output:', res.clone())
            input_suit_orig.log('Yielding!')
            yield res

    elif res.type == RelT.UNION:
        orig.log('It\'s a union!')
        orig.log('Try enumerating the union part')
        uni_path, subs_path = rel.get('uni'), rel.get('subs')
        uni_node = root.get_path(car(uni_path))
        try:
            for uni_compl in kenum(
                    root=uni_node, max_dep=max_dep-1, orig=orig):
                uni_orig = orig.branch('Chosen union:')
                power = powerset(uni_compl.values[0])
                subs_root = [root.get_path(car(path)) for path in subs_path]
                bunch_of_shit = product(power, repeat=len(subs_path)-1)
                for vs in vss:
                    origin.log('Chosen a new set of values')
                    for i, v in enumerate(vs):
                        subs_root[i].values = v
                    uni_fun = lambda x, y: x & y
                    union_kset = reduce(uni_fun, vs)
                    leftover = uni_compl.val - union_kset
                    subs_root[-1].vals = KSet({leftover})

                subs_root_unified = (sub_root &  for sub_root in subs_root)

        except KEnumError:


def fin_p(root, max_dep, orig):
    """Enumerate all children that haven't been enumerated"""
    orig.log('#'*30); orig.log('We are now in Finishing Phase')
    if [n for n in root.children if not n.is_complete()]:
        orig.log('There are incomplete children')
        children_enum = []
        for child in root.children:
            orig.log('Enumerating child {}'.format(child))
            children_enum.append(kenum(child, max_dep = max_dep-1, orig=orig))

        all_children_suits = product(*children_enum)
        for children_suit in all_children_suits:
            children_suit_orig = orig.branch('Chosen a new children suit')
            res = root.clone()
            for n in children_suit:
                res.kattach(n.clone())
            children_suit_orig.log('Attached children suit:', res.clone())
            assert(res.is_complete())
            children_suit_orig.log('Confirmed that the tree is complete')
            children_suit_orig.log('Let\'s yield!')
            yield res
    else:
        orig.log('Great! No children missing')
        orig.log('Let\'s yield!')
        yield root.clone()


start = Mole(role='root', type_ = 'WFF_TEST', cons = KSet({'ATOM', 'NEGATION', 'CONDITIONAL'}))


LEVEL_CAP = 3
debug_root = LogNode('Start Debug')  # For describing the program run
info_root = LogNode('Start Info')  # For output
for t in kenum(root=start, max_dep=LEVEL_CAP, orig=debug_root):
    info_root.log('RETURNED:', t.clone())

# Writing logs
logging.debug(render_log(debug_root))
logging.info(render_log(info_root))

# Got some sick graphs, too:
# anytree.exporter.DotExporter(debug_root).to_dotfile('logs/debug.dot')
