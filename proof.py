from prep import *
from typing import List, Tuple, Set, FrozenSet

# This file contains fundamental constructs concerning proofs.
# However, it does not provide a mechanism to prove.

def rule_anno(symbol: str, args: FrozenSet[int]):
    '''
    Create a Rule Annotation: A str that represents the rule plus a list of arguments
    '''
    try:
        assert(iter(args))
    except AssertionError:
        return None

    anno = MathObject(MathType.PL_RULE_ANNOTATION)
    anno.symbol = symbol # For example &E, &I...
    anno.args = args
    anno.text = '{} {}'.format(symbol, ','.join(map(str, args)))
    return anno

def line(id_: int, form, rule_anno, dep: FrozenSet[int]):
    '''
    Create a line of formal proof
    '''
    # Checking input types
    assert (form.type == MathType.PL_FORMULA)
    assert (rule_anno.type == MathType.PL_RULE_ANNOTATION)

    line = MathObject(MathType.PL_PROOF_LINE)
    line.id_ = id_ # It's essentially "line number", I name it like this to emphasize that
        # it's just a short-hand name for the line
    line.form = form # Formula
    line.rule_anno = rule_anno # Rule Annotation
    line.dep = dep # Dependency
    def str_line():
        line_str = str(line.id_)+'.'
        args = ",".join(map(str, line.rule_anno.args))
        form_str = line.form.text
        dep_str = '{' + ','.join(map(str, line.dep)) + '}'
        return '{0:15}{1:6}{2:60}{3} {4}'.format(dep_str, line_str, form_str, line.rule_anno.symbol, args)
    line.text = str_line()
    return line

def goal(form, dep: FrozenSet):
    '''
    A goal is what I called a connection: a formula plus a set of dependency lines
    When you achieve a goal (demonstrated the connection),...
    ...you have shown that the given formula can be derived from the given dependency
    This is a conceptual data structure in proofs
    '''
    assert (form.type == MathType.PL_FORMULA)

    goal = MathObject(MathType.PL_CONNECTION)
    goal.form = form
    goal.dep = dep
    goal.text = 'connection({}, {})'.format(form.text, str(dep))
    return goal

def proof(premises: List, conclusion, lines: List):
    '''
    A proof can be taken as a list of proof lines, with clear premise and conclusion
    I can technically do proof checking but damn, that's a lot of work (furthremore it's already a proof)
    :param premises: List of premises (supposed to be set)
    :param conclusion: formula
    :param lines: Indexed set of proof lines
    '''
    # Doing assertion here!
    try:
        assert(conclusion.type == MathType.PL_FORMULA)
        for p in premises:
            assert(p.type == MathType.PL_FORMULA)
        for line in lines:
            assert(line.type == MathType.PL_PROOF_LINE)

        # All the lines that are premises must registered
        assert( premises == [line.form for line in lines if line.rule_anno.symbol == 'Premise'] )
        # The final line must be the conclusion
        assert(lines[-1].form == conclusion)
        premise_lines = [l for l in lines if l.rule_anno.symbol == 'Premise']
        assert(lines[-1].dep.issubset( set([l.id_ for l in premise_lines])) )
    except AssertionError:
        return None

    proof_ = MathObject(MathType.PL_PROOF)
    proof_.lines = lines
    proof_.conclusion = conclusion
    proof_.premises = premises
    proof_.text = str_lines(lines)

    return proof_

def str_lines(lines):
    # Printing out the list of lines
    result = '{0:15}{1:6}{2:60}{3}\n'.format('Dep', 'Line', 'Formula', 'Rule Annotation')
    for line in lines:
        result += line.text + '\n'
    return result

