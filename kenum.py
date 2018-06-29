from misc import *
from khoa_math import *
from type_data import *
from rel import *
from call_tree import *
import glob

import anytree
from typing import *
from itertools import product, starmap

from functools import partial, reduce
import time


class KEnumError(Exception):
    pass
class InfinityError(KEnumError):
    def __init__(self, node):
        self.message = 'Cannot enumerate this node: {}'.format(node)
        self.node = node
class OutOfTimeError(KEnumError):
    def __init__(self, node):
        self.message = 'Out of time while enumerating this node'.format(node)
        self.node = node


class State:
    def __init__(self,
                 node: Union[Mole, Atom],
                 max_dep: int,
                 orig: LogNode,
                 deadline: float = None,
                 time_lim: float = None,
                 got_timeout: float = False):
        self.node, self.max_dep, self.orig, self.deadline, self.time_lim, self.got_timeout\
        = node, max_dep, orig, deadline, time_lim, got_timeout

    def clone(self, **kwargs):
        """Offer a shallow copy with custom modification"""
        res = State(self.node, self.max_dep, self.orig, self.deadline,
                    self.time_lim, self.got_timeout)
        for k in kwargs:
            setattr(res, k, kwargs[k])
        return res


def check_time(original_function):
    """
    Decorator: Check time before executing the function
    If out of time, raise OutOfTimeError
    """
    def new_function(*args,**kwargs):
        s = args[0]; assert type(s) is State
        if s.deadline is not None:
            if time.time() > s.deadline:
                s.orig.log('We\'re late by: {} s'.format(time.time()-s.deadline))
                raise OutOfTimeError(s.node)
            else:
                s.orig.log('Time until deadline: {}'.format(s.deadline-time.time()))
        return original_function(*args,**kwargs)
    return new_function


def time_man(orig_fun):
    """Decorator: Time Manager"""
    def new_fun(*args, **kwargs):
        INIT_TIME_LIM = 0.01
        COEF = 10  # To multiply the previous time limit
        s = args[0]
        while True:
            s.time_lim = INIT_TIME_LIM if s.time_lim is None else COEF*s.time_lim
            for res in orig_fun(*args, **kwargs):
                yield res
            if not s.got_timeout:
                break
            else:
                s.got_timeout = False
    return new_fun


def is_enumerable(mole):
    """Return False if the molecule is surely unenumerable given any depth"""
    def can_enumerate_type(type_: str):
        def is_base_constructor(con: str):
            res = True
            form = cons_dic[type_][con].form
            for val in form.values():
                if type(val) is Mole:
                    this_type = only(val['_types'])
                    if this_type == type_ or (not can_enumerate_type(this_type)):
                        res = False; break
                elif not val.is_explicit():
                    res = False; break
            return res

        all_constructors = cons_dic[type_].keys()
        return any(map(is_base_constructor, all_constructors))

    if any(map(lambda k: k not in ['_types', '_cons'], mole.keys())):
        return True
    else:
        return can_enumerate_type(only(mole['_types']))


@check_time
@time_man
def kenum(s: State):
    s.orig.log(30*'#'); s.orig.log('Welcome to kenum!')
    s.orig.log('The node is:'); s.orig.log_m(s.node)
    if type(s.node) == Atom:
        s.orig.log('It\'s an atom')
        if s.node.is_explicit():
            for val in s.node:
                s.orig.log('Yielding this value: {}'.format(wr(val)))
                yield wr(val)
        else:
            s.orig.log('Can\'t get any value for it')
            raise InfinityError(s.node)

    elif type(s.node) == Mole:
        s.orig.log('It\'s a molecule')

        if not is_enumerable(s.node):
            s.orig.log('This molecule is obviously unenumerable')
            raise InfinityError(s.node)
        else: s.orig.log('There is a hope for enumeration')

        if s.node in glob.legits:
            s.orig.log('Molecule already legit, yielding!')
            yield s.node
            return

        s.orig.log('Let\'s go to Formation Phase')
        for well_formed in form_p(s.clone(orig=s.orig.sub())):
            try:
                s.deadline = time.time() + s.time_lim
                this_wf_orig = s.orig.branch()
                this_wf_orig.log('Chosen this from Formation phase')
                this_wf_orig.log_m(well_formed)
                this_wf_orig.log('Let\'s go to Relation Phase')

                rels = cons_dic[only(well_formed['_types'])][only(well_formed['_cons'])].rels
                for partial_ in cycle_rel_p(s.clone(node=well_formed, orig=this_wf_orig.sub()), rels):
                    this_rel_orig = this_wf_orig.branch()
                    this_rel_orig.log('Chosen this from Relation Phase:')
                    this_rel_orig.log_m(partial_)
                    this_rel_orig.log('Let\'s go to Finishing Phase')

                    for finished in fin_p(s.clone(node=partial_, orig=this_rel_orig.sub())):
                        this_fin_orig = this_rel_orig.branch()
                        this_fin_orig.log('Chosen this from Finishing Phase:')
                        this_fin_orig.log_m(finished)
                        glob.legits.add(finished)
                        this_fin_orig.log('All phases are complete, yielding from kenum')
                        yield finished
            except OutOfTimeError:
                this_wf_orig.log('So we ran out of time on this constructor')
                s.got_timeout = True


