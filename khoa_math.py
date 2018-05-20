from enum import Enum, auto

# This file contains the basis of mathematics

class MathObject():
    '''
    This class is the base for all mathematical objects, that's why it doesn't do anything
    '''
    def __init__(self, type_, text: str = ''):
        assert(type(type_) == MathType)
        self.text = text
        self.type = type_
    def __eq__(self, other):
        """
        Overrides the default implementation
        Compare the attributes of the object rather than the IDs
        """
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __repr__(self):
        return self.text

class MathType(Enum):
    PL_FORMULA = auto()
    PL_RULE_ANNOTATION = auto()
    PL_PROOF_LINE = auto()
    PL_CONNECTION = auto()
    PL_PROOF = auto()
    PL_THEOREM = auto()
    PL_TRUTH = autho()
