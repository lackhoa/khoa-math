from misc import *
from khoa_math import *
from type_data import *
from rel import *
import glob

from typing import *
from itertools import product, starmap, repeat

from functools import partial, reduce
import time


class KEnumError:
    pass
class InfinityError(KEnumError):
    def __init__(self, node):
        self.message = 'Cannot enumerate this node: {}'.format(node)
        self.node = node
class OutOfTimeError(KEnumError):
    def __init__(self, node):
        self.message = 'Out of time while enumerating this node'.format(node)
        self.node = node


class State(dict):
    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.prefix = '' if 'prefix' not in self else self.prefix
        self.on = True if 'on' not in self else self.on
        self.choice, self.phase = 0, 0

    def __getattr__(self, attr):
        if attr == 'fork':
            return self.fork
        else:
            return self[attr]

    def __setattr__(self, attr, value):
        self[attr] = value

    def fork(self, **kwargs):
        """Offer a shallow copy with optional modification"""
        res = State()
        for k in self:
            res[k] = self[k]
        for k in kwargs:
            res[k] = kwargs[k]
        return res

    def branch(self):
        new_prefix = self.prefix + chr(97+self.choice)
        res = self.fork(prefix=new_prefix)
        self.choice += 1
        return res

    def sub(self):
        new_prefix = self.prefix + str(self.phase)
        res = self.fork(prefix=new_prefix)
        self.phase += 1
        return res

    def log(self, msg, level=50):
        if self.on:
            msg = '[{}]: {}'.format(self.prefix, msg)
            self.logger.log(msg=msg, level=level)

    def log_m(self, mole, level=50):
        """ Log a molecule only if it\'s on"""
        if self.on:
            msg = '{}\n'.format(str(mole))
            self.logger.log(msg=msg, level=level)








def pipe(*procs):
    def glue(proc1, proc2):
        def func(s):
            for intermediate in proc1(s):
                for res in proc2(intermediate):
                    yield res
        return func
    return procs[0] if len(procs)==1 else glue(procs[0], pipe(procs[1:]))


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


def kenum(s: State):
    s.log(30*'#' + 'Welcome to kenum!')
    s.log('The node is:'); s.log_m(s.node)
    if type(s.node) == Atom:
        s.log('It\'s an atom')
        if s.node.is_explicit():
            for val in s.node:
                sb = s.branch(s.node = Atom(wr(val)))
                s.log('Yielding this value: {}'.format(wr(val)))
                yield sb
        else:
            s.log('Can\'t get any value for it')
            yield InfinityError()

    elif type(s.node) == Mole:
        s.log('It\'s a molecule')
        if 'deadline' in s and time.time() > s.deadline:
            s.log('We\'re late by: {} s'.format(time.time()-s.deadline))

        if s.node in glob.legits:
            s.log('Molecule already legit, yielding!')
            yield s
            return

        if not is_enumerable(s.node):
            s.log('This molecule is obviously unenumerable')
            yield InfinityError()
            return
        else:
            s.log('There is a hope for enumeration, so let\'s begin!')

        if s.node in glob.cache:
            s.log('The molecule is already in cache')
            for cached_node in glob.cache[s.node]:
                sb = s.branch(node = cached_node)
                yield sb
            return

        memo = set()  # To build the cache
        well_formed = form_p(s)
        while well_formed:
            # HERE!
            sb = s.branch(node = well_formed[0])
            new_deadline = time.time() + 0.1
            while True:
                for res in pipe(cycle_rel_p, fin_p)(s):
                    if type(res) is State:
                        if res.node not in memo:
                            memo.add(res.node)
                            yield res
                        else: s.log('Duplication detected')
                    elif type(res) is OutOfTimeError:
                        break

                    if 'deadline' in s and time.time() > s.deadline:
                        s.log('We\'re late by: {} s'.format(time.time()-s.deadline))
                        yield OutOfTimeError()
                break
            well_formed = well_formed[1:]

        s.log('Updating the cache')
        glob.cache[s.node] = memo


def form_p(s: State):
    """Assure that the s.node is well-formed"""
    s.log('#'*30); s.log('Welcome to Formation Phase')
    assert(s.node['_types'].is_singleton()), 'How come the type is unknown?'
    s.node_type = only(s.node['_types'])
    cons = s.node['_cons'] & Atom(cons_dic[only(s.node['_types'])].keys())
    s.log('Current constructor is: {}'.format(s.node['_cons']))
    s.log('Possible constructors after unified are: {}'.format(cons))
    s.log('Exploring all constructors')
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


