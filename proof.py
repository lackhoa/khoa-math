from khoa_math import MathType
from wff import PlCons
from misc import MyEnum

from enum import auto

# This file contains the definitions of formal prepositional proofs

class ProofCons(MyEnum):
    AND_INTRO = auto()


def inference_rules(child, parent):
    new_nodes = []
    role = child['role']
    val = child['value']
    proof_cons_set = set(list(ProofCons))

    if role == 'type':
        # This clause lists all constructors for inferences
        if val == {MathType.PL_PROOF}:
            # Proof has the formula content, dependency and constructor
            new_nodes += [dict(value=set(list(ProofCons)), path='cons')]
            new_nodes += [dict(value={KSet.UNKNOWN}, path='form')]
            new_nodes += [dict(value={MathType.PL_FORMULA}, path='form/type')]
            new_nodes += [dict(value={KSet.UNKNOWN}, path='dep')]

    elif role == 'cons':
        # This clause provides proof constructors
        if val == {ProofCons.AND_INTRO}:
            # and intro has left and right proof
            new_nodes += [dict(value=None, path='left')]
            new_nodes += [dict(value=None, path='right')]
            new_nodes += [dict(value={MathType.PL_PROOF}, path='left/type')]
            new_nodes += [dict(value={MathType.PL_PROOF}, path='right/type')]

    return new_nodes

