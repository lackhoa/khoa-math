from prep import *
from proof import *
from typing import Callable

def prove(premises: List, conclusion, loop_limit=30, goal_try_limit=1, goal_queue_limit=8, len_limit=40) -> List:
    '''
    Prove some formula from the premises
    :param premises: A list of formulas as premises
    :param conclusion: One formula as the conclusion
    :param loop_limit: How many loops does the program take at most
    :param goal_try_limit: How many loops does the program take for a goal before shelving it
    :param len_limit: The length limit of the text of a sentence
    '''
    # Check input types:
    for p in premises:
        assert(p.type == MathType.PL_FORMULA)
    assert(conclusion.type == MathType.PL_FORMULA)

    # Check that the conclusion is within length limit:
    assert(len(conclusion.text) <= len_limit), 'Please raise the length limit'
    
    # The main proof lines, will be populated with premises:
    lines = []
        
    # This goal list, which shows the cur_goals we're trying works like a stack or queue
    # We always focus on the item at the end of the goal list
    cur_goals = [conclusion]
    # Store the cur_goals that we've tried and failed:
    tried_goals = []

    # Subroutine to check if the conclusion has not yet been made,
    # which also checks if there is any goal remaining
    def check_goal():
        for goal in cur_goals:
            if conclusion.text == goal.text:
                return True
        return False

    def make_line(l: Callable[..., MathObject]):
        # Returns line if you have lambda, automatically increment line number
        return l(len(lines))

    def add_line(line) -> bool:
        # Safely add a line to the proof
        # returns True if succeeded, False if not
        assert(line.type == MathType.PL_PROOF_LINE)

        # Only reject if there's a line with the same text and dependency (to combat under-dependency)
        # Furthremore, don't assume the same thing twice
        b1 = not [l for l in lines if l.form.text == line.form.text and (l.dep == line.dep or l.rule_anno.symbol == line.rule_anno.symbol == 'A')]
        length_check = len(line.form.text) <= len_limit
        if b1 and length_check:
            print(line.text)
            lines.append(line)
            return True
        return False

    def add_goal(goal) -> bool:
        # Safely add a goal, returns True if successful
        assert(goal.type == MathType.PL_FORMULA)
        length_ok = len(cur_goals) < goal_queue_limit
        tried = lambda: goal.text in [g.text for g in tried_goals]
        trying = lambda: goal.text in [g.text for g in cur_goals]
        succeeded = lambda: search_form(lines, goal)

        if length_ok and (not tried()) and (not trying()) and (not succeeded()):
            cur_goals.append(goal)
            return True
        return False

    # Enough wait, the proofwork starts here:

    # Add premises, and record the line numbers for future use:
    premise_nums = set()
    for premise in premises:
        premise_line = make_line(pre_intro(premise))
        add_line( premise_line )
        premise_nums.add(premise_line.num)

    premise_nums = frozenset(premise_nums) # Lock the premises for good measure

    loop_count = 0 # Keep count to check against the loop limit
    goal_try_count = 0
    # The main loop: as long as the conclusion is there, and
    # we've not exceeded loop quota
    while check_goal() and loop_count <= loop_limit:
        loop_count += 1
        goal_try_count += 1
        # Shelve the goal and try something else if we're stuck:
        if goal_try_count >= goal_try_limit:
            this_goal = cur_goals.pop()
            cur_goals.insert(0, this_goal)
            goal_try_count = 0

        # Check if we've already achieved the goal:
        if search_form(lines, cur_goals[-1]):
            cur_goals.pop()
            continue
        # Note: Do NOT pop the goal queue for the rest of the loop,
        # Because we do not know if the queue is empty
        # If you think you've achieved a goal, simply command 'continue'
        print('Current goal queue (right-most first): '+ str([g.text for g in cur_goals]))

        # Goal-oriented approach first: for rules that has
        # loose requirements, which pollutes the proof lines

        # Conjunction: try and-introduction:
        if cur_goals[-1].cons == PlCons.CONJUNCTION:
            l = search_form(lines, cur_goals[-1].left)
            r = search_form(lines, cur_goals[-1].right)
            if l and r:
                add_line( make_line(and_intro(l, r)) )
                continue
            else:
                # If we don't have the components yet, find them:
                tmp = cur_goals[-1]
                add_goal(tmp.left)
                add_goal(tmp.right)

        # Conditional: use CP tactics
        elif cur_goals[-1].cons == PlCons.CONDITIONAL:
            add_line( make_line(assume(cur_goals[-1].ante)) )
            tmp = cur_goals[-1]
            add_goal(tmp.conse)
            if (search_form(lines, tmp.ante)):
                # If we already possess the consequent, then this is a trap:
                # We must prove the conjunction of the antecedent along with the consequent...
                # ...to "pretend" that we can derive the consequent from the antecedent
                add_goal(conj(tmp.ante, tmp.conse))

        # Biconditional: find the components
        elif cur_goals[-1].cons == PlCons.BICONDITIONAL:
            l, r = cur_goals[-1].left, cur_goals[-1].right
            lr, rl = search_form(lines, cond(l, r)), search_form(lines, cond(r, l))
            if lr and rl:
                add_line( make_line(bicond_intro(lr, rl)) )
                continue
            else:
                # If we don't have the components yet, find them:
                tmp = cur_goals[-1]
                add_goal(cond(tmp.left, tmp.right))
                add_goal(cond(tmp.right, tmp.left))

        # Then we switch to... guessing aimlessly (with restraint, of course)

        # Loop through everything we have, and add more to our knowledge
        for line in lines:
            # If the line contains a conjunction,
            # break it down
            # Try and-elim1:
            if and_elim1(line): add_line( make_line(and_elim1(line)) )
            # Try and-elim2:
            if and_elim2(line): add_line( make_line(and_elim2(line)) )
            # Try biconditional-elim:
            if bicond_elim(line): add_line( make_line(bicond_elim(line)) )

            # If the line contains a conditional,
            # try to get the consequent
            if line.form.cons == PlCons.CONDITIONAL:
                # Try modus ponens:
                ante = search_form(lines, line.form.ante)
                if ante: add_line( make_line(modus_ponens(line, ante)) )
                # If we don't have the antecedent yet, try proving it!
                else: add_goal(line.form.ante)

            # If the line depends on assumptions,
            # make a conditional statement:
            asps = line.dep - premise_nums
            # asps should now contains (potentially many) lines numbers
            # of the assumptions that this line depends on
            # so now we discharge them one by one and see what happens
            for asp_num in asps:
                add_line( make_line(cp(lines[asp_num], line)) )

    solved = conclusion not in cur_goals
    print('\n' + '-'*100)
    if solved:
        cleaned_proof = clean_proof(lines, conclusion)
        print('\nSuccess! Here is the proof:')
        print(str_proof(cleaned_proof))
    else:
        print("Failed! Here's what I found")
        print(str_proof(lines))

    return cleaned_proof if solved else None

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
