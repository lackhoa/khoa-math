# About `kset.py`:
This file contains the structure for atoms' values attribute.

## KSet
This is the stuff that atoms' values are made of. ksets are ultimately
iterable, but contains more stuff like length (optional), and
some special elements like KElem.UNKNOWN.

KElem.UNKNOWN is an enum element representing unknown values.
Technically, there is no such thing as unknown values.
However, there are cases when there is no incentive to iterate
through all the possible values, since it is so huge. Also, In a few cases,
there might be no way to enumerate the values (e.g. real numbers).

An empty iterable stands for a surely "impossibile" value, meaning that
there is a logical inconsistency.

# About `khoa_math.py`:
This file contains the basic constructs of mathematics.

All "Math Objects" stored as tree. Atoms are leaves, and
molecules are branches.

## Math Objects (abbr. `MathObj`) (Inherits `NodeMixin`)
The abstract base class for atoms and molecules

A math object consists of: a role. Roles are means of indexing
and traversing through the trees.

### Methods
#### `__eq__(self, other)`
This function compares the values of the two nodes if they're atoms
, or all of their children if they're molecules.

#### `get(self, path)`: Navigate around
Get a descendant of a this object, referenced by `path`.

Paths are ultimately a series of movements, separated by forward slashes
(in UNIX fashion, but use roles instead of directory names).

#### `path(self)`
return the path which takes the root to this node by `get`.

#### `_recur_test(self, func, conj)`
Template for recursive tests on trees, written in normal form.

:param `func`: function to test on atoms.

:param `conj`: True for conjunctive test, False for disjunctive test.

## Atoms (Inherits Math Objects)
An atom consists of: "a" values, which is a kset, and a web.

There is a difference between *values the attribute* and what we
casually refer to as the value of the atom.
*values the attribute* represents all possible "real" values this atom might have,
but it's possible that even though there are infinitely many "possible"
values, we will not find any. However, if the atom exists and it has a value,
then the value must be an element of the value attribute.

The web is a list of paths referencing other atoms. Each other atom referenced
is dependent on this atom, and so they can potentially be updated when this atom
is updated.

Note that atoms' values are the only data in the tree.

Note on `parent`: While this attribute could be None, it's very rare to see
since it means that this atom is the only in its tree.

## Molecules (Inherits Math Objects)
A molecule consists of: a type, a constructor, children, and a name.

Type & Constructor: these are obvious. These are mandatory attributes.
Types must be elements of the MathType enum, while constructors should be
enum specified in the module specifying the type.

Children: can be atoms or other molecules. In program context, they're exactly
like children node of the molecule.

Name: optional, mainly for referencing roots
