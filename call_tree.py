from anytree import *
from khoa_math import Mole
from pprint import pformat


class LogNode(NodeMixin):
    def __init__(self, lines=[], lw=False, parent=None):
        self.lines, self.lw, self.parent = lines, lw, parent

    def log(self, line):
        """Add a new line"""
        self.lines.append(line)

    def log_m(self, mole):
        """
        Add a molecule
        :param `lw`: light-weight logging, set True
        to disable pretty formatting
        """
        if self.lw:
            self.lines.extend([str(mole)] + [''])
        else:
            self.lines.extend(pformat(mole).split('\n') + [''])

    def branch(self, lines=[]):
        """Return the a branch from this node"""
        return LogNode(lines=lines, lw=self.lw, parent=self)


def render_log(root: LogNode, main_style=ContStyle, sub_style=DoubleStyle):
    lines = []
    for pre, fill, node in RenderTree(root):
        lines.append("%s%s" % (pre, node.lines[0]))
        for line in node.lines[1:]:
            lines.append("%s%s" % (fill, line))
    return '\n'.join(lines)


if __name__ == '__main__':
    root = LogNode(['Start'])
    def a(orig):
        orig.log('do something')
        b_branch = orig.branch(['Call b'])
        b(b_branch)

    def b(orig):
        x = Mole(name = 'x'); y = Mole(name = 'y')
        branch = orig.branch(['Here\'s a molecule inside a tree:'])
        branch.log_m(x)
        branch.log('and something under that')

    a(root)
    print(render_log(root))
