from proof import *
from solver import *
import os
import readline
import re  # Regular expression

# This is a test file

print("Test #1:")
p, q, r, s = atom('P'), atom('Q'), atom('R'), atom('S')
np, nq, nr, ns = neg(p), neg(q), neg(r), neg(s)
pq, qp, qr, rq, pr, rs, rp = conj(p, q), conj(q, p), conj(q, r), conj(r, q), conj(p, r), conj(r, s), conj(r, p)
p2p, p2q, q2r, r2s, r2p, r2q, p2r, q2s, s2q, s2r, q2p, p2s, s2q = cond(p, p), cond(p, q), cond(q, r), cond(r, s), cond(r, p), cond(r, q), cond(p, r), cond(q, s), cond(s, q), cond(s, r), cond(q, p), cond(p, s), cond(s, q)
p3q, q3p, q3r, p3r = bicond(p, q), bicond(q, p), bicond(q, r), bicond(p, r)
pvq, qvp, pvr, rvs = disj(p, q), disj(q, p), disj(p,r), disj(r, s)

premises = [p2q, cond(p, nq)]
conclusion = np
l = []

# Premise introduction
for i in range(len(premises)):
    l.append(pre_intro(premises[i], i))


# The CLI:
choice = ''
while True:
    choice = input('PL>>> ')
    # Respond to user input
    if choice == 'a':
        # Add a line
        line = input('Enter line: ')
        # Processing the input line:
        line_pattern = re.compile(r'#(?P<line_number>[0-9]+)')
        for (pattern, replace) in [('mp', 'modus_ponens'),  # Modus Ponens shortcut
                ('mt', 'modus_tollens'),                    # Modus Tollens shortcut
                (r'\)$', ',' + str(len(l)) + ')'),           # automatically use the next line number
                (line_pattern, r'l[\g<line_number>]')]:     # '#<number>' returns l[number]

            line = re.sub(pattern, replace, line)
        print('Interpreted as: \'{}\''.format(line))

        try:
            if eval(line) is not None:
                l.append(eval(line))
                print(eval(line))
            else: print('You messed up!')
        except: print('That wasn\'t even coherent!')

    elif choice == 'p':
        # Clear screen
        os.system('clear')
        # View proof:
        print(str_lines(l))
        # View conclusion:
        print('Aim: {}'.format(str(conclusion)))

    elif choice == 'done':
        if proof(premises, conclusion, l):
            print('Well done! You can save your work if you want')
        else: print('We\'re not done yet!')

    elif choice == 's':
        # Write down the proof:
        try:
            file_name = input('Give me the file name: ')
            with open('proofs/{}'.format(file_name), 'w+') as file:
                file.write(pr.text)
            print('File written!')
        except: print('Failed!')

    elif choice == 'q':
        print('Good bye!')
        break
    else:
        print('I\'m sorry what did you say? Ca...catc...catch me outside?')


