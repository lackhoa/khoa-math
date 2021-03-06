from misc import *

from typing import *
from enum import Enum
from pprint import pformat


class MObj(Enum):
    UNIT = 'UNIT'
    def __and__(self, other: Union['MObj', 'Atom', 'Mole']):
        return MObj.UNIT if other is MObj.UNIT else other


class Atom:
    def __init__(self,
                 content: Optional[Iterable] = None,
                 qualifier: Optional[Callable[..., bool]] = None,
                 custom_repr: Optional[str] = None):
        """Content should be set for better performance"""
        assert((content is None) ^ (qualifier is None)),\
                'One and only one of either content or qualifier should be present'
        self.content = content
        self.qualifier, self.custom_repr = qualifier, custom_repr

    @property
    def content(self):
        if self._content is None: return None
        else:
            save, res = tee(self._content)
            # Iteration on the content property won't affect the original iterable
            self._content = save
            return res

    @content.setter
    def content(self, value):
        self._content = value

    def __eq__(self, other):
        if self.qualifier is None and other.qualifier is None:
            return set(self.content) == set(other.content)
        else:
            return self.qualifier == other.qualifier

    def __hash__(self) -> int:
        if self.content is not None:
            return hash(frozenset(self.content))
        else: return hash(self.qualifier)

    def clone(self) -> 'Atom':
        # Content is already a copy, qualifier and custom_repr are immutable
        return Atom(self.content, self.qualifier, self.custom_repr)

    def __repr__(self) -> str:
        def recur(thing):
            if type(thing) in [str, Mole]:
                return str(thing)
            else:
                try: return '{{{0}}}'.format(', '.join(recur(item) for item in thing))
                except TypeError: return str(thing)
        left_sur, right_sur = '<', '>'
        core: str
        if self.custom_repr: core = self.custom_repr
        elif self.is_explicit(): core = ' | '.join(map(recur, self.content))
        else: core = '?' + str(self.qualifier) + '?'
        return '{}{}{}'.format(left_sur, core, right_sur)

    def __len__(self) -> int:
        if hasattr(self.content, '__len__'): return len(self.content)
        else: return sum(1 for _ in self.content)

    def is_explicit(self):
        return (self.content is not None)

    def __getitem__(self, index: int):
        """For explicit atoms only."""
        res = nth(self.content, index)
        if res is not None: return res
        else: raise IndexError

    def __iter__(self):
        """For explicit atoms only."""
        return iter(self.content)

    def __call__(self, val):
        """Usable for all atoms."""
        if self.is_explicit(): return (val in self.content)
        else: return self.qualifier(val)

    def is_empty(self):
        return (len(self) == 0) if self.is_explicit() else False

    def is_singleton(self):
        return (len(self) == 1) if self.is_explicit() else False

    def __and__(self, other: Union['Atom', 'Mole', 'MObj']):
        if other is MObj.UNIT:
            return self
        elif type(other) is Mole:
            return NONE
        elif type(other) is Atom:
            res: 'Atom'
            e1, e2 = self.is_explicit(), other.is_explicit()
            if e1:
                if e2:
                    # Both are explicit: result is explicit
                    try:
                        # Special treatment for types that implements union
                        res = Atom(content = self.content & other.content)
                    except TypeError:
                        res = Atom(content = filter(other, self))
                else:
                    # Only `self` is explicit: result is explicit
                    res = Atom(content = filter(other, self))
            elif e2:
                # Only `other` is explicit: result is explicit
                res = Atom(content = filter(self, other))
            else:
                # Either is explicit: result is implicit
                res = Atom(qualifier = lambda x: self(x) and other(x))
            return res


# Some handy atoms
ANY       = Atom(qualifier = lambda x: True, custom_repr='ANY')
NONE      = Atom(content   = set(), custom_repr='NONE')
STR       = Atom(qualifier = lambda x: type(x) is str, custom_repr='STR')
SET       = Atom(qualifier = lambda x: type(x) in [set, frozenset],
            custom_repr='SET')
INT       = Atom(qualifier = lambda x: type(x) is int, custom_repr='INT')
SINGLETON = Atom(qualifier = lambda x: type(x) in [set, frozenset] and len(x) == 1)


