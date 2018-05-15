from proof import *
from solver import *

P = atom('P')
Q = atom('Q')
R = atom('R')
PQ = conj(P, Q)
QR = conj(Q, R)
conclusion = conj(PQ, R)

prove([pre_intro(0, QR), pre_intro(1, P)], conclusion, loop_limit=25, len_limit=20)
