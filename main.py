from kset import *
from misc import *
from khoa_math import *
from type_mgr import *
from type_data import *
from rel import *
from call_tree import *

import anytree, anytree.exporter
import timeit
from typing import Set, Iterable, FrozenSet, Union
from itertools import product, starmap
from functools import partial, reduce
import sys, logging, traceback
from graphviz import Digraph


# Handler that writes debugs to a file
debug_handler = logging.FileHandler(filename='logs/debug.log', mode='w+')
debug_handler.setFormatter(logging.Formatter('%(message)s'))
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


def kenum(root: ATMO, max_dep: int, orig=None):
    orig.log(30*'#'); orig.log('Welcome to kenum!')
    orig.log('The root is:'); orig.log_t(root)
    if root.legit:
        orig.log('Node already legit, yielding!')
        yield root.clone()
    else:
        if type(root) == Atom and max_dep >= 0:
            orig.log('It\'s an atom')
            if root.vals.is_explicit():
                for val in root.vals:
                    res = root.clone()
                    res.vals = KSet({val})
                    res.legit = True
                    orig.log('Yielding this atom:'); orig.log_t(res)
                    yield res
            else:
                raise KEnumError(root)

        else:
            orig.log('It\'s a molecule')

            orig.log('Let\'s go to Formation Phase')
            for well_formed in form_p(root=root, max_dep=max_dep, orig=orig):
                this_wf_orig = orig.branch(['Chosen this from Formation phase'])
                this_wf_orig.log_t(well_formed)
                this_wf_orig.log('Let\'s go to Relation Phase')

                rels = cons_dic[well_formed.type][well_formed.con].rels
                rel_iter_ = iter(rels)
                for relationed in repeat_rel_p(
                        root=well_formed, rel_iter=rel_iter_, max_dep=max_dep, orig=this_wf_orig):
                    this_rel_orig = this_wf_orig.branch(['Chosen this from Relation Phase:'])
                    this_rel_orig.log_t(relationed)
                    this_rel_orig.log('Let\'s go to Finishing Phase')

                    for finished in fin_p(root=relationed, max_dep=max_dep, orig=this_rel_orig):
                        this_fin_orig = this_rel_orig.branch(['Chosen this from Finishing Phase:'])
                        this_fin_orig.log_t(finished)
                        this_fin_orig.log('All phases are complete, yielding from main')
                        final = finished.clone(); final.legit = True
                        yield final


def form_p(root, max_dep, orig):
    """Assure that the root is well-formed (for one immediate level)"""
    orig.log('#'*30); orig.log('Welcome to Formation Phase')
    cons = root.cons & KSet(cons_dic[root.type].keys())
    orig.log('Possible constructors after unified are: {}'.format(cons))
    orig.log('Exploring all constructors')
    for con in cons:
        con_orig = orig.branch(['Chosen constructor {}'.format(con)])
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
        con_orig.log('Attached all components')
        con_orig.log_t(res)

        con_orig.log('Yielding from constructor phase')
        yield res


def rel_p(root: Mole, max_dep, rel, orig):
    """Apply all relation `rel` to aid in root enumeration"""
    orig.log('#'*30); orig.log('Welcome to Relation Phase')

    orig.log('Working with relation {}'.format(rel))
    if rel.type == RelT.FUN:
        orig.log('It\'s a functional relation')
        for res in _fun_rel(root=root, max_dep=max_dep, rel=rel, orig=orig):
            yield res
    elif rel.type == RelT.UNION:
        orig.log('It\'s a union relation')
        for res in _uni_rel(root=root, max_dep=max_dep, rel=rel, orig=orig):
            yield res


def _fun_rel(root, max_dep, rel, orig):
    in_roots = [root.get_path(car(path)) for path in rel.get('in')]
    orig.log('The inputs needed are:')
    for in_root in in_roots:
        orig.log_t(in_root)

    nl_ins = (kenum(root=i, max_dep=max_dep-1, orig=orig) for i in in_roots if not i.legit)
    # What would happen if some of those inputs' roots aren't legit?
    # Then we would yield nothing
    for in_legit in product(*nl_ins):
        m_in_orig = orig.branch(['Chosen a new input suit'])
        res = root.clone()
        for inp in in_legit:
            res.kattach(inp.clone())
        m_in_orig.log('Attached input suit:'); m_in_orig.log_t(res)

        function = rel.get('fun')
        get_val_of_path = lambda p: res.get_path(p).val
        arguments = map(get_val_of_path, rel.get('in'))
        output = function(*arguments)

        out_atom = Atom(role=rcar(rel.get('out')), vals=KSet({output}))
        res.kattach(node=out_atom, path=rcdr(rel.get('out')))
        m_in_orig.log('Attached output:')
        m_in_orig.log_t(res)
        m_in_orig.log('Yielding!')
        yield res


