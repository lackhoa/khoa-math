from khoa_math import Mole, only
from pprint import pformat
import logging


class LogNode:
    def __init__(self, logger, prefix=''):
        self.prefix, self.logger = prefix, logger
        self.choice, self.phase = 0, 0
        self.on = True

    def log(self, msg, level=50):
        if self.on:
            msg = '[{}]: {}'.format(self.prefix, msg)
            self.logger.log(msg=msg, level=level)

    def log_m(self, mole, level=50):
        """
        Log a molecule
        """
        # If the switch is off, don't let anything run
        if self.on:
            msg = '{}\n'.format(str(mole))
            self.logger.log(msg=msg, level=level)

    def branch(self):
        """Return the a branch from this node"""
        new_prefix = self.prefix + str(self.choice)
        res = LogNode(prefix=new_prefix, logger=self.logger)
        res.on = self.on
        self.choice += 1
        return res

    def sub(self):
        """Return a subprocess log"""
        new_prefix = self.prefix + chr(97+self.phase)
        res = LogNode(prefix=new_prefix, logger=self.logger)
        res.on = self.on
        return res


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    root = LogNode(logger=logging.getLogger())
    root.log('Start')
    def a(orig):
        orig.log('do something', level=logging.INFO)
        orig.log('Calling b'); b_branch = orig.sub(); b(b_branch)
        orig.log('Calling c'); c_branch = orig.branch(); c(c_branch)

    def b(orig):
        orig.log('b reporting for action', level=logging.INFO)
        x = Mole(name = 'x'); y = Mole(name = 'y')
        orig.log('Here\'s a molecule inside a tree:'); orig.log_m(x)
        orig.log('and something under that')

    def c(orig):
        orig.log('This is c, I have nothing to say', level=logging.INFO)

    a(root)
