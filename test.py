from proof import *
from solver import *

print("Test #1:")
P = atom('knife')
Q = atom('PP gud')
R = atom('CM kill')
S = atom('MS kitchen')
PQ = conj(P, Q)
QP = conj(Q, P)
QR = conj(Q, R)
PR = conj(P, R)
RS = conj(R, S)
P2Q = cond(P, Q)
Q2R = cond(Q, R)
R2S = cond(R, S)

premises = [P, P2Q, cond(P, Q2R), R2S]
conclusion = conj(PQ, RS)

prove(premises, conclusion, loop_limit=30, len_limit=400)
