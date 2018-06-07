from typing import Union, List, NamedTuple
from khoa_math import MathObj, MathType, Atom, Molecule
from kset import KSet, STR


class AtomData(NamedTuple):
    path: str
    value: KSet
    web: List = []


class MoleData(NamedTuple):
    path: str
    type_: MathType
    cons: KSet = STR


def get_role(path: str) -> str:
    """Extract the role from `path`."""
    return path.split('/')[-1]

def get_parent(path: str) -> str:
    """Extract the path to the parent from `path`."""
    return '/'.join(path.split('/')[:-1])

def math_obj_from_data(t: Union[AtomData, MoleData]) -> MathObj:
    """Construct math objects from dataclasses."""
    if type(t) == AtomData:
        return Atom(role=get_role(t.path), value=t.value, web=t.web)
    elif type(t) == MoleData:
        return Molecule(role=get_role(t.path), type_=t.type_, cons=t.cons)
