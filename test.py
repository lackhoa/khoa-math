from khoa_math import *
from wff import *

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

    if role == 'cons':
        if val == {PlCons.ATOM}:
            # Atoms have texts, and that text should be 'P'
            new_nodes += [dict(role='text', value={'P'}, path='')]

    return new_nodes


# Set up the environment
counter = 1  # How we get new ids
form0 = MathObj(id_ = '#0')  # The starting unknown formula
MathObj.propa_rules += [wff_rules, custom_rules]  # These are the rules we're using today
active_roots = [form0]  # Store the active roots
inconsistent = []  # Store the inconsistent objects
completed = []  # Store the completed objects
# Attach the type to the form0
MathObj.kattach(dict(role= 'type', value={MathType.PL_FORMULA}), form0)


# We proceed level-by-level, as indexed by 'dep'
# We loop the last level until there is no more active roots remaining
LEVEL_CAP = 5
while True:
    # Exit if there is any active root:
    if not active_roots: break

    # Then we do two jobs for each root
    # Job 1 (Exploring): Attach nodes from the queue:
    for root in copy(active_roots):
        for q in copy(root.queue):
            # Path resolving:
            parent = MathObj.path_resolve(q['ref'], q['path'])

            if parent.depth <= LEVEL_CAP - 1:
                MathObj.kattach(dict(role=q['role'], value=q['value']), parent)
            root.queue.remove(q)  # Remove regardless of parent's depth


        # Job 2 (Expanding): expand the possible values:
        all_nodes = [node for node in PreOrderIter(root)]
        node_index = 0  # This value will be "preserved" when cloning
        for node in all_nodes:
            if node.value and len(node.value) > 1:  # If there are multiple possible values
                for v in (node.value - {KSet.UNKNOWN}):  # Expand them all
                    # Create an identical tree, change the id
                    root_clone = root.clone()
                    root_clone.id = '#{}'.format(counter)
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

        # Find completed trees
        elif root.is_complete():
            active_roots.remove(root)
            completed += [root]




# Printing out the resulting lists:
rt = lambda t: print(str(RenderTree(t)) + '\n')
print('These are the active roots:')
for r in active_roots: rt(r)
# print('\nThese are the inconsistent:')
# for r in inconsistent: rt(r)
print('\nThese are the completed roots:')
for r in completed: rt(r)