class Mole(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def complexity(self):
        return 1 + sum(k.complexity for k in self.values() if type(k) is Mole)

    def __setitem__(self, path: str, value):
        assert(type(value) in [Mole, Atom]),\
                'Watch the type!'
        assert(path != ''),\
                'You don\'t have to do this! You don\'t need to do this!'
        if car(path) == path:
            super().__setitem__(path, value)
        else:
            if car(path) in self:
                self[car(path)][cdr(path)] = value
            else:
                self[car(path)] = Mole()  # This is the commitment
                self[car(path)][cdr(path)] = value

    def __getitem__(self, path: str):
        if path == '': return self  # Special property
        elif car(path) == path: return super().__getitem__(path)
        else: return self[car(path)][cdr(path)]

    def __missing__(self, key):
        return MObj.UNIT

    def __hash__(self) -> int:
        """Hopefully this does not take too much time"""
        return hash(tuple(sorted(self.items(), key=lambda item: item[0])))

    def __repr__(self) -> str:
        def normalize(self):
            res = {}
            for key in self:
                if type(self[key]) is Mole:
                    res[key] = normalize(self[key])
                else:
                    res[key] = self[key]
            return res
        def prune(d):
            if '_text' in d and d['_text'].is_singleton():
                d = '^{}^'.format(only(d['_text']))
            else:
                for key in d:
                    if type(d[key]) is dict:
                        d[key] = prune(d[key])
            return d
        return pformat(prune(normalize(self)))

    def __and__(self, other: ['Mole', Atom, MObj]):
        if other is MObj.UNIT:
            return self
        elif type(other) is Atom:
            return NONE
        elif type(other) is Mole:
            res = Mole()
            for key in self.keys() | other.keys():
                res[key] = self[key] & other[key]
            return res
    
    def is_inconsistent(self) -> bool:
        res = False
        for key in self:
            if type(self[key]) is Mole and self[key].is_inconsistent():
                res = True; break
            elif type(self[key]) is Atom and self[key].is_empty():
                res = True; break
        return res

    def clone(self) -> 'Mole':
        res = Mole()
        for key in self:
            # `self[key]` is a `Atom` or `Mole`, which has clone()
            res[key] = self[key].clone()
        return res


def wr(value):
    """Stands for 'wrap'"""
    return value if type(value) is Mole else Atom(content={value})


def only(singleton: Union[Atom, Mole]):
    if type(singleton) is Mole:
        return singleton
    else:
        assert(singleton.is_singleton()), 'This set is NOT a singleton'
        return singleton[0]


# A bit of testing
from pprint import pprint as pp
if __name__ == '__main__':
    atom1 = Mole(_types = wr('WFF'), _cons = wr('CONJUNCTION'))
    atom2 = Mole(_types = wr('WFF'), _cons = wr('CONJUNCTION'))
    atom3 = Mole(_types = wr('WFF'), _cons = wr('NEG'), body=Mole())
    atom4 = Mole(_types = wr('WFF'), _cons = wr('ATOM'), _text=Atom({'5'}))
    pp(atom3, width=3)
    atom3['body/name'] = wr('Greese')
    atom4['body/blood_type'] = wr('A')
    atom4['_text'] = wr('tasty')
    atom3['body']['_text'] = wr('gross')
    print('Atom 3'); print(str(atom3))
    atom3_old, atom4_old = atom3.clone(), atom4.clone()
    atom5 = atom3 & atom4
    assert(atom3_old == atom3); assert(atom4_old == atom4)
    print('Atom 5'); pp(atom5)
    atom6 = wr('A Atom')
    atom7 = atom3 & atom6
    atom8 = atom4 & atom3
    assert(atom5 == atom8)
    assert(atom5.is_inconsistent())
    print('Atom 7'); pp(atom7)
    print('Atom 8'); pp(atom8)
    assert(atom1 == atom2)
    s1 = Atom({2,3,5,1,4})
    s2 = Atom([1,2,3,4,5])
    assert(s1 == s2)
    print('Atom 3\'s complexity: {}'.format(atom3.complexity))
    print('Atom 5\'s complexity: {}'.format(atom5.complexity))
    print('Atom 8\'s complexity: {}'.format(atom8.complexity))
