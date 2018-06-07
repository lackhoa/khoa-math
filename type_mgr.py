from khoa_math import MathObj, MathType, Atom, Molecule
from kset import KSet, STR

from typing import List, Union, NamedTuple


###Stuff to interface with the typing modules###
class AtomData(NamedTuple):
    path: str
    values: KSet
    web: List = []


class MoleData(NamedTuple):
    path: str
    type_: MathType
    cons: KSet = STR
