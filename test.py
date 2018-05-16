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
P2Q = cond(P, Q)
Q2R = cond(Q, R)
R2S = cond(R, S)
R2P = cond(R, P)
R2Q = cond(R, Q)

premises = [P2Q, R2P]
conclusion = R2Q

prove(premises, conclusion, loop_limit=30, len_limit=400)
