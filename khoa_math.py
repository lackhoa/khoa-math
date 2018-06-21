from misc import MyEnum, car, cdr, rcar, rcdr
from kset import *

from typing import *
from pprint import pformat


class Mole(dict):
    def __init__(self, **kwargs):
        """
        If you don't provide _types of _cons,
        they will be initialized with STR.
        """
        super().__init__(**kwargs)
        if '_types' not in self: self['_types'] = STR
        if '_cons' not in self: self['_cons'] = STR

    def __setitem__(self, key, value):
        assert(type(value) == Mole or type(value) == KSet), 'Watch the type!'
        super().__setitem__(key, value)

    def __getitem__(self, path: str):
        if path == '': return self
        elif car(path) == path: return super().__getitem__(path)
        else: return super().__getitem__(car(path)).__getitem__(cdr(path))

    def has_path(self, path: str) -> bool:
        try: self[path]; return True
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
            self[rcdr(path)].merge(val=val, path=rcar(path))
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

    def __hash__(self) -> int:
        """Hopefully this does not take too much time"""
        return hash(tuple(sorted(self.items(), key=lambda item: item[0])))


def wr(value):
    """Stands for 'wrap'"""
    return value if type(value) is Mole else KSet(content={value})


def only(singleton: Union[KSet, Mole]):
    if type(singleton) is Mole:
        return singleton
    else:
        assert(singleton.is_singleton()), 'This set is NOT a singleton'
        return singleton[0]


def adapter(fun: Callable):
    """
    E.g: if f(a) = b then adapter(f)(KSet({a})) = KSet({b})
    """
    return lambda *args: wr(fun(*map(lambda s: only(s), args)))



# A bit of testing
from pprint import pprint as pp
if __name__ == '__main__':
    atom1 = Mole(_types = wr( 'WFF'), _cons = wr( 'CONJUNCTION'))
    atom2 = Mole(_types = wr( 'WFF'), _cons = wr( 'CONJUNCTION'))
    atom3 = Mole(_types = wr('WFF'), _cons = wr('NEG'), body=Mole())
    atom4 = Mole(_types = wr('WFF'), _cons = wr('ATOM'), _text=KSet({'5'}))
    pp(atom3, width=3)
    assert(atom1 == atom2)