def form_p(s: State):
    """Assure that the s.node is well-formed"""
    s.orig.log('#'*30); s.orig.log('Welcome to Formation Phase')
    assert(s.node['_types'].is_singleton()), 'How come the type is unknown?'
    s.node_type = only(s.node['_types'])
    cons = s.node['_cons'] & Atom(cons_dic[only(s.node['_types'])].keys())
    s.orig.log('Current constructor is: {}'.format(s.node['_cons']))
    s.orig.log('Possible constructors after unified are: {}'.format(cons))
    s.orig.log('Exploring all constructors')
    for con in cons:
        con_orig = s.orig.branch(); con_orig.log('Chosen constructor {}'.format(con))
        form, rels = cons_dic[only(s.node['_types'])][con]

        if s.max_dep == 1 and any(map(lambda x: type(x) is Mole, form.values())):
            con_orig.log('Out of depth, try another constructor')
            continue
        else:
            con_orig.log('Depth remaining: {}'.format(s.max_dep))

        res = s.node.clone()
        res['_cons'] = wr(con)
        res &= form
        con_orig.log('Attached all components')
        con_orig.log_m(res)
        if not res.is_inconsistent():
            con_orig.log('Consistent, yielding from formation phase')
            yield res
        else: con_orig.log('Inconsistent')


@check_time
@time_man
def cycle_rel_p(s: State, rels):
    for new_node, unchecked_rels in repeat_rel_p(
            s, iter(rels)):
        new_orig = s.orig.branch()
        new_orig.log('Chosen from `repeat_rel_p`:'); new_orig.log_m(new_node)
        if new_node == s.node:
            new_orig.log('`repeat_rel_p` didn\'t do anything')
            if unchecked_rels:
                new_orig.log('There are unchecked relations, which is bad')
                raise InfinityError(s.node)
            else:
                new_orig.log('All relations checked! Yielding:'); new_orig.log_m(s.node)
                yield s.node
        else:
            new_orig.log('Got new information!')
            if unchecked_rels:
                new_orig.log('Still got some relations, going to the next cycle')
                for res in cycle_rel_p(s.clone(node=new_node, orig=new_orig), unchecked_rels):
                    yield res
            else:
                new_orig.log('No more relations left, yielding this:'); new_orig.log_m(new_node)
                yield new_node


@check_time
def repeat_rel_p(s: State, rel_iter):
    try:
        this_rel = next(rel_iter)
    except StopIteration:
        s.orig.log('No more relations left, yielding')
        yield (s.node, ())
        return
    try:
        new_deadline = time.time() + s.time_lim
        for new_node in rel_p(s.clone(deadline=new_deadline), this_rel):
            choice_orig = s.orig.branch()
            choice_orig.log('Chosen '); choice_orig.log_m(new_node)
            choice_orig.log('Moving on to the next relation')
            rel_iter, new_rel_iter = tee(rel_iter)  # New path, new iterator
            for res, unchecked_rels in repeat_rel_p(
                    s.clone(node=new_node, orig=choice_orig), new_rel_iter):
                yield (res, unchecked_rels)
    except KEnumError as e:
        if type(e) is OutOfTimeError:
            s.orig.log('We ran out of time for this relation')
            s.got_timeout = True
        elif type(e) is InfinityError:
            s.orig.log('Cannot apply this relation (right now)')
        s.orig.log('Moving on to the next relation anyways')
        for res, unchecked_rels in repeat_rel_p(s, rel_iter):
            yield (res, (this_rel,)+unchecked_rels)


def rel_p(s: State, rel: Rel):
    """Apply relation `rel` to aid in enumeration"""
    s.orig.log('#'*30); s.orig.log('Welcome to Relation Phase')

    s.orig.log('Working with relation \"{}\"'.format(rel))
    if rel.type == 'FUN':
        s.orig.log('It\'s a functional relation')
        for res in _fun_rel(s, rel):
            yield res
    elif rel.type == 'UNION':
        s.orig.log('It\'s a union relation')
        for res in _uni_rel(s, rel):
            yield res


