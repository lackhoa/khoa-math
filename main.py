from kset import *
from misc import *
from khoa_math import *
from type_data import *
from rel import *
from call_tree import *

import anytree
import timeit
from typing import Set, Iterable, FrozenSet, Union
from itertools import product, starmap
from functools import partial, reduce
import sys, logging, traceback


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
    def __init__(self, thing: Union[Mole, KSet]):
        self.message = 'Cannot enumerate this thing'
        self.thing = thing


def kenum(root: Union[Mole, KSet],
          max_dep: int,
          orig: LogNode):
    orig.log(30*'#'); orig.log('Welcome to kenum!')
    orig.log('The root is:'); orig.log_m(root)

    if type(root) == KSet:
        orig.log('It\'s an atom')
        if max_dep >= 0:
            if root.is_explicit():
                for val in root:
                    orig.log('Yielding this value: {}'.format(val))
                    yield KSet({val})
            else:
                orig.log('Can\'t get any value for it')
                raise KEnumError(root)
        else:
            orig.log('But we do not have enough level left (how did it happen?)')
            return

    elif type(root) == Mole:
        orig.log('It\'s a molecule')
        if 'legit' in root:
            orig.log('Molecule already legit, yielding!')
            yield root

        orig.log('Let\'s go to Formation Phase')
        for well_formed in form_p(root=root, max_dep=max_dep, orig=orig):
            this_wf_orig = orig.branch(['Chosen this from Formation phase'])
            this_wf_orig.log_m(well_formed)
            this_wf_orig.log('Let\'s go to Relation Phase')

            rels = cons_dic[well_formed.type][well_formed.con].rels
            rel_iter_ = iter(rels)
            for relationed in repeat_rel_p(
                    root=well_formed, rel_iter=rel_iter_, max_dep=max_dep, orig=this_wf_orig):
                this_rel_orig = this_wf_orig.branch(['Chosen this from Relation Phase:'])
                this_rel_orig.log_m(relationed)
                this_rel_orig.log('Let\'s go to Finishing Phase')

                for finished in fin_p(root=relationed, max_dep=max_dep, orig=this_rel_orig):
                    this_fin_orig = this_rel_orig.branch(['Chosen this from Finishing Phase:'])
                    this_fin_orig.log_m(finished)
                    this_fin_orig.log('All phases are complete, yielding from main')
                    finished['legit'] = KSet({True})
                    yield finished


def form_p(root, max_dep, orig):
    """Assure that the root is well-formed"""
    orig.log('#'*30); orig.log('Welcome to Formation Phase')
    cons = root['_cons'] & KSet(cons_dic[root.type].keys())
    orig.log('Possible constructors after unified are: {}'.format(cons))
    orig.log('Exploring all constructors')
    for con in cons:
        con_orig = orig.branch(['Chosen constructor {}'.format(con)])
        res = root.clone()
        res.con = con
        form, rels = cons_dic[root.type][con]

        if max_dep == 1 and any(map(lambda x: type(x) is Mole, form.values())):
            con_orig.log('Out of level, try another constructor')
            continue

        con_orig.log('Alright! We still have enough level for this molecule')
        ill_formed = False
        if (res.keys()-form.keys()) != set():
            con_orig.log('This molecule does not fit to this constructor')
            continue
        else: con_orig.log('Good, there is no redundant keys')

        res.merge(form)
        con_orig.log('Attached all components')
        con_orig.log_m(res)

        con_orig.log('Yielding from constructor phase')
        yield res


def rel_p(root, max_dep, rel, orig):
    """Apply relation `rel` to aid in enumeration"""
    orig.log('#'*30); orig.log('Welcome to Relation Phase')

    orig.log('Working with relation \"{}\"'.format(rel))
    if rel.type == 'FUN':
        orig.log('It\'s a functional relation')
        for res in _fun_rel(root=root, max_dep=max_dep, rel=rel, orig=orig):
            yield res
    elif rel.type == 'UNION':
        orig.log('It\'s a union relation')
        for res in _uni_rel(root=root, max_dep=max_dep, rel=rel, orig=orig):
            yield res
    elif rel.type == 'ISO':
        orig.log('It\'s an isomorphic relation')
        for res in _iso_rel(root=root, max_dep=max_dep, rel=rel, orig=orig):
            yield res


def _fun_rel(root, max_dep, rel, orig):
    in_paths, out_path = rel['inp'], rel['out']
    in_roles = [car(path) for path in in_paths]
    orig.log('The inputs needed are:')
    for role in in_roles:
        orig.log(root[role])

    legit_ins = [kenum(root=root[role], max_dep=max_dep-1, orig=orig) for role in in_roles]
    for legit_in in product(*legit_ins):
        in_orig = orig.branch(['Chosen a new input suit'])
        res = root.clone()
        for index, inp in enumerate(legit_in):
            res.merge(inp, path=in_roles[index])  # The index is preserved
        in_orig.log('Attached input suit:'); in_orig.log_m(res)

        arguments = [res.get_path(path) for path in in_paths]
        output = rel['fun'](*arguments)

        res.merge(val=output, path=out_path)
        in_orig.log('Attached output:')
        in_orig.log_m(res)
        in_orig.log('Yielding!')
        yield res


def _iso_rel(root, rel, max_dep, orig):
    orig.log('Try left to right first')
    orig.log('Delegating work for the functional module')
    Lr_fun, rL_fun = rel['Lr_fun'], rel['rL_fun']
    left,   right  = rel['left'], rel['right']
    try:
        Lr_rel = Rel('FUN', Lr_fun, left, right)
        for res in _fun_rel(root=root, rel=Lr_rel, max_dep=max_dep, orig=orig):
            yield res
    except KEnumError:
        orig.log('Left to right did not work, how about right to left?')
        orig.log('Delegating work for the functional module')
        rL_rel = Rel('FUN', rL_fun, right, left)
        for res in _fun_rel(root=root, rel=rL_rel, max_dep=max_dep, orig=orig):
            yield res


