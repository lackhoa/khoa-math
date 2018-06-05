from enum import Enum, auto

# Awesome class to name Enums
class MyEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        """Return a more subtle representation"""
        return self.value


AtomTup = namedtuple('AtomTuple', ['path', 'value'])
MoleTup = namedtuple('MoleculeTuple', ['path', 'type_'])
