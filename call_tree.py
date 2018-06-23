from khoa_math import Mole
from pprint import pformat


class LogNode:
    def __init__(self, lw=False, prefix=''):
        self.lw, self.prefix = lw, prefix
        self.lines, self.choice, self.phase, self.children = [], 0, 0, []

    def log(self, line):
        """Add a new line"""
        self.lines.append('({}): {}'.format(self.prefix, line))

    def log_m(self, mole):
        """
        Add a molecule
        :param `lw`: light-weight logging, set True
        to disable pretty formatting
        """
        self.lines.append('({}):'.format(self.prefix))
        if self.lw:
            self.lines.extend([str(mole)])
        else:
            self.lines.extend(pformat(mole).split('\n'))

    def branch(self):
        """Return the a branch from this node"""
        res = LogNode(lw=self.lw, prefix=self.prefix + str(self.choice))
        self.choice+=1
        self.children.append(res)
        return res

    def sub(self):
        """I don't know what it does yet"""
        res = LogNode(lw=self.lw, prefix=self.prefix + chr(97+self.phase))
        self.phase += 1
        self.children.append(res)
        return res

def render_log(root: LogNode):
    res = '\n'.join(root.lines)
    for child in root.children:
        res += '\n' + render_log(child)
    return res


if __name__ == '__main__':
    root = LogNode(); root.log('Start')
    def a(orig):
        orig.log('do something')
        orig.log('Calling b'); b_branch = orig.sub(); b(b_branch)
        orig.log('Calling c'); c_branch = orig.branch(); c(c_branch)

    def b(orig):
        orig.log('b reporting for action')
        x = Mole(name = 'x'); y = Mole(name = 'y')
        orig.log('Here\'s a molecule inside a tree:'); orig.log_m(x)
        orig.log('and something under that')

    def c(orig):
        orig.log('This is c, I have nothing to say')

    a(root)
    print(render_log(root))
