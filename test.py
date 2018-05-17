from proof import *
from solver import *

print("Test #1:")
p, q, r, s = atom('P'), atom('Q'), atom('R'), atom('S')
pq, qp, qr, rq, pr, rs, rp = conj(p, q), conj(q, p), conj(q, r), conj(r, q), conj(p, r), conj(r, s), conj(r, p)
p2p, p2q, q2r, r2s, r2p, r2q, p2r, q2s, s2q, s2r, q2p = cond(p, p), cond(p, q), cond(q, r), cond(r, s), cond(r, p), cond(r, q), cond(p, r), cond(q, s), cond(s, q), cond(s, r), cond(q, p)
p3q, q3p, q3r, p3r = bicond(p, q), bicond(q, p), bicond(q, r), bicond(p, r)

premises = [p3q, q3r]
conclusion = p3r

prove(premises, conclusion, loop_limit=50, goal_try_limit = 2, len_limit=40)
