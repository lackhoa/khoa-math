from misc import MyEnum, car, cdr, rcar, rcdr
from kset import KSet, KConst

from typing import *
from pprint import pformat


class Mole(dict):
    def __init__(self,
                 type_: KSet = KConst.STR.value,
                 cons : KSet = KConst.STR.value,
                 con  : str  = None,
                 dic  : dict = {})
        """
        Specify either `cons` (if has multiple constructors)
        or `con`(if has one constructor)
        """
        kelf.type = type_
        self.cons = KSet(frozenset({con})) if con is not None else cons
        self.update(dic)

    def __repr__(self) -> str:
        return pformat(self)

    @property
    def cons(self):
        return self['cons']

    @cons.setter
    def cons(self, value):
        self['cons'] = value

    @property:
    def type(self):
        return self['type']

    @type.setter:
    def type(self, value):
        self['type'] = value

    @property
    def con(self):
        assert(self.cons.is_singleton()), 'Constructors not a singleton'
        return self.cons[0]

    @con.setter
    def con(self, value):
         self.cons = KSet(frozenset({value}))

    def get_path(self, path: str):
        if path == '': return self
        else: return self[car(path)].get_path(cdr(path))

    def has_path(self, path: str) -> bool:
        try: self.get_path(path); return True
        except KeyError: return False

    def pave_way(self, path: str):
        """
        Keep attaching new molecules until `self.has_path(path)` is True
        """
        if not self.has_path(path):
            if car(path) not in self:
                next_mole = Mole()  # a dummy molecule
                self[car(path)] = next_mole 
            else:
                next_mole = self[car(path)]
            next_mole.pave_way(cdr(path))

    def merge(self, val, path: str):
        """
        Merge/attach `value` to this molecule, with optional path down the line
        """
        assert(path != ''), 'Empty path doesn\'t make sense'
        # When the path has many levels down
        if rcdr(path) != '':
            self.pave_way(rcdr(path))
            self.get_path(rcdr(path)).attach(val=val, path=rcar(path), mode=mode)
        # When the path goes down only one level
        elif path not in self:
            self[path] = val
        else:
            if type(val) != Mole:  # `val` is a KSet
                self[path] = self[path] & val
            else:  # `val` is a molecule, do recursive merge
                for key in val:
                    self[path].merge(val=val[key], path=key, mode=mode)

    def clone(self) -> 'Mole':
        res = Mole()
        for key in self:
            # `self[key]` is either `KSet` or `Mole`
            # which has `clone()`
            clone[key] = self[key].clone()
        return res

    def __eq__(self, other) -> bool:
        res = True
        if len(self) == len(other):
            for key in self:
                if (key not in other) or (self[key] != other[key]):
                    res = False; break
        else:
            res = False
        return res

    def __hash__(self) -> int:
        """Hopefully this does not take too much time"""
        return hash(tuple(self.items()))
