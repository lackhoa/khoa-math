from prep import *
from proof import *

def prove(premises: List, conclusion, loop_limit=5, goal_try_limit=5, len_limit=40) -> List:
    '''
    Prove some formula from the premises
    :param loop_limit: How many loops does the program take at most
    :param goal_try_limit: How many loops does the program take for a goal before shelving it
    :param len_limit: The length limit of the text of a sentence
    '''
    # Check input types:
    for p in premises:
        assert(p.type == MathType.PL_PROOF_LINE)
    assert(conclusion.type == MathType.PL_FORMULA)
    
    # Check that the conclusion is within length limit:
    assert(len(conclusion.text) <= len_limit), 'Please raise the length limit'
    
    # The main proof lines
    lines = premises
    # This goals list works like a stack
    # We always focus on the item at the end of the goal list
    goals = [conclusion]
    # Check if the conclusion is not yet made
    # Also checks if there is any goal remaining
    def check_goal():
        for goal in goals:
            if conclusion.text == goal.text:
                return True
        return False
    
    loop_count = 0 # Keep count to check against the loop limit
    goal_try_count = 0
    # The main loop:
    while check_goal() and loop_count <= loop_limit:
        loop_count += 1
        goal_try_count += 1
        # Shelve the goal and try something else if we're stuck:
        if goal_try_count > goal_try_limit:
            this_goal = goals.pop()
            goals = [this_goal].append(goals)
            goal_try_count = 0

        print('Current goal queue (right-most first): '+ str([g.text for g in goals]))
        
        # Goal-oriented approach first: see if we can somehow
        # deduce the conclusion immediately

        # Check if we've already achieved the goal:
        if search_form(lines, goals[-1]):
            goals.pop()
            continue

        # Try and-introduction:
        if(goals[-1].cons == PlCons.CONJUNCTION):
            l = search_form(lines, goals[-1].left)
            r = search_form(lines, goals[-1].right)
            if l and r:
                if add_line(lines, and_intro(len(lines), l, r), len_limit):
                    goals.pop()
                    continue
            # If that doesn't work, try breaking the conjunction into two branches:
            tmp = goals[-1]
            goals.append(tmp.left)
            goals.append(tmp.right)

        # Try and-elim1:
        if check_goal:
            con_left = lambda line: line.form.cons == PlCons.CONJUNCTION and line.form.left == goals[-1]
            for line in filter(con_left, lines):
                if add_line(lines, and_elim1(len(lines), line), len_limit):
                    goals.pop()

        # Try and-elim2:
        con_right = lambda line: line.form.cons == PlCons.CONJUNCTION and line.form.right == goals[-1]
        if check_goal():
            for line in filter(con_right, lines):
                if add_line(lines, and_elim2(len(lines), line), len_limit):
                    goals.pop()
                    break

        # Then we switch to... guessing aimlessly (with restraint, of course)
        l_con = lambda line: line.form.cons == PlCons.CONJUNCTION
        # Loop through everything we have, and try out everything we know
        for line in lines:
            if l_con(line):
                # Try and-elim1:
                add_line(lines, and_elim1(len(lines), line), len_limit)
                # Try and-elim2:
                add_line(lines, and_elim2(len(lines), line), len_limit)

    solved = conclusion not in goals
    if solved:
        cleaned_proof = clean_proof(lines, conclusion)
        print('\nSuccess! Here is the proof:')
        print(str_proof(cleaned_proof))
    else:
        print("Failed!")

    return cleaned_proof if solved else None

def add_line(lines, line, len_limit) -> bool:
    '''
    Safely add a line to the proof
    returns True if succeeded, False if not
    '''
    if (not search_form(lines, line.form)) and (len(line.form.text) <= len_limit) and (line.num == len(lines)):
        print(str_line(line))
        lines.append(line)
        
        return True
        
    return False
        
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
            if lines[n].rule_anno.symbol != 'Premise':
                changed = True
                tmp2.extend(lines[n].rule_anno.args)
            tmp1 = tmp2
    
    # With all the needed line numbers, let's sort them:
    relevant_line_num = sorted(list(relevant_line_num))
    
    # And then return all the lines
    return [lines[i] for i in relevant_line_num]
