# Information About This Document
This document contains the meaning of every module in the project. I must
emphasize that this is NOT a docstring, but an extensive "comment" of the code.
It says what the code does not say, like specifying the structure of classes,
what the methods are for, what sentinel values mean, etc.

# File `kset.py`:
This file contains the structure for atoms' values attribute.

## KSet
This is the stuff that atoms' values are made of. ksets are usually
(and preferably) iterables, but contains more auxiliary stuff.

There are three levels of clarity information a kset can have, expressed in `content`:
1. explicit: `content` is an iterable,
2. known: `content` is not an iterable, but a predicate to test membership, and finally
3. unknown: `content` equals to KSet.UNKNOWN.

`user_len` is a user-defined length of the object, mainly used for heuristic
problem solving and does not necessarily reflect the actual length of its
content. This attribute has another usage when the content is explicit and we
know exactly how many items will be generated, but the len() method is not
supported. We usually want to assign the upper-bound value for length.

More on `KConst.UNKNOWN`: Technically speaking, there is no such thing as
"unknown values".  However, there are cases when there is no incentive to
iterate through all the possible values, since it is so huge. Also, In a few
cases (e.g. real numbers), there might be no way to enumerate all the values.

A KSet whose content is an empty iterator represents a surely "impossibile" value,
meaning that there is a logical inconsistency. Note that even though the False predicate
means essentially the same thing, there is no way we can check for that.

Another special case is when the iterator only has one element, then we can deduce
other useful facts. This state is checked by the method `is_singleton(self)`.


### Methods:
#### `__len__(self)`
A prerequisite for this method is that `self` must be explicit, otherwise it
throws a LengthUnsupportedError. However, users can still mess this up since
`user_len` is consulted first.

#### `__and__(self, other)`
This operation is called "unification", a symmetric binary operation that
unifies the content of two ksets. With the slogan: "You can never learn less,
you can only learn more". The function tries to gather as much knowledge as it
can.

The result can be any of the three possible clarity levels, explicit results
are favored. Specifically, unifying an explicit kset with anything returns an
explicit kset, and only by unifying two unknown ksets can we get back an
unknown kset.

The `user_len` of the result is maximized among the two ksets.

# File `khoa_math.py`:
This file contains the basic constructs of mathematics.

All "Math Objects" stored as tree. Atoms are leaves, and
molecules are branches.

## Class `MathObj` (Inherits `NodeMixin`)
Stands for Math Objects, the abstract base class for atoms and molecules

A math object consists of: a role. Roles are means of indexing
and traversing through the trees.

### Methods
#### `get(self, path)`: Navigate around
Get a descendant of a this object, referenced by `path`.

Paths are ultimately a series of movements, separated by forward slashes
(in UNIX fashion, but use roles instead of directory names).

#### `path_from(self, origin)`
return the path which takes the origin to this node by `get`.

#### `_recur_test(self, func, conj)`
Template for recursive tests on trees, written in normal form.

:param `func`: function to test on atoms.

:param `conj`: True for conjunctive test, False for disjunctive test.

## Class `Atom` (Inherits `MathObj`)
An atom consists of: "a" values, which is a kset, and an iterable web.

There is a difference between *values the attribute* and what we
casually refer to as the value of the atom.
*values the attribute* represents all possible "real" values this atom might have,
but it's possible that even though there are infinitely many "possible"
values, we will not find any. However, if the atom exists and it has a value,
then the value must be an element of the value attribute.

The web is collection of paths referencing other atoms. Each other atom referenced
is dependent on this atom, and so they can potentially be updated when this atom
is updated.

### Remarks
Atoms' values are the only data in the tree.

While the `parent` attribute of an atom could be None, it's rare to see
because it means that this atom is the only in its tree.

## Class `Molecule` (Inherits `MathObj`)
A molecule consists of: a type, children, and a name.

Type: These are mandatory attributes for molecules. Types must be elements of
the MathType enum

Constructor (`cons`): It is actually one of the molecule's children. Even though
it is also a special attribute like `type`, a lot of time we want a constructor
to be unknown. Why is `cons` special? Because we can look up the values in the
type module.

Children: can be atoms or other molecules. In program context, they're exactly
like children node of the molecule.

Name: optional, mainly for referencing roots

# File `k_math_more.py`

This builds on top of `khoa_math.py`, providing more concepts to interface user
code.

## Class `AtomData` and `MoleData`

These dataclasses represents math objects that are yet to be attached to the
tree. They are useful for interfacing with type modules' component
dictionaries.

# Type Modules Concepts

For each type in MathType, we have a type module consisting of:

1. A "constructor enum" (named `<type>Cons`) listing all constructors for the
   type, and

2. An "component dictionary" (named `<type>comp_dic`) mapping the type's
   constructors to corresponding lists of components as AtomTups and MoleTups,
   which can be thought of as "template" for actual atoms/molecules to be
   attached.

3. A to-string function (named `<type>to_str(mol)`) representing Molecules in
   usual mathematical notatoin.

Every time you want to expand a molecule of this type, determine a constructor
in the constructor enum, consult the component dictionary for this constructor,
construct the nodes according to the values returned, and attach those to the
molecule in question. Since this procedure is recursive, you can continue to
expand the new nodes.

# File `type_mgr.py` (The Type Manager)

For ease of typing management, there is a file called `type_mgr.py` containing
a dictionary `cons_dic` mapping types to their listings of constructors,
`comp_dic` maps types to their component dictionaries, and `math_str` function,
which will return a mathematical representation of the molecule passed in,
reguardless of its type.

Of course, this file is dependent on all type modules involved.

# Listing Of Type Modules:

* `wff.py` specifies well-formed formulas
