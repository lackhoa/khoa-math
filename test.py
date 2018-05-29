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
for dep in range(6):
    # Clean-up routine
    for root in roots:
        if root.is_inconsistent():
            roots.remove(root)
            discarded += [root]

    # Then we do two jobs for each root
    roots_extend = []  # This variable is here for modifying roots after the loop
    for root in roots:
        # Job 1: Attach nodes from the queue:
        index_to_delete = []
        for i in range(len(root.queue)):
            node, ref, path = root.queue[i]

            # Path processing:
            path = path.split('/')
            parent = ref
            # Go down each level one by one UNIX style:
            for n in path:
                if n == '': continue
                else:
                    parent = parent.get(n)
                    if not parent: break

            if parent and parent.depth <= dep:  # must attach level-by-level, for safety
                MathObj.kattach(node, parent)
                index_to_delete += [i]

        for j in sorted(index_to_delete, reverse=True):  # Yeah, gotta reverse the list
            root.queue.pop(j)  # We're done with it, so we pop it!

        # Job 2: Explore the possibilities of the current level:
        levels = [lvl for lvl in LevelOrderGroupIter(root)]
        if len(levels) <= dep: continue  # Not enough levels in this tree

        for node in levels[dep]:
            if node.value and len(node.value) > 1:  # If there are many values
                for v in (node.value - {KSet.UNKNOWN}):  # Explore possibility v
                    # Create an identical tree, change the id
                    root_clone = root.clone()
                    root_clone.id = '#{}'.format(counter)
                    roots_extend.append(root_clone)
                    counter += 1
                    # Narrow down the possibility of the value to just v
                    possibility = MathObj(role=node.role, value={v})
                    MathObj.kattach(possibility, root_clone)

                # Clean up the value from the original tree
                node.clear_val()

    roots.extend(roots_extend)

# Printing out the resulting lists:
rt = lambda t: print(RenderTree(t))
print('These are the active roots:')
for r in roots: rt(r)
print('\nThese are the discarded:')
for r in discarded: rt(r)
print('\nThese are the completed:')
for r in completed: rt(r)

