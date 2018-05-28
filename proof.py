from prep import *
from typing import List, Tuple, Set, FrozenSet

# This file contains fundamental constructs concerning proofs.
# However, it does not provide a mechanism to prove.

def conn(form, dep: FrozenSet):
    '''
    Connection: a formula plus a set of dependency
    '''
    res = MathObject(MathType.PL_CONNECTION)
    res.form = form
    res.dep = dep
    res.text = 'connection({}, {})'.format(form.text, str(dep))
    
    # Self test mechanism
    res.self_test = lambda: form.type == MathType.PL_FORMULA
    return res