from khoa_math import *
from typing import Iterable

def always():
    return True

def never():
    return False

def k_set(explicit: Set=None, qualifier: Callable[..., bool]=None):
    '''
    Sets represent knowledge, you always assume everything that could be
    :param qualifier: always() for the universal set and never() for the empty set
    :param explicit: Provide the explicit set whenever possibe!
    When both are None, this set is unknown. The __bool__ function will return False
    You cannot provide explicit and qualifier!
    '''
    res = MathObject(MathType.SET)

    assert( bool(explicit) == bool(qualifier) == True ), 'You cannot supply both!'

    if explicit:
        # You can always derive the qualifier from the explicit
        self.qualifier = lambda j: j in explicit

    # You can also derive the explicit if the qualifier is special:
    if qualifier == never:
        self.explicit = set()

    self.explicit = explicit
    self.qualifier = qualifier

    return res

# Helper functions defined on k_set:
is_empty = lambda k_set_: k_set_.qualifier == never
is_universal = lambda k_set_: k_set_.qualifier == always
is_unknown = lambda k_set_: k_set_.qualifier == k_set_.explicit == None

def union(s1, s2):
    res = None

    if s1.explicit and s2.explicit:
        res = s1.explicit.union(s2.explicit)
    elif s1.explicit:
        if is_empty(s2): res = k_set(explicit = set())
        else: res = s1
    elif s2.explicit:
        if is_empty(s1): res = k_set(explicit = set())
        else: res = s2
    else: res = k_set(qualifier = lambda x: s1.qualifier(x) and s2.qualifier(x))

    return res


# Unknown:
def unknown():
    '''
    Kind of like a throaway structure, but it's important nonetheless
    '''
    u = MathObject(MathType.UNKNOWN)
    return u


def lookup(u, attr: str):
    '''
    Return an attribute of an Unknown object whenever possible
    If attribute does not exist, return the unknown set
    '''
    if hasattr(u, attr): return getattr(u, attr)
    else: return k_set()

def reduce(u):
    '''
    Narrow down an unknown object based on its determined attributes
    This is basically what the UNKNOWN type is for
    '''
    if u.type == MathType.PL_FORMULA:
        setattr(u, 'cons', union( lookup(u, 'cons'), k_set(explicit=set(list(MathType))) ))

        elif u.cons == PlCons.ATOM:
            pass
        elif u.cons == PlCons.NEGATION:
            setattr(u, 'body', union( lookup(u, 'body'), k_set(explicit=set(list(MathType))) ))
