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


res = k_enumerate(Atom(role = 'root', values = KSet(content = lambda x: x%2)))
for t in res:
    print(RenderTree(t))
