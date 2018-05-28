from prep import *
from typing import Tuple

# This file contains the semantic interpretation of PL:

# These two constructors represent the principle of bivalence
def true_():
    return MathObject(MathType.TRUTH, 'true')
def false_():
    return MathObject(MathType.TRUTH, 'false')

def interpretation(assign: List[Tuple[MathObject, MathObject]]):
    '''
    An interpretation assigns truth values to atomic formulas
    '''
    for k, v in assign:
        assert(k.type == MathType.FORMULA)
        assert(v.type == MathType.TRUTH)

    

