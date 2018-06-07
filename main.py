from kset import *
from misc import *
from khoa_math import *
from type_mgr import *
from type_data import *

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
    return cons_dic[t].keys()


def get_args(type_: MathType, cons: str) -> List[Union['AtomData', 'MoleData']]:
    """Return an argument list based on type `t` and constructor `c`"""
    return cons_dic[type_][cons]


def k_enumerate(root: MathObj):
    if type(root) == Atom:
        if root.values.is_explicit():
            for x in root.values:
                yield Atom(role= root.role, values = KSet(x))
        else:
            print('Result cannot be enumerated!')
    elif type(root) == Molecule:
        for i, x in enumerate(list_cons(root.type)):
            res = Molecule(role='root', type_=root.type, cons=KSet([x]))
            res.name = str(i)
            # Add its arguments since we now know the constructor
            for arg in get_args(type_=res.type, cons=res.cons[0]):
                math_obj_from_data(arg).parent = res
            yield res


root = Molecule(role = 'root', type_ = MathType.WFF)
res = k_enumerate(root)
for t in res:
    print(RenderTree(t))
