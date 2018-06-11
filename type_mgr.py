from typing import Union, NamedTuple, Iterable


###Stuff to interface with the typing modules###
class CI(NamedTuple):
    args: Iterable[Union['Atom', 'Molecule']]
    rels: Iterable['Rel'] = []
