from proof import *
from solver import *

print("Test #1:")
P = atom('P')
Q = atom('Q')
R = atom('R')
S = atom('S')
PQ = conj(P, Q)
QP = conj(Q, P)
QR = conj(Q, R)
PR = conj(P, R)
RS = conj(R, S)

premises = [pre_intro(0, PQ)]
conclusion = QP

prove(premises, conclusion, loop_limit=25, len_limit=40)