def _uni_rel(root, rel, max_dep, orig):
    orig.log('Try enumerating the superset part')
    super_path, subs_path = rel.get('uni'), rel.get('subs')
    super_root = root.get_path(car(super_path))
    subs_root = [root.get_path(car(path)) for path in subs_path]
    try:
        for uni_legit in kenum(
                root=super_root, max_dep=max_dep-1, orig=orig):
            rc = root.clone()
            rc.kattach(uni_legit)
            uni_orig = orig.branch(['Chosen the superset part:']); uni_orig.log_t(rc)
            uni_orig.log('Updating the subsets')
            for sub_path in subs_path[:-1]:
                a = Atom(role=rcar(sub_path), vals=KSet(content=powerset(uni_legit.val)))
                rc.kattach(a, path=rcdr(sub_path))
            uni_orig.log('Result is'); uni_orig.log_t(rc)
            uni_orig.log('Now we are ready to enumerate the subsets')
            sub_roots_legit = (
                kenum(root=s, max_dep=max_dep-1, orig=orig) for s in subs_root[:-1] if not s.legit)
            for sub_roots_legit in product(*sub_roots_legit):
                sub_orig = uni_orig.branch(['Chosen subsets (except for the last)'])
                res = rc.clone()
                for sub_root_legit in sub_roots_legit:
                    res.kattach(sub_root_legit)
                sub_orig.log('Attached those:'); sub_orig.log_t(res)
                subsets_so_far = (res.get_path(path).val for path in subs_path[:-1])  # type: (frozen)set
                union_so_far = reduce(lambda x, y: x | y, subsets_so_far)  # type: (frozen)set
                leftover = uni_legit.val - union_so_far  # type: (frozen)set
                val_for_last = KSet((leftover | x for x in powerset(union_so_far)))
                last_atom = Atom(role=rcar(subs_path[-1]), vals=val_for_last)
                res.kattach(last_atom, path=rcdr(subs_path[-1]))
                sub_orig.log('Attached the union:'); sub_orig.log_t(res)
                yield res

    except KEnumError:
        orig.log('Well, that didn\'t work')
        orig.log('Then it must mean that the subsets are known')
        sub_roots_legit = (
                kenum(root=s, max_dep=max_dep-1, orig=orig) for s in subs_root if not s.legit)
        for sub_roots_legit in product(*sub_roots_legit):
            sub_orig = orig.branch(['Chosen subsets'])
            res = root.clone()
            for sub_root_legit in sub_roots_legit:
                res.kattach(sub_root_legit)
            sub_orig.log('Attached those:')
            sub_orig.log_t(res)
            subsets = (res.get_path(path).val for path in subs_path)  # type: list of (frozen)set
            superset = reduce(lambda x, y: x | y, subsets)  # type: (frozen)set
            super_atom = Atom(role=rcar(super_path), vals=KSet({superset}))
            res.kattach(super_atom, path=rcdr(super_path))
            sub_orig.log('Attached the union:'); sub_orig.log_t(res)
            yield(res)


def repeat_rel_p(root, max_dep, rel_iter, orig):
    try:
        this_rel = next(rel_iter)
        for new_root in rel_p(
                root=root, max_dep=max_dep, rel=this_rel, orig=orig):
            choice_orig = orig.branch(['Chosen '])
            choice_orig.log_t(new_root)
            for res in repeat_rel_p(new_root, max_dep, rel_iter, choice_orig):
                yield res
    except StopIteration:
        orig.log('No more relations, yielding')
        yield root.clone()


def fin_p(root, max_dep, orig):
    """Enumerate all children that haven't been enumerated"""
    orig.log('#'*30); orig.log('We are now in Finishing Phase')
    m_children_enum = []
    for child in root.children:
        if not child.legit:
            m_children_enum.append(kenum(child, max_dep = max_dep-1, orig=orig))

    m_children_suits = product(*m_children_enum)
    for m_children_suit in m_children_suits:
        m_children_suit_orig = orig.branch(['Chosen a new children suit'])
        res = root.clone()
        for n in m_children_suit:
            res.kattach(n.clone())
        m_children_suit_orig.log('Attached children suit:')
        m_children_suit_orig.log_t(res)
        m_children_suit_orig.log('Let\'s yield!')
        yield res


start = Mole(role='root', type_ = 'UNI')


LEVEL_CAP = 3
debug_root = LogNode(['Start Debug'])  # For describing the program execution
info_root = LogNode(['Start Info'])  # For output
start_time = timeit.default_timer()
try:
    for t in kenum(root=start, max_dep=LEVEL_CAP, orig=debug_root):
        info_root.log('RETURNED:'); info_root.log_t(t)
finally:
    stop_time = timeit.default_timer()
    # Writing logs
    logging.info("Program Executed in {} seconds".format(stop_time - start_time))
    logging.debug(render_log(debug_root))
    logging.info(render_log(info_root))

# Got some sick graphs, too:
# anytree.exporter.DotExporter(debug_root).to_dotfile('logs/debug.dot')
