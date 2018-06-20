from kenum import *
from kset import *
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
    p = Mole(type_='WFF', con='ATOM', _text=ks('P'))
    q = Mole(type_='WFF', con='ATOM', _text=ks('Q'))
    and_intro_root = Mole(type_='PROOF', dep=KSet(frozenset({p, q})))

    LEVEL_CAP = 3
    start_roots = [Mole(type_ = 'WFF_TEST'),]
                   # Mole(type_ = 'UNI'),
                   # Mole(type_ = 'PROOF_TEST'),
                   # Mole(type_ = 'ISO_TEST'),
                   # and_intro_root]
    debug_root = LogNode(['Start Debug'])  # For describing the program execution
    info_root = LogNode(['Start Info'])  # For output
    start_time = timeit.default_timer()
    try:
        for i, start in enumerate(start_roots[:]):
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