def _uni_rel(root, rel, max_dep, orig):
    orig.log('Try enumerating the superset part')
    super_path, subs_path = rel['uni'], rel['subs']
    super_role, subs_role = car(super_path), [car(path) for path in subs_path]
    try:
        for uni_legit in kenum(
                root=root[super_role], max_dep=max_dep-1, orig=orig):
            rc = root.clone()
            rc.merge(uni_legit, path=[super_role])
            uni_orig = orig.branch(['Chosen the superset part:']); uni_orig.log_m(rc)
            for sub_path in subs_path[:-1]:
                rc.merge(powerset(uni_legit), path=sub_path)
            uni_orig.log('Updated the subsets')
            uni_orig.log('Result is'); uni_orig.log_m(rc)

            uni_orig.log('Now we are ready to enumerate the subsets')
            legit_subs = (
                kenum(root=rc[sub_role], max_dep=max_dep-1, orig=orig)\
                for sub_role in subs_role[:-1])
            for sub_suit in product(*legit_subs):
                sub_orig = uni_orig.branch(['Chosen subsets (except for the last)'])
                res = rc.clone()
                for i, v in enumerate(sub_suit):
                    res.merge(sub_root_legit, path=subs_role[i])
                sub_orig.log('Attached those:'); sub_orig.log_m(res)
                subsets_so_far = (res[role] for role in subs_path[:-1])  # type: (frozen)set
                union_so_far = reduce(lambda x, y: x | y, subsets_so_far)  # type: (frozen)set
                leftover = uni_legit - union_so_far  # type: (frozen)set
                val_for_last = KSet((leftover | x for x in powerset(union_so_far)))
                res.merge(val_for_last, path=subs_path[-1])
                sub_orig.log('Attached the union:'); sub_orig.log_m(res)
                yield res

    except KEnumError:
        orig.log('Well, that didn\'t work')
        orig.log('Then it must mean that the subsets are known')
        sub_roots_legit = (
                kenum(root=s, max_dep=max_dep-1, orig=orig) for s in subs_root)
        for sub_roots_legit in product(*sub_roots_legit):
            sub_orig = orig.branch(['Chosen subsets'])
            res = root.clone()
            for index, sub_root_legit in enumerate(sub_roots_legit):
                res.merge(sub_root_legit, path=subs_root[index])
            sub_orig.log('Attached those:'); sub_orig.log_m(res)
            subsets = (res.get_path(path) for path in subs_path)  # type: list of (frozen)set
            superset = reduce(lambda x, y: x | y, subsets)  # type: (frozen)set
            res.merge(superset, path=super_path)
            sub_orig.log('Attached the union:'); sub_orig.log_m(res)
            yield(res)


def repeat_rel_p(root, max_dep, rel_iter, orig):
    try:
        this_rel = next(rel_iter)
        for new_root in rel_p(
                root=root, max_dep=max_dep, rel=this_rel, orig=orig):
            choice_orig = orig.branch(['Chosen '])
            choice_orig.log_m(new_root)
            for res in repeat_rel_p(
                root=new_root, max_dep=max_dep, rel_iter=rel_iter, orig=choice_orig):
                yield res
    except StopIteration:
        orig.log('No more relations left, yielding')
        yield root

def fin_p(root, max_dep, orig):
    """Enumerate all children that haven't been enumerated"""
    orig.log('#'*30); orig.log('We are now in the Finishing Phase')
    all_keys = list(root.keys())
    m_children_enum = [
        kenum(root=root[key], max_dep=max_dep-1, orig=orig) for key in all_keys]
    m_children_suits = product(*m_children_enum)
    for m_children_suit in m_children_suits:
        m_children_suit_orig = orig.branch(['Chosen a new children suit'])
        res = root.clone()
        for index, child in enumerate(m_children_suit):
            res[all_keys[index]] = child
        m_children_suit_orig.log('Attached children suit:')
        m_children_suit_orig.log_m(res)
        m_children_suit_orig.log('Let\'s yield!')
        yield res


def main():
    p = Mole(type_='WFF', con='ATOM', _text=KSet({'P'}))
    q = Mole(type_='WFF', con='ATOM', _text=KSet({'Q'}))
    and_intro_root = Mole(type_='PROOF', dep=KSet(frozenset({p, q})))

    LEVEL_CAP = 3
    start_roots = [Mole(type_ = 'WFF_TEST'),]
                   # Mole(type_ = 'UNI'),
                   # Mole(type_ = 'PROOF_TEST'),
                   # Mole(type_ = 'ISO_TEST'),
                   # and_intro_root]
    debug_root = LogNode(['Start Debug'])  # For describing the program execution
    info_root = LogNode(['Start Info'])  # For output
    start_time = timeit.default_timer()
    try:
        for i, start in enumerate(start_roots[:]):
            for j, t in enumerate(kenum(root=start, max_dep=LEVEL_CAP, orig=debug_root)):
                info_root.log('{}. RETURNED ({}):'.format(i, j))
                info_root.log_m(t)
    finally:
        # Write down logs even after failure
        stop_time = timeit.default_timer()
        logging.info("Program Executed in {} seconds".format(stop_time - start_time))
        logging.debug(render_log(debug_root))
        logging.info(render_log(info_root))

main()
