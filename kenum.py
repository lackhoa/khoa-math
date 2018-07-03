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
class InfinityToken(KEnumError):
    def __init__(self, node):
        self.message = 'Cannot enumerate this node: {}'.format(node)
        self.node = node
class TimeoutToken(KEnumError):
    def __init__(self, node):
        self.message = 'Out of time while enumerating node:'.format(node)


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
                if type(intermediate) is TimeoutToken:
                    # Timeout tokens are propagated
                    new_deadline = (yield TimeoutToken)
                    # Resume point
                    assert(new_deadline > time.time())
                    s.deadline = new_deadline
                elif type(intermediate) is InfinityToken:
                    # Infinity tokens are propagated and unrecoverable
                    yield intermediate; return
                else:
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


def check_consistency(orig_fun):
    def new_fun(*args, **kwargs):
        for res in orig_fun(*args, **kwargs):
            if not res.node.is_inconsistent():
                res.log('Consistent, yielding!')
                yield res
            else:
                res.log('Inconsistent')
    return new_fun


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
            yield InfinityToken()

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
            yield InfinityToken()
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
        states_procs = [well_formed, pipe(cycle_rel_p, fin_p)(well_formed)
                        for well_formed in form_p(s)]
        while states_procs:
            next_deadline = time.time() + (s.deadline-time.time())/8 if 'deadline' in s
                            else time.time() + 0.1
            for state, proc in states_procs:
                state.deadline = next_deadline  # Insert more coins
                for res in proc:
                    if type(res) is State:
                        if res.node not in memo:
                            memo.add(res.node)
                            yield res
                        else: s.log('Duplication detected')
                    elif type(res) is TimeoutToken:
                        break  # Go to next constructor
                    elif type(res) is InfinityToken:
                        yield res; return
                # Process is done, remove it
                procs.remove(proc)

                if 'deadline' in s and time.time() > s.deadline:
                    s.log('Late by: {} s'.format(time.time()-s.deadline))
                    new_deadline = (yield TimeoutToken)
                    assert(new_deadline > time.time())
                    s.deadline = new_deadline

        s.log('Enumeration done, updating the cache')
        glob.cache[s.node] = memo


@check_consistency
def form_p(s: State):
    """Assure node returned is well-formed"""
    s.log(30*'#' + 'Welcome to Formation Phase')
    assert(s.node['_types'].is_singleton()), 'How is the type unknown?'
    s.node_type = only(s.node['_types'])
    cons = s.node['_cons'] & Atom(cons_dic[only(s.node['_types'])].keys())
    s.log('Current constructor is: {}'.format(s.node['_cons']))
    s.log('Possible constructors after unified are: {}'.format(cons))
    for con in cons:
        sb = s.branch(node = s.node.clone())
        sb.log('Chosen constructor {}'.format(con))
        form, rels = cons_dic[only(s.node['_types'])][con]

        if s.max_dep == 1 and any(map(lambda x: type(x) is Mole, form.values())):
            sb.log('Out of depth, try another constructor')
            continue
        else:
            sb.log('Depth remaining: {}'.format(s.max_dep))

        sb['_cons'] = wr(con)
        new_node &= form
        sb.log('Attached all components:'); con_orig.log_m(res)
        yield sb


class Edge():
    def __init__(self, head: Iterable, tail: Iterable):
        self.head = set(head)
        self.tail = set(tail)

class Graph():
    def __init__(self, vertices = set(), edges = set())
        self.vertices = set(vertices)
        self.edges    = set(edges)

def rels_to_graph(rels):
    graph = Graph()
    for rel in rels:
        if rel.type == 'FUN':
            graph.vertices |= set(rel['inp']) | set(rel['out'])
            graph.edges.append(Edge(tail=rel['inp'], head=rel['out']))
        elif rel.type = 'UNI':
            graph.vertices |= set(rel['subs']) | set(rel['sup'])
            graph.edges.extend([Edge(tail=rel['subs'], head=rel['sup']),
                                Edge(tail=rel['sup'], head=rel['subs'])])
        elif rel.type = 'ISO':
            graph.vertices |= set(rel['left']) | set(rel['right'])
            graph.edges.extend([Edge(tail=rel['left'], head=rel['right']),
                                Edge(tail=rel['right'], head=rel['left'])])
    return graph

