from prep import *
from typing import List, Tuple, Set, FrozenSet

# Inference rules: these accept input proof lines and return ONE proof line
def pre_intro(form):
    '''
    Premise introduction
    '''
    ass_pl(form)
    return lambda l_num: line(l_num, form, rule_anno('Premise', frozenset()), frozenset({l_num}))
    
def and_intro(left, right):
    '''
    A, B => A /\ B
    '''
    assert(left.type == MathType.PL_PROOF_LINE)
    assert(right.type == MathType.PL_PROOF_LINE)

    return lambda l_num: line(l_num, conj(left.form, right.form), rule_anno('&I', frozenset([left.num, right.num])), left.dep | right.dep)

def and_elim1(conj):
    '''
    A /\ B => A
    '''
    assert(conj.type == MathType.PL_PROOF_LINE)
    assert(conj.form.cons == PlCons.CONJUNCTION)

    return lambda l_num: line(l_num, conj.form.left, rule_anno('&E', frozenset([conj.num])), conj.dep)

def and_elim2(conj):
    '''
    A /\ B => B
    '''
    assert(conj.type == MathType.PL_PROOF_LINE)
    assert(conj.form.cons == PlCons.CONJUNCTION)

    return lambda l_num: line(l_num, conj.form.right, rule_anno('&E', frozenset([conj.num])), conj.dep)

def modus_ponens(conditional, antecedent):
    '''
    P -> Q, P |- Q
    '''
    assert(conditional.type == MathType.PL_PROOF_LINE)
    assert(conditional.form.cons == PlCons.CONDITIONAL)
    assert(antecedent.type == MathType.PL_PROOF_LINE)
    assert(antecedent.form.text == conditional.form.ante.text)
    
    return lambda l_num: line(l_num, conditional.form.conse, rule_anno('MP', frozenset({conditional.num, antecedent.num})), conditional.dep | antecedent.dep)

def assume(form):
    '''
    Assume something
    '''
    assert(form.type == MathType.PL_FORMULA)
    
    return lambda l_num: line(l_num, form, rule_anno('A', frozenset()), frozenset({l_num}))

def cp(antecedent, consequent):
    '''
    Assume p, q |- p -> q
    '''
    assert(antecedent.type == MathType.PL_PROOF_LINE)
    assert(consequent.type == MathType.PL_PROOF_LINE)
    # the antecedent must be an assumption
    assert(antecedent.rule_anno.symbol == 'A')
    # the consequent must depends on the assumption
    assert(antecedent.num in consequent.dep)
    
    return lambda l_num: line(l_num, cond(antecedent.form, consequent.form), rule_anno('CP', frozenset({antecedent.num, consequent.num})), consequent.dep - antecedent.dep)
    
    
# Math objects concerning proofs
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
    
def line(line_num: int, form, rule_anno, dep: FrozenSet[int]):
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

# ToString() functions:
def str_line(line):
    line_str = str(line.num)+'.'
    args = ",".join(map(str, line.rule_anno.args))
    form_str = line.form.text
    dep_str = '{' + ','.join(map(str, line.dep)) + '}'
    return '{0:15}{1:6}{2:60}{3} {4}'.format(dep_str, line_str, form_str, line.rule_anno.symbol, args)
    
def str_proof(lines: List):
    result = '{0:15}{1:6}{2:60}{3}\n'.format('Dep', 'Line', 'Formula', 'Rule Annotation')
    for line in lines:
        result += str_line(line) + '\n'
    return result