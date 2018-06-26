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
class UnknownAtomError(KEnumError):
    def __init__(self, atom: KSet):
        self.message = 'Cannot enumerate this atom: {}'.format(atom)
        self.atom = atom
class RelationError(KEnumError):
    def __init__(self, rels):
        self.message = 'Cannot checked these relations'
        self.rels = rels
class OutOfTimeError(KEnumError):
    def __init__(self, mole):
        self.message = 'Out of time while enumerating this molecule'.format(mole.root)
        self.root = mole.root

def kenum(node    : Union[Mole, KSet],
          max_dep : int,
          orig    : LogNode,
          deadline: Optional[float] = None,  # It is a time like the ones given by time.time()
          ):
    def form_p(node, orig):
        """Assure that the node is well-formed"""
        orig.log('#'*30); orig.log('Welcome to Formation Phase')
        assert(node['_types'].is_singleton()), 'How come the type is unknown?'
        node_type = only(node['_types'])
        cons = node['_cons'] & KSet(cons_dic[only(node['_types'])].keys())
        orig.log('Current constructor is: {}'.format(node['_cons']))
        orig.log('Possible constructors after unified are: {}'.format(cons))
        orig.log('Exploring all constructors')
        for con in cons:
            con_orig = orig.branch(); con_orig.log('Chosen constructor {}'.format(con))
            form, rels = cons_dic[only(node['_types'])][con]

            if max_dep == 1 and any(map(lambda x: type(x) is Mole, form.values())):
                con_orig.log('Out of depth, try another constructor')
                continue
            else:
                con_orig.log('Depth remaining: {}'.format(max_dep))

            res = node.clone()
            res['_cons'] = wr(con)
            res &= form
            con_orig.log('Attached all components')
            con_orig.log_m(res)
            if not res.is_inconsistent():
                con_orig.log('Consistent, yielding from formation phase')
                yield res
            else: con_orig.log('Inconsistent')

    def rel_p(node, rel, orig):
        """Apply relation `rel` to aid in enumeration"""
        orig.log('#'*30); orig.log('Welcome to Relation Phase')

        orig.log('Working with relation \"{}\"'.format(rel))
        if rel.type == 'FUN':
            orig.log('It\'s a functional relation')
            for res in fun_rel(node, rel, orig):
                yield res
        elif rel.type == 'UNION':
            orig.log('It\'s a union relation')
            for res in uni_rel(node, rel, orig):
                yield res

    def cycle_rel_p(node, rels, orig):
        for new_node, unchecked_rels in repeat_rel_p(
                node, iter(rels), orig):
            new_orig = orig.branch()
            new_orig.log('Chosen from `repeat_rel_p`:'); new_orig.log_m(new_node)
            if new_node == node:
                new_orig.log('`repeat_rel_p` didn\'t do anything')
                if unchecked_rels:
                    new_orig.log('There are unchecked relations, which is bad')
                    raise RelationError(unchecked_rels)
                else:
                    new_orig.log('All relations checked! Yielding this:'); new_orig.log_m(node)
                    yield node
            else:
                new_orig.log('Got some new information')
                if unchecked_rels:
                    new_orig.log('Still got some relations, going to the next cycle')
                    for res in cycle_rel_p(new_node, unchecked_rels, new_orig):
                        yield res
                else:
                    new_orig.log('No more relations left, yielding this:'); new_orig.log_m(new_node)
                    yield new_node

    def repeat_rel_p(node, rel_iter, orig):
        try:
            this_rel = next(rel_iter)
        except StopIteration:
            orig.log('No more relations left, yielding')
            yield (node, ())
            return
        try:
            for new_node in rel_p(node, this_rel, orig):
                choice_orig = orig.branch()
                choice_orig.log('Chosen '); choice_orig.log_m(new_node)
                choice_orig.log('Moving on to the next relation')
                rel_iter, new_rel_iter = tee(rel_iter)  # New path, new iterator
                for res, unchecked_rels in repeat_rel_p(
                    new_node, new_rel_iter, choice_orig):
                    yield (res, unchecked_rels)
        except KEnumError as e:
            if type(e) is UnknownAtomError:
                orig.log('Cannot apply this relation (right now)')
            elif type(e) is OutOfTimeError:
                orig.log('We ran out of time for this relation')
            orig.log('Moving on to the next relation anyways')
            for res, unchecked_rels in repeat_rel_p(node, rel_iter, orig):
                yield (res, (this_rel,)+unchecked_rels)

    def fun_rel(node, rel, orig):
        in_paths, out_path = rel['inp'], rel['out']
        in_roles = [car(path) for path in in_paths]
        orig.log('The inputs\' nodes are:')
        for role in in_roles:
            orig.log_m(node[role])

        legit_ins = [kenum(node[role], max_dep-1, orig.sub(), deadline)
                     for role in in_roles]
        for legit_in in product(*legit_ins):
            in_orig = orig.branch()
            in_orig.log('Chosen a new input suit')
            res = node.clone()
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

    def uni_rel(node, rel, orig):
        orig.log('Try enumerating the superset part')
        super_path, subs_path = rel['sup'], rel['subs']
        super_role, subs_role = car(super_path), [car(path) for path in subs_path]
        try:
            for uni_legit in kenum(node[super_role], max_dep-1, orig.sub(), deadline):
                rc = node.clone()
                rc[super_role] &= uni_legit
                uni_orig = orig.branch()
                uni_orig.log('Chosen the superset part:'); uni_orig.log_m(rc)
                for sub_path in subs_path[:-1]:
                    rc[sub_path] &= KSet(content=powerset(only(uni_legit)))
                uni_orig.log('Updated the subsets')
                uni_orig.log('Result is'); uni_orig.log_m(rc)

                uni_orig.log('Now we are ready to enumerate the subsets')
                legit_subs = (kenum(rc[sub_role], max_dep-1, orig.sub(), deadline)\
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
                    val_for_last = KSet(content=(leftover | x for x in powerset(union_so_far)))
                    res[subs_path[-1]] &= val_for_last
                    sub_orig.log('Attached the superset:'); sub_orig.log_m(res)
                    if not res.is_inconsistent():
                        sub_orig.log('Yielding')
                        yield res
                    else:
                        sub_orig.log('Inconsistent')

        except KEnumError:
            orig.log('Well, that didn\'t work')
            orig.log('Then it must mean that the subsets are known')
            sub_nodes_legit = (kenum(node[r], max_dep-1, orig.sub(), deadline)
                               for r in subs_role)
            for rs in product(*sub_nodes_legit):
                sub_orig = orig.branch()
                sub_orig.log(['Chosen subsets'])
                res = node.clone()
                for index, v in enumerate(rs):
                    res[subs_role[index]] &= v
                sub_orig.log('Attached those subsets:'); sub_orig.log_m(res)
                subsets = (only(res[path]) for path in subs_path)  # type: list of (frozen)set
                superset = reduce(lambda x, y: x | y, subsets)  # type: (frozen)set
                res[super_path] &= wr(superset)
                sub_orig.log('Attached the union:'); sub_orig.log_m(res)
                if not res.is_inconsistent():
                    sub_orig.log('Yielding')
                    yield res
                else:
                    sub_orig.log('Inconsistent')

    def fin_p(node, orig):
        """Enumerate all children that haven't been enumerated"""
        orig.log('#'*30); orig.log('We are now in the Finishing Phase')
        form = cons_dic[only(node['_types'])][only(node['_cons'])].form
        needed_keys = list(form.keys())
        m_children_enum = [kenum(node[key], max_dep-1, orig.sub(), deadline)
                           for key in needed_keys]
        m_children_suits = product(*m_children_enum)
        for m_children_suit in m_children_suits:
            m_children_suit_orig = orig.branch()
            m_children_suit_orig.log('Chosen a new children suit')
            res = node.clone()
            for index, child in enumerate(m_children_suit):
                res[needed_keys[index]] = child
            m_children_suit_orig.log('Attached children suit:')
            m_children_suit_orig.log_m(res)
            m_children_suit_orig.log('Let\'s yield!')
            yield res

    orig.log(30*'#'); orig.log('Welcome to kenum!')
    if deadline is not None and time.time() > deadline:
        orig.log('We\'ve ran out of time')
        raise OutOfTimeError
    else: orig.log('We still have time left')

    orig.log('The node is:'); orig.log_m(node)

    if type(node) == KSet:
        orig.log('It\'s an atom')
        if node.is_explicit():
            for val in node:
                orig.log('Yielding this value: {}'.format(wr(val)))
                yield wr(val)
        else:
            orig.log('Can\'t get any value for it')
            raise UnknownAtomError(node)

    elif type(node) == Mole:
        orig.log('It\'s a molecule')

        if node in glob.legits:
            orig.log('Molecule already legit, yielding!')
            yield node
            return

        orig.log('Let\'s go to Formation Phase')
        for well_formed in form_p(node, orig.sub()):
            this_wf_orig = orig.branch()
            this_wf_orig.log('Chosen this from Formation phase')
            this_wf_orig.log_m(well_formed)
            this_wf_orig.log('Let\'s go to Relation Phase')

            rels = cons_dic[only(well_formed['_types'])][only(well_formed['_cons'])].rels
            for relationed in cycle_rel_p(well_formed, rels, this_wf_orig.sub()):
                this_rel_orig = this_wf_orig.branch()
                this_rel_orig.log('Chosen this from Relation Phase:')
                this_rel_orig.log_m(relationed)
                this_rel_orig.log('Let\'s go to Finishing Phase')

                for finished in fin_p(relationed, this_rel_orig.sub()):
                    this_fin_orig = this_rel_orig.branch()
                    this_fin_orig.log('Chosen this from Finishing Phase:')
                    this_fin_orig.log_m(finished)
                    glob.legits.add(finished)
                    this_fin_orig.log('All phases are complete, yielding from kenum')
                    yield finished