def _fun_rel(s: State, rel):
    in_paths, out_path = rel['inp'], rel['out']
    in_roles = [car(path) for path in in_paths]
    s.orig.log('The inputs\' nodes are:')
    for role in in_roles:
        s.orig.log_m(s.node[role])

    legit_ins = [kenum(s.clone(node    = s.node[role],
                               max_dep = s.max_dep-1,
                               orig    = s.orig.sub()))
                 for role in in_roles]
    for legit_in in product(*legit_ins):
        in_orig = s.orig.branch()
        in_orig.log('Chosen a new input suit')
        res = s.node.clone()
        for index, inp in enumerate(legit_in):
            res[in_roles[index]] &= inp
        in_orig.log('Attached input suit:'); in_orig.log_m(res)

        arguments = [res[path] for path in in_paths]
        output = rel['fun'](*arguments)

        res[out_path] &= output
        in_orig.log('Attached output:')
        in_orig.log_m(res)
        if not res.is_inconsistent():
            in_orig.log('Yielding!')
            yield res
        else:
            in_orig.log('Inconsistent')


def _uni_rel(s: State, rel):
    s.orig.log('Try enumerating the superset part')
    super_path, subs_path = rel['sup'], rel['subs']
    super_role, subs_role = car(super_path), [car(path) for path in subs_path]
    try:
        for uni_legit in kenum(s.clone(node    = s.node[super_role],
                                       max_dep = s.max_dep-1,
                                       orig    = s.orig.sub())):
            rc = s.node.clone()
            rc[super_role] &= uni_legit
            uni_orig = s.orig.branch()
            uni_orig.log('Chosen the superset part:'); uni_orig.log_m(rc)
            for sub_path in subs_path[:-1]:
                rc[sub_path] &= Atom(content=powerset(only(uni_legit)))
            uni_orig.log('Updated the subsets')
            uni_orig.log('Result is'); uni_orig.log_m(rc)

            uni_orig.log('Now we are ready to enumerate the subsets')
            legit_subs = (kenum(s.clone(node    = rc[sub_role],
                                        max_dep = s.max_dep-1,
                                        orig    = s.orig.sub()))
                          for sub_role in subs_role[:-1])
            for sub_suit in product(*legit_subs):
                sub_orig = uni_orig.branch()
                uni_orig.log('Chosen subsets (except for the last)')
                res = rc.clone()
                for i, v in enumerate(sub_suit):
                    res[subs_role[i]] &= v
                sub_orig.log('Attached those:'); sub_orig.log_m(res)
                subsets_so_far = (only(res[role]) for role in subs_path[:-1])  # type: list (frozen)set
                union_so_far = reduce(lambda x, y: x | y, subsets_so_far)  # type: (frozen)set
                leftover = only(uni_legit) - union_so_far  # type: (frozen)set
                val_for_last = Atom(content=(leftover | x for x in powerset(union_so_far)))
                res[subs_path[-1]] &= val_for_last
                sub_orig.log('Attached the superset:'); sub_orig.log_m(res)
                if not res.is_inconsistent():
                    sub_orig.log('Yielding')
                    yield res
                else:
                    sub_orig.log('Inconsistent')

    except KEnumError:
        s.orig.log('Well, that didn\'t work')
        s.orig.log('Then it must mean that the subsets are known')
        subs_legit = (kenum(s.clone(
                                    node    = s.node[r],
                                    max_dep = s.max_dep-1,
                                    orig    = s.orig.sub()))
                      for r in subs_role)
        for rs in product(*subs_legit):
            sub_orig = s.orig.branch()
            sub_orig.log(['Chosen subsets'])
            res = s.node.clone()
            for index, v in enumerate(rs):
                res[subs_role[index]] &= v
            sub_orig.log('Attached those subsets:'); sub_orig.log_m(res)
            subsets: Iterable[set] = (only(res[path]) for path in subs_path)
            superset: Set = reduce(lambda x, y: x | y, subsets)
            res[super_path] &= wr(superset)
            sub_orig.log('Attached the union:'); sub_orig.log_m(res)
            if not res.is_inconsistent():
                sub_orig.log('Yielding')
                yield res
            else:
                sub_orig.log('Inconsistent')

def fin_p(s: State):
    """Enumerate all children that haven't been enumerated"""
    s.orig.log('#'*30); s.orig.log('We are now in the Finishing Phase')
    form = cons_dic[only(s.node['_types'])][only(s.node['_cons'])].form
    needed_keys = list(form.keys())
    mc_e = [kenum(s.clone(node    = s.node[key],
                          max_dep = s.max_dep-1,
                          orig    = s.orig.sub()))
                  for key in needed_keys]
    mcs_s = product(*mc_e)
    for mcs in mcs_s:
        mcs_orig = s.orig.branch()
        mcs_orig.log('Chosen a new children suit')
        res = s.node.clone()
        for index, child in enumerate(mcs):
            res[needed_keys[index]] = child
        mcs_orig.log('Attached children suit:')
        mcs_orig.log_m(res)
        mcs_orig.log('Let\'s yield!')
        yield res
