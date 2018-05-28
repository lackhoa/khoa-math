from proof import *
from typing import Callable

# This file contains theorems, which are logical proofs derivable from PL
# Object construct
def theorem(name, func: Callable):
    '''
    :param func: the functionality of the theorem
    '''
    thm = MathObject(MathType.PL_THEOREM)
    thm.func = func
    thm.text = name

    return thm

excluded_middle = theorem('Law of Excluded Middle', lambda A: disj(A, neg(A)) )

