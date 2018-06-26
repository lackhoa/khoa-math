from kenum import *
from misc import *
from khoa_math import *
from type_data import *
from rel import *
from call_tree import *

import anytree
import timeit
import sys, logging, traceback


# Logger-handler pair that writes debugs to a file
debug_handler = logging.FileHandler(filename='logs/debug.log', mode='w+')
debug_handler.setFormatter(logging.Formatter('%(message)s'))
debug_logger = logging.getLogger('debug')
debug_logger.addHandler(debug_handler)

# Logger-Handler that writes setup logic to a separate file
setup_handler = logging.FileHandler(filename='logs/setup.log', mode='w+')
setup_handler.setFormatter(logging.Formatter('%(message)s'))
setup_logger = logging.getLogger('setup')
setup_logger.addHandler(setup_handler)

# Logger-Handler that writes info messages or higher to the sys.stderr
output_handler_csl = logging.StreamHandler()
output_handler_csl.setFormatter(logging.Formatter('%(message)s'))
output_handler_file = logging.FileHandler(filename='logs/output.log', mode='w+')
output_handler_file.setFormatter(logging.Formatter('%(message)s'))
info_logger = logging.getLogger('output')
info_logger.addHandler(output_handler_csl)
info_logger.addHandler(output_handler_file)

# Adding on top of that my logging layer
setup_node  = LogNode(setup_logger)
debug_node  = LogNode(debug_logger)
info_node   = LogNode(info_logger)

# Switches to turn off the nodes
setup_node.on = False
debug_node.on = False


def custom_traceback(exc, val, tb):
    print('\n'.join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def main_func():
    p = Mole(_types=wr('WFF'), _cons=wr('ATOM'), _text=wr('P'))
    q = Mole(_types=wr('WFF'), _cons=wr('ATOM'), _text=wr('Q'))
    r = Mole(_types=wr('WFF'), _cons=wr('ATOM'), _text=wr('R'))
    pq = Mole(_types=wr('WFF'), _cons=wr('CONJUNCTION'), left_f=p, right_f=q)
    qr = Mole(_types=wr('WFF'), _cons=wr('CONJUNCTION'), left_f=q, right_f=r)
    pq_r = Mole(_types=wr('WFF'), _cons=wr('CONJUNCTION'), left_f=pq, right_f=r)

    setup_vars, new_setup_vars = [p, q, r, pq, qr, pq_r], []
    for i, sr in enumerate(setup_vars):
        sr = list(kenum(node=sr, max_dep=10, orig=setup_node))[0]
        new_setup_vars.append(sr)
        setup_node.log('{}. SETUP OUTPUT:'.format(i))
        setup_node.log_m(sr)

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

    DEP_CAP = 4 
    start_roots = [Mole(_types = wr('WFF_TEST')),  # Danger!
                   Mole(_types = wr('UNI')),
                   Mole(_types = wr('ISO_TEST')),
                   Mole(_types = wr('MULTI')),
                   and_intro_root,
                   and_elim_root,
                   both_root]
    start_time = timeit.default_timer()
    for i, start in enumerate(start_roots[1:6]):
        for j, t in enumerate(
                kenum(node=start, max_dep=DEP_CAP, orig=debug_node)):
            info_node.log('{}. RETURNED ({}):'.format(i, j))
            info_node.log_m(t)
    stop_time = timeit.default_timer()
    info_node.log("Program Executed in {} seconds".format(stop_time - start_time))

main_func()