def min_start(graph: Graph):
    def span(subv, graph):
        res = subv
        changed = True
        while changed:
            for edge in graph.edges:
                if edge.tail.issubset(res):
                    old_res = res
                    res |= edge.head
                    changed = (res != old_res)
        return res

    res = set()
    for subv in powerset(graph.vertices):
        if filter(lambda v: v.issubset(subv), res):
            continue
        elif span(subv, graph) == graph.vertices:
            res.add(subv)
    return res


def cycle_rel_p(s: State, rels = None, time_lim = None):
    MS = 0.001  # One millisecond
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
                    raise InfinityToken(s.node)
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
        if type(e) is TimeoutToken:
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
    in_paths, out_paths = rel['inp'], rel['out']
    arguments = [res[path] for path in in_paths]
    outputs = rel['fun'](*arguments)
    for out_path, output in zip(out_paths, outputs):
        res.node[out_path] = output
    in_orig.log('Attached output:')
    in_orig.log_m(res)
    if not res.is_inconsistent():
        in_orig.log('Yielding!')
        yield res
    else:
        in_orig.log('Inconsistent')


@check_consistency
def _uni_rel(s: State, rel):
    sub_path, super_path = rel['subs'], rel['sup']
    subs, super_ = [s.node[p] for p in sub_paths], s.node[super_path]
    if not super_.is_singleton():
        s.node[super_path] = reduce(lambda x, y: only(x)|only(y), subs)
        yield s
    else:
        for subsets in product(powerset(only(super_)),
                               repeat=len(subs_path)-1):
            sb = s.branch(node = s.node.clone())
            for sub_path, subset in zip(subs, subsets):
                sb.node[sub_path] &= wr(subset)
            if sb.nodesub_path.is_inconsistent():
                sb.log('Inconsistent, moving on to other subsets')
                continue
            sb.log('Attached subsets except for the last:'); sb.log_m(res)
            subsets_so_far: List[Set] = [only(sb.node[role]) for role in subs_path[:-1]]
            union_so_far  : Set       = reduce(lambda x, y: x | y, subsets_so_far)
            leftover      : Set       = only(super_) - union_so_far
            val_for_last = Atom(content=(leftover | x for x in powerset(union_so_far)))
            sb.node[subs_path[-1]] &= val_for_last
            sub_orig.log('Attached the superset:'); sub_orig.log_m(res)
            yield res


@check_consistency
def fin_p(s: State):
    """Enumerate all children that haven't been enumerated"""
    s.log(30*'#' + 'We are now in the Finishing Phase')
    form = cons_dic[only(s.node['_types'])][only(s.node['_cons'])].form
    needed_keys = list(form.keys())
    subs = [s.sub(node=s.node[key], max_dep=s.max_dep-1) for key in needed_keys]
    mc_gens = [kenum(sub) for sub in subs]
    results = [[] for _ in range(len(needed_keys))]
    for index, mc_gen in enumerate(mc_gens):
        for res in mc_gen():
            if type(res) is TimeoutToken:
                yield res
                # Resume
                assert(s.deadline > time.time())
                for sub in subs: sub.deadline = s.deadline  # Sync up the deadline

            elif type(res) is InfinityToken:
                yield res; return

            else:
                results[index].append(state.node)

    for suit in product(results):
        sb = s.branch(node = s.node.clone())
        for index, child in enumerate(suit):
            sb.node[needed_keys[index]] = child
            sb.log('Attached children suit:'); sb.log_m(sb.node)
            sb.log('Yielding!')
            yield sb


if __name__ == '__main__':
    print('Testing the logging')
    s = State(logger = logging.getLogger()); s.log('This is from s')
    s_sub = s.sub(); s_sub.log('This is from s_sub')
    s_branch = s_sub.branch(); s_branch.log('This is from s_branch')
    sbb = s_branch.branch(); sbb.log('This is a branch of s_branch')
