from kset import *
from misc import *
from khoa_math import *
from k_math_more import *
from type_mgr import *

from anytree import PreOrderIter, RenderTree

def k_enumerate(root: MathObj):
    if type(root) == Atom:
        if root.values.is_explicit():
            for x in root.values:
                yield Atom(role= root.role, values = KSet(x))
        else:
            print('Result cannot be enumerated!')
    elif type(root) == Molecule:
        for i, x in enumerate(list_cons(root.type)):
            res = Molecule(role='root', type_=root.type, cons=x)
            res.name = str(i)
            yield res


root = Molecule(role = 'root', type_ = MathType.WFF)
res = k_enumerate(root)
for t in res:
    print(RenderTree(t))
