from misc import MyEnum, car, cdr, rcar, rcdr
from kset import KSet, KConst

from typing import *
from pprint import pformat


class Mole(dict):
    def __init__(self,
                 type_: str  = None,
                 con  : str  = None,
                 dic  : dict = {'types': KConst.STR.value, 'cons': KConst.STR.value}):
        """
        If `type_` is set, the corresponding key `types`
        in `dic` will be ignored. The same thing goes for `con`
        """
        self.update(dic)
        if type_ is not None: self.type = type_
        if con is not None: self.con = con

    def __repr__(self) -> str:
        return pformat(self)

    @property
    def type(self):
        assert(self.types.is_singleton()), 'Types not a singleton'
        return self.types[0]

    @type.setter
    def type(self, value):
         self.types = KSet(frozenset({value}))

    @property
    def con(self):
        assert(self.cons.is_singleton()), 'Constructors not a singleton'
        return self.cons[0]

    @con.setter
    def con(self, value):
        self.cons = KSet(frozenset({value}))

    def get_path(self, path: str):
        if path == '': return self
        elif car(path) == path: return self[path]
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
        Merge/attach `value` to this molecule,
        with optional path down the line
        """
        assert(path != ''), 'Empty path doesn\'t make sense'
        # When the path has many levels down
        if rcdr(path) != '':
            self.pave_way(rcdr(path))
            self.get_path(rcdr(path)).merge(val=val, path=rcar(path))
        # When the path goes down only one level
        elif path not in self:
            self[path] = val
        else:
            if type(val) != Mole:  # `val` is a KSet
                self[path] = self[path] & val
            else:  # `val` is a molecule, do recursive merge
                for key in val:
                    # We assume that `self[path]` must also be a molecule
                    self[path].merge(val=val[key], path=key)

    def clone(self) -> 'Mole':
        res = Mole()
        for key in self:
            # `self[key]` is either a `KSet` or a `Mole`
            # which has `clone()`
            res[key] = self[key].clone()
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
