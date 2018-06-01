from khoa_math import *
from wff import *

import anytree
from anytree import LevelOrderGroupIter, PreOrderIter
from copy import deepcopy, copy
import itertools


def custom_rules(child, parent):
    """
    Some new rules for this program.
    """
    new_nodes = []
    role = child['role']
    val = child['value']

    if role == 'type':
        if val == {MathType.PL_FORMULA}:
            # Limit wff constructors:
            new_nodes += [dict(role='cons',
                            value={PlCons.ATOM, PlCons.NEGATION, PlCons.CONJUNCTION},
                            path='')]

    if role == 'cons':
        if val == {PlCons.ATOM}:
            # Limit atoms' text
            new_nodes += [dict(role='text', value={'P', 'Q'}, path='')]

    return new_nodes


# Set up the environment
counter = 1  # How we get new names
form0 = MathObj(name = '#0', value = None)  # The starting unknown formula
MathObj.propa_rules += [wff_rules, custom_rules]  # These are the rules we're using today
active_roots = [form0]  # Store the active roots
inconsistent = []  # Store the inconsistent roots
completed = []  # Store the completed roots
grounded = []  # Store the grounded roots
# Attach the type to the form0
MathObj.kattach(dict(role= 'type', value={MathType.PL_FORMULA}), form0)


# We proceed level-by-level, as indexed by 'dep'
# We loop the last level until there is no more active roots remaining
LEVEL_CAP = 3
while True:
    # Exit if there is any active root:
    if not active_roots: break

    # Then we do two jobs for each root
    # Job 1 (Exploring): Attach nodes from the queue:
    for root in copy(active_roots):
        for q in copy(root.queue):
            # Path resolving:
            parent = MathObj.path_resolve(q['ref'], q['path'])

            # Beware: the next line assumes that `parent` already exists,
            # from the way we append and iterate the queue
            if parent.depth <= LEVEL_CAP - 1:
                MathObj.kattach(dict(role=q['role'], value=q['value']), parent)
            # Remove queue item regardless of parent's depth
            # So that oversized trees can become 'complete' in a sense that there's
            # nothing else to expand on it
            root.queue.remove(q)

        # Job 2 (Expanding): expand the possible values:
        all_nodes = [node for node in PreOrderIter(root)]
        node_index = 0  # This value will be "preserved" when cloning
        for node in all_nodes:
            if node.value and len(node.value) > 1:  # If there are multiple possible values
                for v in (node.value - {KSet.UNKNOWN}):  # Loop through each
                    # Create an identical tree, change the name
                    root_clone = root.clone()
                    root_clone.name = '#{}'.format(counter)
                    active_roots.append(root_clone)
                    counter += 1

                    # The new node has value 'v':
                    new_node = dict(role=node.role, value={v})
                    # Iterate over the cloned tree to get the corresponding parent's location:
                    all_nodes_clone = [node_clone for node_clone in PreOrderIter(root_clone)]
                    node_clone = all_nodes_clone[node_index]
                    MathObj.kattach(new_node, node_clone.parent)

                # Clean up the value from the original tree
                node.clear_val()
            node_index += 1


    # Clean-up routine afterwards
    for root in copy(active_roots):
        # Find inconsistent trees
        if root.is_inconsistent():
            active_roots.remove(root)
            inconsistent += [root]

        # Find grounded trees
        elif root.is_grounded():
            active_roots.remove(root)
            grounded += [root]

        # Find completed trees
        elif root.is_complete():
            active_roots.remove(root)
            completed += [root]




# Printing out the resulting lists:
rt = lambda t, s=anytree.ContStyle:\
        print(str(RenderTree(t, style=s)) + '\n')

# print('These are the active roots:')
# for r in active_roots: rt(r)

# print('\nThese are the inconsistent:')
# for r in inconsistent: rt(r)

# print('\nThese are the completed roots:')
# for r in completed: rt(r, anytree.DoubleStyle)

print('\nThese are the grounded roots:')
for r in grounded: rt(r, anytree.DoubleStyle)
