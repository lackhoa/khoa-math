from prep import *
from proof import *

def prove(premises: List, conclusion, loop_limit=5, len_limit=20) -> List:
    '''
    Prove some formula from the premises
    :param loop_limit: How many loops does the program take at most
    :param len_limit: The length limit of the text of a sentence
    '''
    # Check input types:
    for p in premises:
        assert(p.type == MathType.PL_PROOF_LINE)
    assert(conclusion.type == MathType.PL_FORMULA)
    
    # The main proof lines
    lines = premises
    # This goals list works like a stack
    # We always focus on the item at the end of the goal list
    goals = [conclusion]
    
    loop_count = 0 # Keep count to check against the loop limit
    # The main loop:
    while conclusion in goals and loop_count <= loop_limit:
        loop_count += 1
        print([g.text for g in goals])
        
        # Goal-oriented approach first: see if we can deduce the
        # conclusion immediately
        
        # Check if we've already achieved the goal:
        if search_form(lines, goals[-1]):
            goals.pop()
            continue

        # Try and-intro:
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

        # Try and-elim1:
        con_left = lambda line: line.form.cons == PlCons.CONJUNCTION and line.form.left == goals[-1]
        for line in filter(con_left, lines):
            add_line(lines, and_elim1(len(lines), line), len_limit)
            goals.pop()
            continue

        # Try and-elim2:
        con_right = lambda line: line.form.cons == PlCons.CONJUNCTION and line.form.right == goals[-1]
        for line in filter(con_right, lines):
            add_line(lines, and_elim2(len(lines), line), len_limit)
            goals.pop()
            continue

        # Then we switch to... guessing aimlessly (with restraint, of course)
        l_con = lambda line: line.form.cons == PlCons.CONJUNCTION
        # Loop through everything we have, and try stuffs
        for line in lines:
            if l_con(line):
                # Try and-elim1:
                add_line(lines, and_elim1(len(lines), line), len_limit)
                # Try and-elim2:
                add_line(lines, and_elim2(len(lines), line), len_limit)

    solved = conclusion not in goals
    if solved:
        cleaned_proof = clean_proof(lines, conclusion)
        print_proof(cleaned_proof) # Success!
    else:
        print("Failed!")

    return cleaned_proof if solved else None

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
        # We must compare the text, saying '==' doesn't work!
        if line.form.text == form.text:
            return line
    return None
    
def clean_proof(lines: List, conclusion):
    '''
    Receive a proof, a conclusion and return a clean version of the proof
    '''
    # Checking the input:
    assert(conclusion.type == MathType.PL_FORMULA)
    
    # Check that the there is actually a line containing the proof
    con_line = search_form(lines, conclusion)
    assert(con_line)
    
    # If a line is in tmp1 then it along with all of its
    # 'antecedent' will be added in relevant_line_num
    tmp1 = [l for l in con_line.rule_anno.args]
    
    # Let's fulfill the prophecy above
    relevant_line_num = set()
    relevant_line_num.add(con_line.num)
    relevant_line_num.update(set(tmp1))
    changed = True
    while changed:
        changed = False
        tmp2 = []
        for n in tmp1:
            relevant_line_num.add(n)
            # Since everything traces back to the premise,
            # There should be no infinite loops:
            print(lines[n].rule_anno.symbol)
            if lines[n].rule_anno.symbol != 'Premise':
                changed = True
                tmp2.extend(lines[n].rule_anno.args)
            tmp1 = tmp2
            tmp2 = []
    
    # With all the needed line numbers, let's sort them:
    relevant_line_num = sorted(list(relevant_line_num))
    
    # And then return all the lines
    return [lines[i] for i in relevant_line_num]