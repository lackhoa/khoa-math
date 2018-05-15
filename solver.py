from prep import *
from proof import *

def prove(premises, conclusion, loop_limit=5, len_limit=20):
    '''
    Prove some formula from the premises
    :param loop_limit: How many loops does the program take at most
    :param len_limit: The length limit of the text of a sentence
    '''
    for p in premises:
        assert(p.type == MathType.PL_PROOF_LINE)
    assert(conclusion.type == MathType.PL_FORMULA)
    proven = False
    # The lines of the proof
    lines = premises

    goals = [conclusion] # The item at the end of the list is what we're focusing one
    loop_count = 0
    while conclusion in goals and loop_count <= loop_limit:
        loop_count += 1
        # goals-oriented approach first:
        # Vacuous:
        if search_form(lines, goals[-1]):
            goals.pop()
            continue

        # And-intro:
        if(goals[-1].cons == PlCons.CONJUNCTION):
            l = search_form(lines, goals[-1].left)
            r = search_form(lines, goals[-1].right)
            if l and r:
                add_line(lines, and_intro(len(lines), l, r), len_limit)
                goals.pop()
                continue
            # If that doesn't work, try breaking the conjunction into two branches:
            tmp = goals[-1]
            goals.append(tmp.left)
            goals.append(tmp.right)

        # And-elim1:
        def f(line):
            return line.form.cons == PlCons.CONJUNCTION and line.form.left == goals[-1]
        for line in filter(f, lines):
            add_line(lines, and_elim1(len(lines), line), len_limit)
            goals.pop()
            continue

        # And-elim2:
        def f(line):
            return line.form.cons == PlCons.CONJUNCTION and line.form.right == goals[-1]
        for line in filter(f, lines):
            add_line(lines, and_elim2(len(lines), line), len_limit)
            goals.pop()
            continue

        # Then we switch to... guessing aimlessly (with restraint, of course)
        # And-intro
        # for (line1, line2) in [(line1, line2) for line1 in lines for line2 in lines]:
        #     l = and_intro(len(lines), line1, line2)
        #     add_line(lines, l, len_limit)

        # And-elim1 with and-elim2:
        def f(line):
            return line.form.cons == PlCons.CONJUNCTION
        for line in filter(f, lines):
            l1 = and_elim1(len(lines), line)
            add_line(lines, l1, len_limit)
            l2 = and_elim2(len(lines), line)
            add_line(lines, l2, len_limit)

    solved = conclusion not in goals
    if solved:
        print_proof(lines)
    else:
        print("Failed!")

    return False if solved else True

def add_line(lines, line, len_limit):
    '''
    Safely add a line to the proof
    '''
    if (not search_form(lines, line.form)) and (len(line.form.text) <= len_limit) and (line.num == len(lines)):
        lines.append(line)

def search_form(lines, form):
    '''
    Search in a list of lines for a particular formula
    '''
    for line in lines:
        if line.form.text == form.text:
            return line
    return None
