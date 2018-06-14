from anytree import *


class LogNode(NodeMixin):
    def __init__(self, txt: str, parent=None):
        self.parent = parent
        self.txt = str(txt)

    def __repr__(self):
        return self.txt

    @property
    def name(self):
        return self.txt

    def log(self, line):
        """Add a new line to `self`"""
        child = LogNode(txt = line)
        child.parent = self

    def log_rt(self, intro, tree, style='DoubleStyle'):
        START_DELIM = ''
        END_DELIM = ''
        lines = [intro, START_DELIM, str(RenderTree(tree, DoubleStyle)), END_DELIM]
        self.log('\n'.join(lines))

    def call(self, call_txt):
        """Return the node with `call_name`"""
        return LogNode(txt = call_txt, parent = self)


if __name__ == '__main__':
    root = LogNode('Start')
    def a(orig):
        orig.log('do something')
        b_call = orig.call('Call b')
        b(b_call)

    def b(orig):
        x = Node('x'); y = Node('y', parent=x)
        orig.log_rt('Here\'s a tree inside a tree:', x)

    a(root)
    print(RenderTree(root))
