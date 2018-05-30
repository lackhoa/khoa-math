from enum import Enum, auto

# Awesome class to name Enums
class MyEnum(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

    def __repr__(self):
        """Return a more subtle representation"""
        return str(self)

