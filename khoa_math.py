from enum import Enum, auto

# This file contains the basis of mathematics

class MathObject():
    '''
    This class is the base for all mathematical objects, that's why it doesn't do anything
    '''
    def __init__(self, type_, text: str='', val=self):
        self.text = text
        self.type = type_
        self.val = val

    def __eq__(self, other):
        """
        Overrides the default implementation
        Compare the attributes of the object rather than the IDs
        """
        if isinstance(self, other.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __hash__(self):
        '''
        We vow that MathObjects will never change once they're created
        '''
        return id(self)

    def __repr__(self):
        return self.text

# Awesome class to name Enums
class AutoName(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return name

class MathType(AutoName):
    '''
    All MathObject should have a type belonging to this enum
    But, since there are so many types, sometimes you can just use strings
    '''
    PL_FORMULA = auto()
    PL_RULE_ANNOTATION = auto()
    PL_PROOF_LINE = auto()
    PL_CONNECTION = auto()
    PL_PROOF = auto()
    PL_THEOREM = auto()
    PL_TRUTH = auto()
    SET = auto()
    UNKNOWN = auto()