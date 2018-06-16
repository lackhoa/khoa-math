from anytree import *


class LogNode(NodeMixin):
    def __init__(self, lines=[], parent=None):
        self.lines, self.parent = lines, parent

    def log(self, line):
        """Add a new line"""
        self.lines.append(line)

    def log_t(self, tree, style=DoubleStyle):
        """Add a tree"""
        for pre, fill, node in RenderTree(tree, style=style):
            self.lines.append("%s%s" % (pre, node))

    def branch(self, lines=[]):
        """Return the a child node with `branch_name`"""
        return LogNode(lines=lines, parent=self)


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
        x = Node('x'); y = Node('y', parent=x)
        branch = orig.branch(['Here\'s a tree inside a tree:'])
        branch.log_t(x)
        branch.log('and something under that')

    a(root)
    print(render_log(root))