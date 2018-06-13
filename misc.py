from enum import Enum, auto
from typing import Iterable


# Awesome class to name Enums
class MyEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        """Return a more subtle representation"""
        return self.value


def take_index(L: Iterable, n: int):
    """Return `element` n of an iterable `L`"""
    for i, v in enumerate(L):
        if i == n: return v
    else: raise IndexError


def car(path: str): return path.split('/')[0]

def cdr(path: str): return '/'.join(path.split('/')[1:])

def rcar(path: str): return '/'.join(path.split('/')[-1])

def rcdr(path: str): return '/'.join(path.split('/')[:-1])
