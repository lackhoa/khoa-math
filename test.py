from khoa_math import *
from prep import *

from anytree import LevelOrderGroupIter

# Set up the environment
counter = 1  # How we get new ids
form0 = MathObj(id_ = '#0', propa_rules=[prep_propagate])  # The starting unknown
roots = [form0]  # All the possible roots
discarded = []  # All the inconsistent objects
completed = []  # All the completed objects
form0.kattach(None)  # form0 is root
type_ = MathObj(role='type', value={MathType.PL_FORMULA})
type_.kattach(form0)  # Attach the type to the form0

for dep in range(4):
    # Clean-up routine
    for root in roots:
        if root.is_inconsistent():
            roots.remove(root)
            discarded += [root]

    for root in roots:
        # Attach nodes from the queue
        for queue_item in root.queue:
            child, parent = queue_item
            if parent and parent.depth <= dep:  # must attach level-by-level, for safety
                child.kattach(parent)

        # Exploring the possibilities of the current level
        levels = [lvl for lvl in LevelOrderGroupIter(root)]
        if len(levels) <= dep: continue

        for node in levels[dep]:
            if node.value and len(node.value) > 1:  # If there are many values
                for v in (node.value - {KSet.UNKNOWN}):  # Explore possibility v
                    # Create an identical tree, change the id
                    root_clone = root.clone()
                    root_clone.id = '#{}'.format(counter)
                    roots.append(root_clone)
                    counter += 1
                    # Narrow down the possibility of the value to just v
                    possibility = MathObj(role=node.role, value={v})
                    possibility.kattach(root_clone)
                node.value = {KSet.UNKNOWN} if KSet.UNKNOWN in node.value else set()

rt = lambda t: print(RenderTree(t))
for root in roots: rt(root)
