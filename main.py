from kenum import *
from misc import *
from khoa_math import *
from type_data import *
from rel import *
from call_tree import *

import anytree
import timeit
import sys, logging, traceback


def custom_traceback(exc, val, tb):
    print('\n'.join(traceback.format_exception(exc, val, tb)), file=sys.stderr)
sys.excepthook = custom_traceback


def main_func():
    p = Mole(_types=wr('WFF'), _cons=wr('ATOM'), _text=wr('P'))
    q = Mole(_types=wr('WFF'), _cons=wr('ATOM'), _text=wr('Q'))
    and_intro_root = Mole(_types = wr('PROOF'), dep = wr(frozenset({p, q})))

    LEVEL_CAP = 3
    start_roots = [Mole(_types = wr('WFF_TEST')),
                   Mole(_types = wr('UNI')),
                   Mole(_types = wr('ISO_TEST')),
                   Mole(_types = wr('PROOF_TEST')),
                   Mole(_types = wr('MULTI')),
                   and_intro_root,]
    debug_root = LogNode(['Start Debug'])  # For describing the program execution
    info_root = LogNode(['Start Info'])  # For output
    start_time = timeit.default_timer()
    try:
        for i, start in enumerate(start_roots[:]):
            for j, t in enumerate(kenum(root=start, max_dep=LEVEL_CAP, orig=debug_root)):
                info_root.log('{}. RETURNED ({}):'.format(i, j))
                info_root.log_m(t, lw=False)
    finally:
        # Write down logs even after failure
        stop_time = timeit.default_timer()
        logging.info("Program Executed in {} seconds".format(stop_time - start_time))
        logging.debug(render_log(debug_root))
        logging.info(render_log(info_root))

main_func()