# @check_time
def cycle_rel_p(s: State, rels = None, time_lim = None):
    MS = 0.001  # One millisecond
    INIT_TIME_LIM = 10*MS
    COEF = 10  # The amount to multiply the previous time limit
    # Initialization code for first time
    if time_lim is None:
        time_lim = INIT_TIME_LIM
    if rels is None:
        rels = cons_dic[only(s.node['_types'])][only(s.node['_cons'])].rels

    for new_node, unchecked_rels, timeout in repeat_rel_p(
            s, iter(rels), time_lim):
        new_orig = s.orig.branch()
        new_orig.log('Chosen from `repeat_rel_p`:'); new_orig.log_m(new_node)
        if new_node == s.node:
            new_orig.log('`repeat_rel_p` didn\'t do anything')
            if unchecked_rels:
                new_orig.log('There are unchecked relations, which is bad')
                if timeout:
                    time_lim = COEF*time_lim
                    new_orig.log('Got a timeout, next time limit is: {}'.format(time_lim))
                    for res in cycle_rel_p(s.clone(node=new_node, orig=new_orig), unchecked_rels, time_lim):
                        yield res
                else:
                    new_orig.log('But that wasn\'t due to a timeout')
                    raise InfinityError(s.node)
            else:
                new_orig.log('All relations checked! Yielding this:'); new_orig.log_m(s.node)
                yield s.node
        else:
            new_orig.log('Got new information!')
            if unchecked_rels:
                new_orig.log('Still got some relations, going to the next cycle')
                for res in cycle_rel_p(s.clone(node=new_node, orig=new_orig), unchecked_rels, time_lim):
                    yield res
            else:
                new_orig.log('No more relations left, yielding this:'); new_orig.log_m(new_node)
                yield new_node


# @check_time
def repeat_rel_p(s: State, rel_iter, time_lim):
    try:
        this_rel = next(rel_iter)
    except StopIteration:
        s.log('No more relations left, yielding')
        yield (s.node, (), False)
        return
    try:
        new_deadline = time.time() + time_lim
        for new_node in rel_p(s.clone(deadline=new_deadline), this_rel):
            choice_orig = s.orig.branch()
            choice_orig.log('Chosen '); choice_orig.log_m(new_node)
            choice_orig.log('Moving on to the next relation')
            rel_iter, new_rel_iter = tee(rel_iter)  # New path, new iterator
            for res, unchecked_rels, timeout in repeat_rel_p(
                    s.clone(node=new_node, orig=choice_orig), new_rel_iter, time_lim):
                yield (res, unchecked_rels, timeout)
    except KEnumError as e:
        if type(e) is OutOfTimeError:
            got_timeout = True
            s.log('We ran out of time for this relation')
        else:
            got_timeout = False
            s.log('Cannot apply this relation (right now)')
        s.log('Moving on to the next relation anyways')
        for res, unchecked_rels, will_timeout in repeat_rel_p(s, rel_iter, time_lim):
            yield (res, (this_rel,)+unchecked_rels, got_timeout or will_timeout)


def rel_p(s: State, rel: Rel):
    """Apply relation `rel` to aid in enumeration"""
    s.log('#'*30); s.log('Welcome to Relation Phase')

    s.log('Working with relation \"{}\"'.format(rel))
    if rel.type == 'FUN':
        s.log('It\'s a functional relation')
        for res in _fun_rel(s, rel):
            yield res
    elif rel.type == 'UNION':
        s.log('It\'s a union relation')
        for res in _uni_rel(s, rel):
            yield res


def _fun_rel(s: State, rel):
    in_paths, out_path = rel['inp'], rel['out']
    in_roles = [car(path) for path in in_paths]
    s.log('The inputs\' nodes are:')
    for role in in_roles:
        s.log_m(s.node[role])

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
    s.log('Try enumerating the superset part')
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
        s.log('Well, that didn\'t work')
        s.log('Then it must mean that the subsets are known')
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
    s.log('#'*30); s.log('We are now in the Finishing Phase')
    form = cons_dic[only(s.node['_types'])][only(s.node['_cons'])].form
    needed_keys = list(form.keys())
    mc_e = [kenum(s.clone(node    = s.node[key],
                          max_dep = s.max_dep-1,
                          orig    = s.orig.sub()))
                  for key in needed_keys]
    mcs_s = product(*mc_e)
    for mcs in mcs_s:
        mcs_orig = s.orig.branch()
        mcs.log('Chosen a new children suit')
        res = s.node.clone()
        for index, child in enumerate(mcs):
            res[needed_keys[index]] = child
        mcs.log('Attached children suit:')
        mcs.log_m(res)
        mcs.log('Let\'s yield!')
        yield res


if __name__ == '__main__':
    print('Testing the logging')
    s = State(logger = logging.getLogger()); s.log('This is from s')
    s_sub = s.sub(); s_sub.log('This is from s_sub')
    s_branch = s_sub.branch(); s_branch.log('This is from s_branch')
    sbb = s_branch.branch(); sbb.log('This is a branch of s_branch')
