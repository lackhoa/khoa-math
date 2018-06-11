from misc import MyEnum


class RelType(MyEnum)
    """Each relation's value is its arity"""
    EQ = 2
    FUNC = 2
    UNION = 3


class Rel:
    def __init__(self, type_: RelType, tup):
        assert(len(tup) == type_.value),\
            'Expected tuple with arity {}, got {}'.format(type_.value, len(tup))
        self.type = type_
        self.tup = tup
