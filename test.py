from khoa_math import *
from wff import *

from anytree import LevelOrderGroupIter

# Set up the environment
counter = 1  # How we get new ids
form0 = MathObj(id_ = '#0')  # The starting unknown
MathObj.propa_rules += [wff_rules]
roots = [form0]  # All the possible roots
discarded = []  # All the inconsistent objects
completed = []  # All the completed objects
type_ = MathObj(role='type', value={MathType.PL_FORMULA})
MathObj.kattach(type_, form0)  # Attach the type to the form0

# We iterate level-by-level, indicated by 'dep'
for dep in range(4):
    # Clean-up routine
    for root in roots:
        if root.is_inconsistent():
            roots.remove(root)
            discarded += [root]

    # Then we do two jobs for each root
    for root in roots:
        # Job 1: Attach nodes from the queue:
        for i in range(len(root.queue)):
            queue_item = root.queue[i]
            child, parent = queue_item
            if parent and parent.depth <= dep:  # must attach level-by-level, for safety
                MathObj.kattach(child, parent)
                root.queue.pop(i)

        # Job 2: Explore the possibilities of the current level:
        levels = [lvl for lvl in LevelOrderGroupIter(root)]
        if len(levels) <= dep: continue  # Not enough levels in this tree

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
                    MathObj.kattach(possibility, root_clone)

                # Clean up the value from the original tree (this is quite dangerous)
                node.clear_val()

# Printing out the resulting lists:
rt = lambda t: print(RenderTree(t))
print('This is roots:')
for r in roots: rt(r)
print('This is discarded:')
for r in discarded: rt(r)
print('This is completed:')
for r in completed: rt(r)

