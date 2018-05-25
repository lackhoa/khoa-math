from khoa_math import *
from typing import Iterable

def kset(explicit: Iterable=None):
    '''
    Sets represent knowledge, containing every possibility that could be.

    :param explicit: None means 'could be anything'. And the empty explicit set
    is an impossibility.

    A set is "explicit" when its explicit attribute is present.

    As of now, a kset NEVER contains other math objects, it only serves as a collection
    of possible literal values.
    '''
    res = MathObject(MathType.KSET)

    return res

# Helper functions defined on kset:
def unify(s1, s2):
    '''
    Binary operation unifying two sets of knowledge
    You can never learn less, you can only learn more
    '''
    assert(s1.type == s2.type == MathType.KSET)
    
    res = None

    if s1.explicit and s2.explicit:
        res = kset( s1.explicit.unify(s2.explicit) )
    elif s1.explicit: res = s1
    elif s2.explicit: res = s2
    else: res = kset()

    return res