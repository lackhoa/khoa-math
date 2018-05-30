from khoa_math import *
from wff import *

from anytree import LevelOrderGroupIter, PreOrderIter
from copy import deepcopy, copy


def custom_rules(child, parent):
    """
    Some new rules for this program.
    """
    new_nodes = []
    role = child.role
    val = child.value

    if role == 'cons':
        if val == {PlCons.ATOM}:
            # Atoms have texts, and that text should be 'P'
            new_nodes += [( MathObj( role='text', value={'P'}), '')]

    return new_nodes


# Set up the environment
counter = 1  # How we get new ids
form0 = MathObj(id_ = '#0')  # The starting unknown formula
MathObj.propa_rules += [wff_rules, custom_rules]  # These are the rules we're using today
roots = [form0]  # Store the active roots
inconsistent = []  # Store the inconsistent objects
completed = []  # Store the completed objects

type_ = MathObj(role='type', value={MathType.PL_FORMULA})
MathObj.kattach(type_, form0)  # Attach the type to the form0


# We proceed level-by-level, as indexed by 'dep'
LEVEL_CAP = 6
REPEAT = 3
# Each level is repeated a few times before incremented
for dep in [x for x in range(LEVEL_CAP) for _ in range (REPEAT)]:

    print('\n\nWorking up to level {}'.format(dep+1))

    # Then we do two jobs for each root
    # Job 1 (Exploring): Attach nodes from the queue:
    for root in copy(roots):
        for queue_item in copy(root.queue):
            node, ref, path = queue_item

            # Path processing:
            path = path.split('/')
            parent = ref
            # Process the path UNIX style:
            for n in path:
                if n == '': continue
                elif n == '..':
                    if not parent: raise Exception('Rule cannot be applied!')
                    else: parent = parent.parent
                else:
                    if not parent: raise Exception('Rule cannot be applied!')
                    else: parent = parent.get(n)

            if parent and parent.depth <= dep:  # must attach level-by-level, for safety
                MathObj.kattach(node, parent)
                root.queue.remove(queue_item)  # This is fine since we're iterating on a copy

        # Job 2 (Expanding): expand the possible values:
        all_nodes = [node for node in PreOrderIter(root)]
        node_index = 0  # This value will be "preserved" when cloning
        for node in all_nodes:
            if node.value and len(node.value) > 1:  # If there are multiple possible values
                for v in (node.value - {KSet.UNKNOWN}):  # Expand them all
                    # Create an identical tree, change the id
                    root_clone = root.clone()
                    root_clone.id = '#{}'.format(counter)
                    roots.append(root_clone)
                    counter += 1

                    # This tree has value 'v':
                    new_node = MathObj(role=node.role, value={v})
                    all_nodes_clone = [node_clone for node_clone in PreOrderIter(root_clone)]
                    node_clone = all_nodes_clone[node_index]
                    MathObj.kattach(new_node, node_clone.parent)

                # Clean up the value from the original tree
                node.clear_val()
            node_index += 1

    # Clean-up routine afterwards
    for root in copy(roots):
        # Find inconsistent trees
        if root.is_inconsistent():
            roots.remove(root)
            inconsistent += [root]

        # Find completed trees
        elif root.is_complete():
            roots.remove(root)
            completed += [root]




# Printing out the resulting lists:
rt = lambda t: print(str(RenderTree(t)) + '\n')
print('These are the active roots:')
for r in roots: rt(r)
print('\nThese are the inconsistent:')
for r in inconsistent: rt(r)
print('\nThese are the completed:')
for r in completed: rt(r)

