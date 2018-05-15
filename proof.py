from prep import *
from typing import List

# Inference rules: these accept proof lines and return proof lines
def pre_intro(line_num: int, form):
    '''
    Premise introduction
    '''
    ass_pl(form)
    return line(line_num, form, 'Premise', {line_num})
    
def and_intro(line_num, left, right):
    '''
    A, B => A /\ B
    '''
    assert(left.type == MathType.PL_PROOF_LINE)
    assert(right.type == MathType.PL_PROOF_LINE)

    return line(line_num, conj(left.form, right.form), '{},{} &I'.format(left.num, right.num), left.dep.union(right.dep))

def and_elim1(line_num, conj):
    '''
    A /\ B => A
    '''
    assert(conj.type == MathType.PL_PROOF_LINE)
    assert(conj.form.cons == PlCons.CONJUNCTION)

    return line(line_num, conj.form.left, '{} &E'.format(conj.num), conj.dep)

def and_elim2(line_num, conj):
    '''
    A /\ B => B
    '''
    assert(conj.type == MathType.PL_PROOF_LINE)
    assert(conj.form.cons == PlCons.CONJUNCTION)

    return line(line_num, conj.form.right, '{} &E'.format(conj.num), conj.dep)

def line(line_num: int, form, rule_anno: str, dep):
    '''
    Represents a line in a formal proof
    '''
    line = MathObject()
    line.type = MathType.PL_PROOF_LINE
    line.num = line_num
    line.form = form # Formula
    line.rule_anno = rule_anno #Rule annotation
    line.dep = dep # Dependency
    return line

def print_proof(lines: List):
    for line in lines:
        print('{0}\t\t{1}.\t\t{2}\t\t{3}'.format(str(line.dep), line.num, line.form.text, line.rule_anno))

