from misc import MyEnum, car, cdr, rcar, rcdr
from kset import KSet, KConst

from typing import *
from pprint import pformat


class Mole(dict):
    def __init__(self,
                 type_: str  = None,
                 con  : str  = None,
                 **kwargs):
        """
        If you provide `type_`, it will overwrite `types`,
        Same with `con`.
        If you don't provide anything, they will be initialized with STR.
        """
        super().__init__(**kwargs)
        if type_ is not None: self.type = type_
        elif 'type' not in self: self['_types'] = KConst.STR.value
        if con is not None: self.con = con
        elif '_cons' not in self: self['_cons'] = KConst.STR.value

    def __setitem__(self, key, value):
        assert(type(value) == Mole or type(value) == KSet), 'Watch the type!'
        super().__setitem__(key, value)

    @property
    def type(self):
        assert(self['_types'].is_singleton()), 'Types not a singleton'
        return self['_types'][0]

    @type.setter
    def type(self, value):
         self['_types'] = KSet(frozenset({value}))

    @property
    def con(self):
        assert(self['_cons'].is_singleton()), 'Constructors not a singleton'
        return self['_cons'][0]

    @con.setter
    def con(self, value):
        self['_cons'] = KSet(frozenset({value}))

    def __getitem__(self, path: str):
        if path == '': return self
        elif car(path) == path: return super().__getitem__(path)
        else: return super().__getitem__(car(path)).__getitem__(cdr(path))

    def has_path(self, path: str) -> bool:
        try: self.get_path(path); return True
        except KeyError: return False

    def pave_way(self, path: str):
        """
        Keep attaching dummy molecules until `self.has_path(path)` is True
        """
        if not self.has_path(path):
            if car(path) not in self:
                dummy_mole = Mole()
                self[car(path)] = next_mole 
                dummy_mole.pave_way(cdr(path))
            else:
                next_mole = self[car(path)]
                next_mole.pave_way(cdr(path))

    def merge(self, val: Union[KSet, 'Mole'], path: str = ''):
        """
        Merge/attach `value` to this molecule,
        with optional path down the line
        """
        # Empty path
        if (path == ''):
            assert(type(val) is Mole), 'It doesn\'t make sense to merge a KSet to a molecule'
            for key in val:
                self.merge(val=val[key], path=key)
        # When the path has many levels down
        elif rcdr(path) != '':
            self.pave_way(rcdr(path))
            self.get_path(rcdr(path)).merge(val=val, path=rcar(path))
        # When the path goes down only one level
        elif path not in self:
            self[path] = val
        else:
            if type(val) != Mole:  # `val` is a KSet
                self[path] = self[path] & val
            else:
                assert(type(val) is Mole)
                for key in val:
                    assert(type(self[path]) is Mole)
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


# A bit of testing
from pprint import pprint as pp
if __name__ == '__main__':
    atom1 = Mole(type_ = 'WFF', con = 'CONJUNCTION')
    atom2 = Mole(type_ = 'WFF', con = 'CONJUNCTION')
    atom3 = Mole(type='WFF', con='NEG', body=Mole())
    atom4 = Mole(type='WFF', con='ATOM', text=KSet({'5'}))
    pp(atom3, width=3)
