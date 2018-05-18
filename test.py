from proof import *
from solver import *

# This is a test file

print("Test #1:")
p, q, r, s = atom('P'), atom('Q'), atom('R'), atom('S')
np, nq, nr, ns = neg(p), neg(q), neg(r), neg(s)
pq, qp, qr, rq, pr, rs, rp = conj(p, q), conj(q, p), conj(q, r), conj(r, q), conj(p, r), conj(r, s), conj(r, p)
p2p, p2q, q2r, r2s, r2p, r2q, p2r, q2s, s2q, s2r, q2p = cond(p, p), cond(p, q), cond(q, r), cond(r, s), cond(r, p), cond(r, q), cond(p, r), cond(q, s), cond(s, q), cond(s, r), cond(q, p)
p3q, q3p, q3r, p3r = bicond(p, q), bicond(q, p), bicond(q, r), bicond(p, r)

premises = [cond(pq, nr)]
conclusion = cond(r, cond(p, nq))

prove(premises, conclusion, loop_limit=20, goal_try_limit = 3, len_limit=30, goal_queue_limit=1000)
