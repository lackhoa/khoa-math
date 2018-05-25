from khoa_math import *
from typing import Iterable

def kset(explicit: Iterable=None):
    '''
    Sets represent knowledge, containing every possibility that could be. And it is how
    we represent data in this system.

    :param explicit: None means 'could be anything', not to be confused with
    the empty set, which is an impossibility.

    A set is "explicit" when it does not contain the single None value.

    As of now, a kset NEVER contains other math objects, it only serves as a collection
    of possible literal values.

    Question: Why did I not just use regular set (I mean, ksets are literally sets)?
    Answer: Well, the way I treat it is different, and worthy of a concept declaration.
    '''
    if explicit:
        return set(explicit)
    else: return {None}  # Note: it returns a single None object

# Helper functions defined on kset:
def unify(s1, s2):
    '''
    Binary operation unifying two sets of knowledge
    You can never learn less, you can only learn more
    '''
    res = None

    if s1 and s2:
        res = kset( s1.union(s2) )
    elif s1: res = s1
    elif s2: res = s2
    else: res = kset()

    return res