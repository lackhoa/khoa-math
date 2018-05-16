from proof import *
from solver import *

print("Test #1:")
P, Q, R, S = atom('P'), atom('Q'), atom('R'), atom('S')
PQ, QP, QR, RQ, PR, RS, RP = conj(P, Q), conj(Q, P), conj(Q, R), conj(R, Q), conj(P, R), conj(R, S), conj(R, P)
P2Q, Q2R, R2S, R2P, R2Q, P2R, Q2S, S2Q, S2R = cond(P, Q), cond(Q, R), cond(R, S), cond(R, P), cond(R, Q), cond(P, R), cond(Q, S), cond(S, Q), cond(S, R)

premises = [P2Q]
conclusion = cond(cond(RQ, S), cond(RP, S))

prove(premises, conclusion, loop_limit=100, goal_try_limit = 1, len_limit=40)
