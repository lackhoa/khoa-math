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
    cur_goals = []
    # Store the cur_goals that we've tried and failed:
    tried_goals = []

    def add_goal(goal) -> bool:
        nonlocal cur_goals # use the common goal queue, not create another
        # Safely add a goal, returns True if successful
        assert(goal.type == 'goal')
        
        length_ok = len(cur_goals) < goal_queue_limit
        tried = lambda: goal in tried_goals
        trying = lambda: goal in cur_goals
        succeeded = solved_goal(goal)

        if length_ok:
            if (not tried()) and (not trying()) and (not succeeded):
                cur_goals.append(goal)
                return goal
        else:
            # When the goal queue gets too big, just go to sleep,
            # forget everything, and try again from the start:
            print('Cleaning up the goal queue!')
            cur_goals = [conclusion_goal]

        return None

    # Subroutine to search for a formula, returns None if there is none
    def search_form(form, dep=None) -> List:
        '''
        Search in a list of lines that contains a particular formula
        and dependency, if dependency is None then anything goes
        '''
        result = []
        for line in lines:
            if line.form == form and (dep == None or line.dep <= dep):
                result.append(line)
        return result

    def make_line(l: Callable[..., MathObject]):
        # Returns line if you have lambda, automatically increment line number
        return l(len(lines))

    def add_line(line) -> bool:
        # Safely add a line to the proof
        # returns the line if succeeded, None if not
        assert(line.type == MathType.PL_PROOF_LINE)

        # Only reject if there's a line with the same text and dependency (to combat under-dependency)
        # Furthremore, don't assume the same thing twice
        b1 = not [l for l in lines if l.form == line.form and (l.dep == line.dep or l.rule_anno.symbol == line.rule_anno.symbol == 'A')]
        length_check = len(line.form.text) <= len_limit
        if b1 and length_check:
            print(line)
            lines.append(line)
            return line
        return None
    
    def solved_goal(goal):
        # See if we've already achieved a goal:
        return True if search_form(goal.form, goal.dep) else False

    # Enough wait, the proofwork starts here:

    # Add premises, and record the line numbers for future use:
    premise_nums = set()
    print('Introducing premises')
    for premise in premises:
        premise_line = make_line(pre_intro(premise))
        add_line( premise_line )
        premise_nums.add(premise_line.num)

    premise_nums = frozenset(premise_nums) # Lock the premises for good measure

    # The conclusion depends only on the premises
    conclusion_goal = goal(conclusion, premise_nums)
    cur_goals = [conclusion_goal]

    loop_count = 0 # Keep count to check against the loop limit
    goal_try_count = 0
    # The main loop: as long as the conclusion is there, and
    # we've not exceeded loop quota
    while conclusion_goal in cur_goals and loop_count <= loop_limit:
        loop_count += 1
        print('\nLoop #{}:'.format(loop_count))
        goal_try_count += 1
        
        # Shelving goal because we are stuck
        if goal_try_count >= goal_try_limit:
            print('Shelving the current goal because we are stuck')
            this_goal = cur_goals.pop()
            cur_goals.insert(0, this_goal)
            goal_try_count = 0

        # Check if we've already achieved the goal:
        if solved_goal(cur_goals[-1]):
            print('Goal achieved! Removing goal')
            cur_goals.pop()
            continue
        # Note: Do NOT pop the goal queue for the rest of the loop,
        # Because we do not know if the queue is empty
        # If you think you've achieved a goal, simply command 'continue'
        print('Current goal queue (right-most first): '+ str(cur_goals))

        # Goal-oriented approach first: for rules that has
        # loose requirements, which pollutes the proof lines

        # Conjunction: try and-introduction:
        if cur_goals[-1].form.cons == PlCons.CONJUNCTION:
            print('The goal is a conjunction: try and-introduction:')
            left = search_form(cur_goals[-1].form.left, cur_goals[-1].dep)
            right = search_form(cur_goals[-1].form.right, cur_goals[-1].dep)
            
            if left and right:
                add_line( make_line(and_intro(left[0], right[0])) )
            else:
                print('We don\'t have the components yet, find them')
                tmp = cur_goals[-1]
                add_goal(goal(tmp.form.left, cur_goals[-1].dep))
                add_goal(goal(tmp.form.right, cur_goals[-1].dep))

        # Conditional: use CP tactics
        elif cur_goals[-1].form.cons == PlCons.CONDITIONAL:
            print('The goal is a conditional:')
            ante = make_line(assume(cur_goals[-1].form.ante))
            add_line( ante )
            tmp = cur_goals[-1]
            conse = search_form(tmp.form.conse, tmp.dep)
            if conse:
                print('But we already possess the consequent even before the assumption, this is a trap, we must prove the conjunction of the consequent and the antecedent, detach the consequent, and then we will be done')
                conjunction = add_line( make_line(and_intro(ante, conse[0])) )
                new_conse = add_line( make_line(and_elim2(conjunction)) )
                add_line( make_line(cp(ante, new_conse)) )
                # And I believe we're done
                continue
            else:
                print('assume the antecedent and prove the consequent with dependency on both the goal\'s and the antecedent')
                add_goal(goal(tmp.form.conse, tmp.dep | ante.dep))

        # Biconditional: find the components
        elif cur_goals[-1].form.cons == PlCons.BICONDITIONAL:
            print('Biconditional: find the components')
            l, r = cur_goals[-1].form.left, cur_goals[-1].form.right
            lr = search_form(cond(l, r), cur_goals[-1].dep)
            rl = search_form(cond(r, l), cur_goals[-1].dep)
            if lr and rl:
                add_line( make_line(bicond_intro(lr[0], rl[0])) )
                continue
            else:
                # If we don't have the components yet, find them:
                print('We don\'t have the components yet, find them:')
                tmp = cur_goals[-1]
                add_goal(goal(cond(l, r), tmp.dep))
                add_goal(goal(cond(r, l), tmp.dep))

        # Find some conditional
        win_cond = [l for l in lines if l.form.cons == PlCons.CONDITIONAL and l.form.conse == cur_goals[-1].form and l.dep <= cur_goals[-1].dep]
        if win_cond:
            print('We have some conditional that can deduce the goal, try to prove the antecedents of those')
            for c in win_cond:
                add_goal(goal(c.form.ante, cur_goals[-1].dep))

        # If the goal is a Double Negation:
        if cur_goals[-1].form.cons == PlCons.NEGATION:
            if cur_goals[-1].form.form.cons == PlCons.NEGATION:
                print('Goal is a double negation')
                e = search_form(cur_goals[-1].form.form.form, cur_goals[-1].dep)
                if e:
                    print('Got it!')
                    add_line( make_line(dni(e[0])) )
                else:
                    print('Let\'s find its core')
                    add_goal( goal(cur_goals[-1].form.form.form, cur_goals[-1].dep) )

        #Then we switch to... guessing aimlessly (with restraint, of course)

        print('Loop through everything we have, and add more to our knowledge')
        for line in lines:
            # If the line contains a conjunction,
            # break it down
            # Try and-elim1:
            if and_elim1(line): add_line( make_line(and_elim1(line)) )
            # Try and-elim2:
            if and_elim2(line): add_line( make_line(and_elim2(line)) )
            # Try biconditional-elim:
            if bicond_elim(line): add_line( make_line(bicond_elim(line)) )
            # Try double negation elimination:
            if dne(line): add_line( make_line(dne(line)) )

            # If the line contains a conditional,
            # try to get the consequent
            if line.form.cons == PlCons.CONDITIONAL:
                # Just guess the antecedent, dude, it's still efficient
                for ante in lines:
                    if modus_ponens(line, ante):
                        add_line( make_line(modus_ponens(line, ante)) )

            # If the line depends on assumptions,
            # make a conditional statement:
            asps = line.dep - premise_nums
            # asps should now contains (potentially many) lines numbers
            # of the assumptions that this line depends on
            # so now we discharge them one
            for asp_num in asps:
                add_line( make_line(cp(lines[asp_num], line)) )

    solved = conclusion_goal not in cur_goals
    print('\n' + '-'*100)
    if solved:
        cleaned_proof = clean_proof(lines, conclusion_goal)
        print('\nSuccess! Here is the proof:')
        print(str_proof(cleaned_proof))
    else:
        print("Failed! Here's what I found")
        print(str_proof(lines))

    return cleaned_proof if solved else None

def goal(form, dep: FrozenSet):
    '''
    A goal is a formula plus a set of dependency lines
    This is just a conceptual data structure in proofs
    '''
    assert (form.type == MathType.PL_FORMULA)
    
    goal = MathObject()
    goal.type = 'goal'
    goal.form = form
    goal.dep = dep
    goal.text = 'goal({}, {})'.format(form.text, str(dep))
    return goal

def clean_proof(lines: List, conclusion_goal):
    '''
    Receive a proof, a conclusion and return a clean version of the proof
    '''
    def search_form(form, dep=None) -> List:
        '''
        Search in a list of lines that contains a particular formula
        and dependency, if dependency is None then anything goes
        '''
        result = []
        for line in lines:
            if line.form == form and (dep == None or line.dep <= dep):
                result.append(line)
        return result

    # Checking the input:
    assert(conclusion_goal.type == 'goal')
    
    # Check that the there is actually a line containing...
    # the conclusion with adequate dependency
    con_line = search_form(conclusion_goal.form, conclusion_goal.dep)
    assert(con_line)
    con_line = con_line[0] # There should only be one conclusion line, right?
    
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
