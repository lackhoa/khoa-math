from enum import Enum, auto

# This file contains the basis of mathematics

class MathObject():
    '''
    This class is the base for all mathematical objects, that's why it doesn't do anything
    '''
    def __init__(self, type_, text: str = ''):
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
        
    def __hash__(self):
        '''
        We vow that MathObjects will never change once they're created
        '''
        return id(self)

    def __repr__(self):
        return self.text

class MathType(Enum):
    '''
    All MathObject should have a type belonging to this enum
    But, since there are so many types, sometimes you can just use strings
    '''
    PL_FORMULA = 'PL Formula'
    PL_RULE_ANNOTATION = 'PL_RULE_ANNOTATION'
    PL_PROOF_LINE = 'PL_PROOF_LINE'
    PL_CONNECTION = 'PL_CONNECTION'
    PL_PROOF = 'PL_PROOF'
    PL_THEOREM = 'PL_THEOREM'
    PL_TRUTH = 'PL_TRUTH'
