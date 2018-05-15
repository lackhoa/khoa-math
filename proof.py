from prep import *
from typing import List, Tuple, Set, FrozenSet

# Inference rules: these accept proof lines and return proof lines
def pre_intro(line_num: int, form):
    '''
    Premise introduction
    '''
    ass_pl(form)
    return line(line_num, form, rule_anno('Premise', frozenset()), {line_num})
    
def and_intro(line_num, left, right):
    '''
    A, B => A /\ B
    '''
    assert(left.type == MathType.PL_PROOF_LINE)
    assert(right.type == MathType.PL_PROOF_LINE)

    return line(line_num, conj(left.form, right.form), rule_anno('&I', frozenset([left.num, right.num])), left.dep | right.dep)

def and_elim1(line_num, conj):
    '''
    A /\ B => A
    '''
    assert(conj.type == MathType.PL_PROOF_LINE)
    assert(conj.form.cons == PlCons.CONJUNCTION)

    return line(line_num, conj.form.left, rule_anno('&E', frozenset([conj.num])), conj.dep)

def and_elim2(line_num, conj):
    '''
    A /\ B => B
    '''
    assert(conj.type == MathType.PL_PROOF_LINE)
    assert(conj.form.cons == PlCons.CONJUNCTION)

    return line(line_num, conj.form.right, rule_anno('&E', frozenset([conj.num])), conj.dep)

def rule_anno(symbol: str, args: FrozenSet[int]):
    '''
    Create a Rule Annotation: A str that represents the rule plus a list of arguments
    '''
    assert(iter(args))
    anno = MathObject()
    anno.type = MathType.PL_RULE_ANNOTATION
    anno.symbol = symbol # For example &E, &I...
    anno.args = args
    return anno
    
def line(line_num: int, form, rule_anno, dep: Set[int]):
    '''
    Create a line of formal proof
    '''
    # Checking input types
    assert (form.type == MathType.PL_FORMULA)
    assert (rule_anno.type == MathType.PL_RULE_ANNOTATION)
    
    line = MathObject()
    line.type = MathType.PL_PROOF_LINE
    line.num = line_num # Line Number
    line.form = form # Formula
    line.rule_anno = rule_anno # Rule Annotation
    line.dep = dep # Dependency
    return line

def print_proof(lines: List):
    print('{0:20}{1:6}{2:40}{3}'.format('Dep', 'Line', 'Formula', 'RA'))
    for line in lines:
        line_str = str(line.num)+'.'
        args = ",".join(map(str, line.rule_anno.args))
        form_str = line.form.text
        dep_str = str(line.dep)
        print('{0:20}{1:6}{2:40}{3} {4}'.format(dep_str, line_str, form_str, line.rule_anno.symbol, args))

