from prep import *
from proof import *
from inference_rules import *
from typing import Callable

# This file provides my mechanism to form proofs

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

    def add_goal(goal, reason: str = '') -> bool:
        # Safely add a goal, returns True if successful
        # (does not check the length of the queue)
        # Reason: the purpoes of this action

        nonlocal cur_goals # use the common goal queue, not create another
        assert(goal.type == MathType.PL_CONNECTION)

        tried = lambda: goal in tried_goals
        trying = lambda: goal in cur_goals
        succeeded = solved_goal(goal)

        if (not tried()) and (not trying()) and (not succeeded):
            cur_goals.append(goal)
            print('Added goal: ' + str(goal))
            print('Reason: {}'.format(reason))
            return goal

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

    # This is a function to provide an id for new lines (increments by one each time)
    get_id = lambda: len(lines)

    def add_line(line, desc:str = '') -> bool:
        # Safely add a line to the proof
        # returns the line if succeeded, None if not
        # Description explains what you did and why you did it
        assert(line.type == MathType.PL_PROOF_LINE)

        # Only reject if there's a line with the same text and dependency (to combat under-dependency)
        # Furthremore, don't assume the same thing twice
        b1 = not [l for l in lines if l.form == line.form and (l.dep == line.dep or l.rule_anno.symbol == line.rule_anno.symbol == 'A')]
        length_check = len(line.form.text) <= len_limit
        if b1 and length_check:
            print(desc)
            print(line)
            lines.append(line)
            return line
        return None

    def solved_goal(goal):
        # See if we've already achieved a goal:
        return True if search_form(goal.form, goal.dep) else False

    print_goal = lambda: print('Current goal queue (right-most first): '+ str(cur_goals))

    # Enough wait, the proofwork starts here:

    # Add premises, and record the line numbers for future use:
    premise_nums = set()
    print('Introducing premises')
    for premise in premises:
        premise_line = pre_intro(premise, get_id())
        add_line( premise_line )
        premise_nums.add(premise_line.id_)

    premise_nums = frozenset(premise_nums) # Lock the premises for good measure

    # The conclusion depends only on the premises
    conclusion_goal = goal(conclusion, premise_nums)
    cur_goals = [conclusion_goal]

    loop_count = 0 # Keep count to check against the loop limit
    goal_try_count = 0
    # The main loop: we'll keep going as long as the conclusion is there, and
    # we've not exceeded loop quota
    # I'll try to do one goal per loop, to show clearly
    # which goal we're focusing on
    while conclusion_goal in cur_goals and loop_count <= loop_limit:
        # Part 1: Goal management
        loop_count += 1
        print('\nLoop #{}:'.format(loop_count))
        goal_try_count += 1

        # When the goal queue gets too big, just go to sleep,
        # forget everything, and try again from the start:
        if len(cur_goals) > goal_queue_limit:
            print('Too many goals! Cleaning up the goal queue!')
            cur_goals = [conclusion_goal]

        # Check if we've already achieved the goal:
        if solved_goal(cur_goals[-1]):
            print('Goal achieved! Removing goal')
            cur_goals.pop()
            continue

        # Shelving goal if we're stuck
        if goal_try_count >= goal_try_limit:
            this_goal = cur_goals.pop()
            cur_goals.insert(0, this_goal)
            goal_try_count = 0

        # Note: Do NOT pop the goal queue for the rest of the loop,
        # Because we do not know if the queue is empty
        # and to make it clear what we're doing
        # If you think you've achieved a goal, command 'continue'
        print('We are currently focusing on: {}'.format(str(cur_goals[-1])))

        # ---------------------------------------------------------
        # Part 2: Goal-oriented approach
        # for rules that has loose requirements
        # which pollutes the proof lines
        # this part can conclude goals

        # Conjunction: try and-introduction:
        if cur_goals[-1].form.cons == PlCons.CONJUNCTION:
            print('The goal is a conjunction: try and-introduction:')
            left = search_form(cur_goals[-1].form.left, cur_goals[-1].dep)
            right = search_form(cur_goals[-1].form.right, cur_goals[-1].dep)

            if left and right:
                add_line( and_intro(left[0], right[0], get_id()), 'And-introduction' )
            else:
                print('We don\'t have the components yet, find them')
                tmp = cur_goals[-1]
                add_goal(goal(tmp.form.left, cur_goals[-1].dep), reason='The left conjunct')
                add_goal(goal(tmp.form.right, cur_goals[-1].dep), reason='The right conjunct')

        # Conditional: use CP tactics
        elif cur_goals[-1].form.cons == PlCons.CONDITIONAL:
            print('The goal is a conditional:')
            ante = assume(cur_goals[-1].form.ante, get_id())
            add_line( ante, 'Assuming for CP' )
            tmp = cur_goals[-1]
            conse = search_form(tmp.form.conse, tmp.dep)
            if conse:
                print('But we already possess the consequent even before the assumption, this is a trap, we must prove the conjunction of the consequent and the antecedent, detach the consequent, and then we will be done')
                conjunction = add_line( and_intro(ante, conse[0], get_id()), 'Step one' )
                new_conse = add_line( and_elim2(conjunction, get_id()) ,'Step two' )
                add_line( cp(ante, new_conse, get_id()), 'Step three: And I believe we\'re done!' )
                continue
            else:
                print('assume the antecedent and prove the consequent with dependency on both the goal\'s and the antecedent')
                add_goal(goal(tmp.form.conse, tmp.dep | ante.dep), reason='Assuming for CP')

        # Biconditional: find the components
        elif cur_goals[-1].form.cons == PlCons.BICONDITIONAL:
            print('Biconditional: find the components')
            l, r = cur_goals[-1].form.left, cur_goals[-1].form.right
            lr = search_form(cond(l, r), cur_goals[-1].dep)
            rl = search_form(cond(r, l), cur_goals[-1].dep)
            if lr and rl:
                add_line( bicond_intro(lr[0], rl[0], get_id()), '<->-intro' )
                continue
            else:
                # If we don't have the components yet, find them:
                print('We don\'t have the components yet, find them:')
                tmp = cur_goals[-1]
                add_goal(goal(cond(l, r), tmp.dep), reason='From left to rigth')
                add_goal(goal(cond(r, l), tmp.dep), reason='From right to left')

        # Find some conditional
        win_cond = [l for l in lines if l.form.cons == PlCons.CONDITIONAL and l.form.conse == cur_goals[-1].form and l.dep <= cur_goals[-1].dep]
        if win_cond:
            print('We have some conditional that can deduce the goal, try to prove the antecedents of those')
            for c in win_cond:
                add_goal(goal(c.form.ante, cur_goals[-1].dep), reason='There is a conditional to get us from this to the goal')

        # If the goal is a Double Negation:
        if cur_goals[-1].form.cons == PlCons.NEGATION:
            if cur_goals[-1].form.form.cons == PlCons.NEGATION:
                print('Goal is a double negation')
                e = search_form(cur_goals[-1].form.form.form, cur_goals[-1].dep)
                if e:
                    add_line( dni(e[0], get_id()), 'Got the core of the double negation' )
                    continue
                else:
                    print('We can\'t find the core of the DN')
                    add_goal(goal(cur_goals[-1].form.form.form, cur_goals[-1].dep), reason='This is the core of the DN')

        # A negation can also mean a Modus Tollens opportunity:
        if cur_goals[-1].form.cons == PlCons.NEGATION:
            conds = [l for l in lines if l.form.cons == PlCons.CONDITIONAL and l.form.ante == cur_goals[-1].form.form]
            for cond_ in conds:
                add_goal( goal(neg(cond_.form.conse), cur_goals[-1].dep), reason='To use Modus Tollens' )
        else:
        # But Modus Tollens can also produce positive sentences
            conds = [l for l in lines if l.form.cons == PlCons.CONDITIONAL and l.form.ante == neg(cur_goals[-1].form)]
            for cond_ in conds:
                add_goal( goal(neg(cond_.form.conse), cur_goals[-1].dep), reason='To use Modus Tollens' )

        # ---------------------------------------------------------
        # Part 3: Try to create more lines
        # (Using rules that have strict requirements)
        # So we don't loop too much
        # This part does not conclude anything

        # Loop through everything we have, and add more to our knowledge
        for line in lines:
            # If the line contains a conjunction,
            # break it down
            # Try and-elim1:
            if and_elim1(line, get_id()): add_line(and_elim1(line, get_id()), '&-elimination on the left' )
            # Try and-elim2:
            if and_elim2(line, get_id()): add_line(and_elim2(line, get_id()), '&-elimination on the right' )
            # Try biconditional-elim:
            if bicond_elim(line, get_id()): add_line( bicond_elim(line, get_id()), '<-> elimination' )
            # Try double negation elimination:
            if dne(line, get_id()): add_line( dne(line, get_id()), 'Double negation elimination' )

            # If the line contains a conditional,
            # try to get the consequent
            if line.form.cons == PlCons.CONDITIONAL:
                # Just guess the antecedent, dude, it's still efficient
                for ante in lines:
                    if modus_ponens(line, ante, get_id()):
                        add_line( modus_ponens(line, ante, get_id()), 'Did some Modus Ponens!' )
                        break
                else: add_goal( goal(line.form.ante, cur_goals[-1].dep), 'Trying to use Modus Ponens' )
                    # Or try to get the negation of the antecedent
                for neg_conse in lines:
                    if modus_tollens(line, neg_conse, get_id()):
                        add_line( modus_tollens(line, neg_conse, get_id()), 'Did some Modus Tollens!' )
                        break
                else:
                    add_goal( goal(neg(line.form.conse), cur_goals[-1].dep), 'Trying to use Modus Tollens' )


            # If the line depends on assumptions,
            # make a conditional statement:
            asps = line.dep - premise_nums
            # asps should now contains (potentially many) lines numbers
            # of the assumptions that this line depends on
            # so now we discharge them one
            for asp_num in asps:
                add_line( cp(lines[asp_num], line, get_id()), 'Did some conditional proof!' )

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
    assert(conclusion_goal.type == MathType.PL_CONNECTION)

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
    relevant_line_num.add(con_line.id_)
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
