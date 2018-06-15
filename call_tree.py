from anytree import *


class LogNode(NodeMixin):
    def __init__(self, txt: str, parent=None, tree=None):
        self.parent = parent
        self.txt = str(txt)
        self.tree = tree

    def __repr__(self):
        return self.txt

    @property
    def name(self):
        return self.txt

    def log(self, txt, tree=None):
        """Add a new log node to `self`"""
        child = LogNode(txt = txt, tree = tree)
        child.parent = self

    def branch(self, branch_txt, branch_tree=None):
        """Return the a child node with `branch_name`"""
        return LogNode(txt = branch_txt, tree = branch_tree, parent = self)


def render_log(root: LogNode, main_style=ContStyle, sub_style=DoubleStyle):
    lines = []
    for pre, fill, node in RenderTree(root, style=main_style):
        lines.append("%s%s" % (pre, node.txt))
        if node.tree is not None:
            for pre_, fill_, node_ in RenderTree(node.tree, style=sub_style):
                lines.append("%s%s%s" % (fill, pre_, node_))
    return '\n'.join(lines)


if __name__ == '__main__':
    root = LogNode('Start')
    def a(orig):
        orig.log('do something')
        b_branch = orig.branch('Call b')
        b(b_branch)

    def b(orig):
        x = LogNode('x'); y = LogNode('y', parent=x)
        branch = orig.branch('Here\'s a tree inside a tree:', x)
        branch.log(LogNode('and something under that'))

    a(root)
    print(render_log(root))
