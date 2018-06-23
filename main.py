from kenum import *
from misc import *
from khoa_math import *
from type_data import *
from rel import *
from call_tree import *

import anytree
import timeit
import sys, logging, traceback

# Handler that writes debugs to a file
debug_handler = logging.FileHandler(filename='logs/debug.log', mode='w+')
debug_handler.setFormatter(logging.Formatter('%(message)s'))
debug_handler.setLevel(logging.DEBUG)

# Handler that writes info messages or higher to the sys.stderr
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
console_handler.setLevel(logging.INFO)

# Configure the root logger
logging.basicConfig(handlers = [console_handler, debug_handler], level = logging.DEBUG)

def custom_traceback(exc, val, tb):
    print('\n'.join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def main_func():
    LW = False
    debug_root = LogNode(lw=LW); debug_root.log('Describing the program execution')
    setup_root = LogNode(lw=LW); setup_root.log('Describing the setup')

    info_root = LogNode(lw=False); info_root.log('The output:')
    
    p = Mole(_types=wr('WFF'), _cons=wr('ATOM'), _text=wr('P'))
    q = Mole(_types=wr('WFF'), _cons=wr('ATOM'), _text=wr('Q'))
    r = Mole(_types=wr('WFF'), _cons=wr('ATOM'), _text=wr('R'))
    pq = Mole(_types=wr('WFF'), _cons=wr('CONJUNCTION'), left_f=p, right_f=q)
    qr = Mole(_types=wr('WFF'), _cons=wr('CONJUNCTION'), left_f=q, right_f=r)
    pq_r = Mole(_types=wr('WFF'), _cons=wr('CONJUNCTION'), left_f=pq, right_f=r)

    setup_vars, new_setup_vars = [p, q, r, pq, qr, pq_r], []
    for i, sr in enumerate(setup_vars):
        debug_root.log('Current setup job: {}'.format(i))
        sr = list(kenum(root=sr, max_dep=10, orig=setup_root))[0]
        new_setup_vars.append(sr)
        info_root.log('{}. SETUP OUTPUT:'.format(i))
        info_root.log_m(sr)

    p, q, r, pq, qr, pq_r = new_setup_vars

    # Main roots
    and_intro_root = Mole(_types = wr('PROOF'),
                          dep    = wr(frozenset({p,q})),
                          formu  = pq)
    and_elim_root = Mole(_types = wr('PROOF'),  # Focus on this one
                         dep    = wr(frozenset({pq})),
                         formu  = p)
    both_root = Mole(_types = wr('PROOF'),
                     formu  = pq_r,
                     dep    = wr(frozenset({qr, p})))

    LEVEL_CAP = 4
    start_roots = [Mole(_types = wr('WFF_TEST')),
                   Mole(_types = wr('UNI')),
                   Mole(_types = wr('ISO_TEST')),
                   Mole(_types = wr('MULTI')),
                   and_intro_root,
                   and_elim_root,
                   both_root]
    start_time = timeit.default_timer()
    try:
        for i, start in enumerate(start_roots[5:6]):
            debug_root.log('Current main job: {}'.format(i))
            for j, t in enumerate(kenum(root=start, max_dep=LEVEL_CAP, orig=debug_root)):
                info_root.log('{}. RETURNED ({}):'.format(i, j))
                info_root.log_m(t)
    finally:
        # Write down logs even after failure
        stop_time = timeit.default_timer()
        logging.info("Program Executed in {} seconds".format(stop_time - start_time))
        logging.debug(render_log(debug_root))
        logging.info(render_log(info_root))

main_func()
