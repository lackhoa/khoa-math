from prep import *
from proof import *

# This file contains inference rules: these take in proof lines, id(int) and return a proof line
# They return None if the inputs are illegal
def pre_intro(form, id_: int):
    '''
    Premise introduction
    '''
    try: ass_pl(form)
    except: return None

    return line(id_, form, rule_anno('Premise', frozenset()), frozenset({id_}))

def and_intro(left, right, id_: int):
    '''
    A, B => A /\ B
    '''
    try:
        assert(left.type == MathType.PL_PROOF_LINE)
        assert(right.type == MathType.PL_PROOF_LINE)
    except: return None

    return line(id_, conj(left.form, right.form), rule_anno('&I', frozenset([left.id_, right.id_])), left.dep | right.dep)

def and_elim1(conj, id_: int):
    '''
    A /\ B => A
    '''
    try:
        assert(conj.type == MathType.PL_PROOF_LINE)
        assert(conj.form.cons == PlCons.CONJUNCTION)
    except: return None

    return line(id_, conj.form.left, rule_anno('&E', frozenset([conj.id_])), conj.dep)

def and_elim2(conj, id_: int):
    '''
    A /\ B => B
    '''
    try:
        assert(conj.type == MathType.PL_PROOF_LINE)
        assert(conj.form.cons == PlCons.CONJUNCTION)
    except: return None

    return line(id_, conj.form.right, rule_anno('&E', frozenset([conj.id_])), conj.dep)

def modus_ponens(conditional, antecedent, id_):
    '''
    P -> Q, P |- Q
    '''
    try:
        assert(conditional.type == MathType.PL_PROOF_LINE)
        assert(conditional.form.cons == PlCons.CONDITIONAL)
        assert(antecedent.type == MathType.PL_PROOF_LINE)
        assert(antecedent.form.text == conditional.form.ante.text)
    except: return None

    return line(id_, conditional.form.conse, rule_anno('MP', frozenset({conditional.id_, antecedent.id_})), conditional.dep | antecedent.dep)

def assume(form, id_: int):
    '''
    Assume something
    '''
    try:
        assert(form.type == MathType.PL_FORMULA)
    except: return None

    return line(id_, form, rule_anno('A', frozenset()), frozenset({id_}))

def cp(antecedent, consequent, id_: int):
    '''
    Assume p, q |- p -> q
    It is conditional introduction, I don't know why it's called cp
    '''
    try:
        assert(antecedent.type == MathType.PL_PROOF_LINE)
        assert(consequent.type == MathType.PL_PROOF_LINE)
        # the antecedent must be an assumption
        assert(antecedent.rule_anno.symbol == 'A')
        # the consequent must depends on the assumption
        assert(antecedent.id_ in consequent.dep)
    except: return None

    return line(id_, cond(antecedent.form, consequent.form), rule_anno('CP', frozenset({antecedent.id_, consequent.id_})), consequent.dep - antecedent.dep)

def bicond_intro(lr_line, rl_line, id_: int):
    # P -> Q, Q -> P |- P <-> Q
    try:
        assert(lr_line.type == MathType.PL_PROOF_LINE)
        assert(lr_line.form.cons == PlCons.CONDITIONAL)
        assert(rl_line.type == MathType.PL_PROOF_LINE)
        assert(rl_line.form.cons == PlCons.CONDITIONAL)
    except: return None

    return line(id_, bicond(lr_line.form.ante, rl_line.form.ante), rule_anno('<->I', frozenset({lr_line.id_, rl_line.id_})), lr_line.dep | rl_line.dep)

def bicond_elim(bicon, id_: int):
    # P <-> Q |- (P -> Q) & (Q -> P)
    try:
        assert(bicon.type == MathType.PL_PROOF_LINE)
        assert(bicon.form.cons == PlCons.BICONDITIONAL)
    except: return None

    left_right = cond(bicon.form.left, bicon.form.right)
    right_left = cond(bicon.form.right, bicon.form.left)
    return line(id_, conj(left_right, right_left), rule_anno('<->E', frozenset({bicon.id_})), bicon.dep)

def dne(p_line, id_: int):
    '~~P |- P'
    try:
        assert(p_line.type == MathType.PL_PROOF_LINE)
        assert(p_line.form.cons == PlCons.NEGATION)
        assert(p_line.form.form.cons == PlCons.NEGATION)
    except:
        return None

    return line(id_, p_line.form.form.form, rule_anno('DNE', frozenset({p_line.id_})), p_line.dep)

def dni(p_line, id_: int):
    'P |- ~~P'
    try:
        assert(p_line.type == MathType.PL_PROOF_LINE)
    except:
        return None

    return line(id_, neg(neg(p_line.form)), rule_anno('DNI', frozenset({p_line.id_})), p_line.dep)

def modus_tollens(cond, n_conse, id_: int):
    try:
        assert(cond.type == MathType.PL_PROOF_LINE)
        assert(n_conse.type == MathType.PL_PROOF_LINE)
        assert(cond.form.cons == PlCons.CONDITIONAL)
        assert(n_conse.form.cons == PlCons.NEGATION)
        assert(cond.form.conse == n_conse.form.form)
    except: return None

    return line(id_, neg(cond.form.ante), rule_anno('MT', frozenset({cond.id_, n_conse.id_})), cond.dep | n_conse.dep)

def or_intro_right(true_line, other_form, id_: int):
    '''
    P |- P \/ Q
    '''
    try:
        assert(true_line.type == MathType.PL_PROOF_LINE)
        assert(other_form.type == MathType.PL_FORMULA)
    except AssertionError:
        return None

    return line(id_, disj(true_line.form, other_form), rule_anno('vI-left', [true_line.id_]), true_line.dep)

def or_intro_left(other_form, true_line, id_: int):
    '''
    P |- Q \/ P
    '''
    try:
        assert(true_line.type == MathType.PL_PROOF_LINE)
        assert(other_form.type == MathType.PL_FORMULA)
    except AssertionError:
        return None

    return line(id_, disj(other_form, true_line.form), rule_anno('vI-right', [true_line.id_]), true_line.dep)

def or_elim(disj, left_assumption, left_conclusion, right_assumption, right_conclusion, id_: int):
    try:
        assert(disj.type == MathType.PL_PROOF_LINE)
        assert(left_assumption.type == MathType.PL_PROOF_LINE)
        assert(left_conclusion.type == MathType.PL_PROOF_LINE)
        assert(right_assumption.type == MathType.PL_PROOF_LINE)
        assert(right_conclusion.type == MathType.PL_PROOF_LINE)
        assert(disj.form.cons == PlCons.DISJUNCTION)
        assert(disj.form.left == left_assumption.form)
        assert(disj.form.right == right_assumption.form)
        assert(left_conclusion.form == right_conclusion.form)
        assert(left_assumption.rule_anno.symbol == 'A')
        assert(right_assumption.rule_anno.symbol == 'A')

    except AssertionError:
        return None

    return line(id_,
            form=left_conclusion.form,
            rule_anno=rule_anno('vE', {disj.id_, left_assumption.id_, left_conclusion.id_, right_assumption.id_, right_conclusion.id_}),
            dep=(disj.dep | left_conclusion.dep | right_conclusion.dep)- (left_assumption.dep | right_assumption.dep))
