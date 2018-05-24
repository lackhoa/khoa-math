from khoa_math import *
from typing import Iterable

def kset(explicit: Iterable=None):
    '''
    Sets represent knowledge, you always assume everything that could be
    :param explicit: None is unknown (could be anything). And the empty set
    is an impossibility
    '''
    res = MathObject(MathType.KSET)
    self.explicit = Set(explicit)

    return res

# Helper functions defined on kset:
is_unknown = lambda kset_: kset_.qualifier == kset_.explicit == None

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

# Unknown:
def unknown():
    '''
    Kind of like a throaway structure, but it's important nonetheless
    Every attribute of an unknown is a set
    '''
    u = MathObject(MathType.UNKNOWN)
    return u

# Functions defined on Unknowns:
def lookup(u, attr: str):
    '''
    Return an attribute of an Unknown object whenever possible
    If attribute does not exist, return the unknown set
    Use the 'dot' chain to look deeper into the components of the unknown
    '''
    if hasattr(u, attr): return getattr(u, attr)
    else: return kset()

def add_knowledge(u, attr: str, ks):
    '''
    Add knowledge 'ks' to an attribute 'attr' of the unknown 'u'
    This function is always "safe", which means you never lose knowledge
    '''
    assert(ks.type == MathType.KSET)
    setattr(u, attr, unify( lookup(u, attr), ks ))
    
def reduce(u):
    '''
    Narrow down an unknown object based on its determined attributes
    This is basically what the UNKNOWN type is for
    '''
    if u.type == MathType.PL_FORMULA:
        add_knowledge( u, 'cons', kset(list(MathType)) )

        elif u.cons == PlCons.ATOM:
            pass
        elif u.cons == PlCons.NEGATION:
            add_knowledge( u, 'body', kset({}) )
