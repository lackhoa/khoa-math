import logging, inspect
from enum import Enum, auto
from typing import Iterable


# Awesome class to name Enums
class MyEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        """Return a more subtle representation"""
        return self.value


def take(n, iterable):
    "Return first n items of the iterable as a list"
    return list(islice(iterable, n))


def nth(iterable, n, default=None):
    "Returns the nth item or a default value"
    return next(islice(iterable, n, None), default)


def powerset(iterable):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s)+1))





def car(path: str): return path.split('/')[0]

def cdr(path: str): return '/'.join(path.split('/')[1:])

def rcar(path: str): return '/'.join(path.split('/')[-1])

def rcdr(path: str): return '/'.join(path.split('/')[:-1])
