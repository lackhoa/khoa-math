from kset import *
from misc import *
from khoa_math import *
from type_mgr import *
from type_data import *
from wff import *

from anytree import PreOrderIter, RenderTree


def get_role(path: str) -> str:
    """Extract the role from `path`."""
    return path.split('/')[-1]


def get_parent(path: str) -> str:
    """Extract the path to the parent from `path`."""
    return '/'.join(path.split('/')[:-1])


def math_obj_from_data(t: Union[AtomData, MoleData]) -> MathObj:
    """Construct math objects from dataclasses."""
    if type(t) == AtomData:
        return Atom(role=get_role(t.path), values=t.values, web=t.web)
    elif type(t) == MoleData:
        return Molecule(role=get_role(t.path), type_=t.type_, cons=t.cons)


def list_cons(t: MathType) -> List:
    return set(cons_dic[t].keys())


def get_args(type_: MathType, cons: str) -> List[Union['AtomData', 'MoleData']]:
    """Return an argument list based on type `t` and constructor `c`"""
    return cons_dic[type_][cons]


def k_enumerate(root: MathObj, max_dep: int):
    if max_dep == 0: raise StopIteration
    if type(root) == Atom:
        if root.values.is_explicit():
            for x in root.values:
                yield Atom(role= root.role, values = KSet(x))
        else:
            print('Result cannot be enumerated!')
            raise StopIteration

    elif type(root) == Molecule:
        if not root.cons.is_explicit():
            # Providing constructors if not yet available:
            root.cons = root.cons & KSet(list_cons(root.type))
        # Try out all the constructors
        for cons_ in root.cons:
            res = Molecule(role=root.role, type_=root.type, cons=KSet({cons_}))
            # Attach arguments according to the constructor
            for arg in get_args(type_=res.type, cons=cons_):
                arg_node = math_obj_from_data(arg)
                for k in k_enumerate(arg_node, max_dep-1):
                    k.parent = res
                    yield res

wff_test_cons_dic = wff_cons_dic
wff_test_cons_dic['ATOM'] = [AtomData(path = 'text', values = KSet({'P'}))]
cons_dic['WFF_TEST'] = wff_test_cons_dic

start = Molecule(role='root', type_ = 'WFF_TEST')
cnt = 0
for t in k_enumerate(start, 2):
    print(RenderTree(t))
