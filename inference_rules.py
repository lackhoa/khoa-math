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

