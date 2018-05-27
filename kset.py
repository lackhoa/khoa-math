from khoa_math import *
from typing import Iterable


# Sets represent knowledge, containing every possibility that could be. And it is how
# we represent data in this system.

# A kset NEVER contains other math objects, it only serves as a collection
# of literal values.

# There are two types of sets: exclusive and inclusive. Exclusive sets CONTAINS all the possibilities, while inclusive sets EXPAND the possibilities. To denote inclusive sets, we add the element None.

# Helper functions defined on kset:
def is_exclusive(kset_):
    if None in kset_: return False
    else: return True

def unify(s1, s2):
    """
    Binary operation unifying two sets of knowledge
    You can never learn less, you can only learn more
    """
    if is_exclusive(s1) and is_exclusive(s2): res = s1 & s2  # Both exclusive
    elif is_exclusive(s1): res = s1
    elif is_exclusive(s2): res = s2
    else res = s1 | s2  # Both inclusive, note that res is also inclusive (it contains 'None')

    return res
