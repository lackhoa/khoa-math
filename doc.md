# File `kset.py`:
This file contains the structure for atoms' values attribute.

## KSet
This is the stuff that atoms' values are made of. ksets are usually
(and preferably) iterables, but contains more auxiliary stuff.

There are three levels of clarity information a kset can have, expressed in `content`:
1. explicit: `content` is an iterable,
2. known: `content` is not an iterable, but a predicate to test membership, and finally
3. unknown: `content` equals to KSet.UNKNOWN.

`user_len` is a user-defined integer on the object, mainly
used for heuristic problem solving, not to reflect the actual length of
its content.

More on `KConst.UNKNOWN`: Technically speaking, there is no such thing as "unknown values".
However, there are cases when there is no incentive to iterate
through all the possible values, since it is so huge. Also, In a few cases
(e.g. real numbers), there might be no way to enumerate all the values.

A KSet whose content has no element (whose boolean value is False) stands
for a surely "impossibile" value, meaning that there is a logical inconsistency.

### Methods:
#### `__len__(self)`
If `user_len` is present, returns that. Otherwise returns the content's built-in
length if it's supported. If neither are present, raise LengthNotSupportedError.

#### `unify(s1, s2)`
Binary operation unify the content of two ksets. With the slogan:
"You can never learn less, you can only learn more". The function tries
to gather as much knowledge as it can.

The result can be any of the 3 possible clarity levels, explicit results are favored.

I cannot decide what to do with the resulting len() at the moment, let us see.

# File `khoa_math.py`:
This file contains the basic constructs of mathematics.

All "Math Objects" stored as tree. Atoms are leaves, and
molecules are branches.

## Class `MathObj` (Inherits `NodeMixin`)
Stands for Math Objects, the abstract base class for atoms and molecules

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

## Class `Atom` (Inherits `MathObj`)
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

### Remarks
Atoms' values are the only data in the tree.

While the `parent` attribute of an atom could be None, it's rare to see
because it means that this atom is the only in its tree.

## Class `Molecule` (Inherits `MathObj`)
A molecule consists of: a type, a constructor, children, and a name.

Type & Constructor: These are mandatory attributes for molecules.
Types must be elements of the MathType enum, while constructors should be
enum specified in the module specifying the type.

Children: can be atoms or other molecules. In program context, they're exactly
like children node of the molecule.

Name: optional, mainly for referencing roots

### Methods
#### `kattach(child, parent, overwrite)`:
This static method attaches child to parent, potentially overwriting other nodes.

`:param overwrite:` If set to `True`, if there is already another node
with the same role, delete that node and attach the child instead.
If set to False, don't do anything.
