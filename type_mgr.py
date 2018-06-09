from khoa_math import MathObj, MathType, Atom, Molecule
from kset import KSet, KConst

from typing import List, Union, NamedTuple


###Stuff to interface with the typing modules###
class AtomData(NamedTuple):
    path: str
    vals: KSet
    web: List = []


class MoleData(NamedTuple):
    path: str
    type_: MathType
    cons: KSet = KConst.STR.value




def math_obj_from_data(t: Union[AtomData, MoleData]) -> MathObj:
    """Construct math objects from dataclasses."""
    def get_role(path: str) -> str:
        """Extract the role from `path`."""
        return path.split('/')[-1]

    def get_parent(path: str) -> str:
        """Extract the path to the parent from `path`."""
        return '/'.join(path.split('/')[:-1])

    if type(t) == AtomData:
        return Atom(role=get_role(t.path), vals=t.vals, web=t.web)
    else:
        return Molecule(role=get_role(t.path), type_=t.type_, cons=t.cons)
