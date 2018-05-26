from khoa_math import *
from typing import Iterable

def kset(explicit: Iterable=None):
    """
    Sets represent knowledge, containing every possibility that could be. And it is how
    we represent data in this system.

    :param explicit: None means 'could be anything', not to be confused with
    the empty set, which is an impossibility.

    A set is "explicit" when it contains the single None (called the sentinel value).

    A kset NEVER contains other math objects, it only serves as a collection
    of literal values.

    Question: Why did I not just use regular set (I mean, ksets are just sets anyways)?
    Answer: Well, it is just a concept declaration. Also, the implicit set cannot be defined
    using python's vanilla sets
    """
    if explicit:
        return set(explicit)
    else: return {None}  # Note: it returns a set with a single None object, NOT None

# Helper functions defined on kset:
def is_explicit(kset_):
    if len(kset_) == 1 and kset_[0] is None: return False
    else: return True

def unify(s1, s2):
    """
    Binary operation unifying two sets of knowledge
    You can never learn less, you can only learn more
    """
    res = kset()
    if is_explicit(s1) and is_explicit(s2): res = kset( s1.union(s2) )
    elif is_explicit(s1): res = s1
    elif is_explicit(s2): res = s2

    return res
