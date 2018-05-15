from proof import *
from solver import *

print("Test #1:")
P = atom('P')
Q = atom('Q')
R = atom('R')
S = atom('S')
PQ = conj(P, Q)
QR = conj(Q, R)
PR = conj(P, R)
RS = conj(R, S)

premises = [pre_intro(0, QR), pre_intro(1, P)]
conclusion = conj(PQ, R)

prove(premises, conclusion, loop_limit=25, len_limit=40)