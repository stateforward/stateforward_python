"""

The `__init__` module is the entry point for a package that provides functionality related to handling and structuring model elements, collections of elements, and their associations. It includes components that allow users to define, manipulate, and validate structured data models, as well as traverse and manipulate these models efficiently. This module imports and exposes all the necessary classes, functions, and types needed for these purposes.

### Main Components:

- `Element`: A generic base class that defines a model element.
- `Collection`: Extends `Element` to represent a collection of model elements.

### Element Manipulation:

- `redefine`: Function to create a new class by redefining an existing element.
- Functions like `find_owned_elements_of`, `owned_elements_of`, `remove_owned_elements_from`, `add_owned_element_to`, etc., provide ways to manipulate ownership and structure of model elements.

### Traversal Helpers:

- `ancestors_of`, `descendants_of`, `find_ancestor_of`, `find_descendants_of` are utility functions for traversing relationships between elements.

### Association Handling:

- Includes utility functions and classes for managing associations between elements, like `associations_of`, `is_association`, `association`.

### Validation and Preprocessing:

- `Preprocessor` and `Validator` classes help in validating and preprocessing model elements, ensuring correctness and consistency.

### Model Serialization:

- The module provides a `dump` function for serializing elements and debugging.

### Miscellaneous Utilities:

- Utility functions like `name_of`, `qualified_name_of`, `id_of`, `owner_of`, `type_of`, `is_descendant_of`, for retrieving various attributes and relationships of model elements.
- `of` function to get the model an element belongs to.

### Visitor Pattern Implementation:

- `Visitor` class that implements the visitor pattern to traverse and operate on a structure of elements.

Note that the details like the method names and definitions of classes are abstracted and only the purpose and interaction model are mentioned in this overview.
"""
from . import element
from .element import (
    Element,
    redefine,
    find_owned_elements_of,
    find_descendants_of,
    owned_elements_of,
    remove_owned_elements_from,
    remove_owned_element_from,
    associations_of,
    add_owned_element_to,
    descendants_of,
    attributes_of,
    ancestors_of,
    find_ancestor_of,
    find_owned_element_of,
    name_of,
    id_of,
    owner_of,
    qualified_name_of,
    type_of,
    find_owned_element_of,
    is_descendant_of,
    ElementType,
    set_attribute,
)
from .collection import Collection, collection, sort_collection, extend_collection
from .model import Model, dump, of
from .preprocessor import Preprocessor
from .validator import Validator
from .association import is_association, Association, association
from .visitor import Visitor


__all__ = (
    "Element",
    "redefine",
    "find_owned_elements_of",
    "owned_elements_of",
    "find_descendants_of",
    "remove_owned_elements_from",
    "remove_owned_element_from",
    "add_owned_element_to",
    "ancestors_of",
    "find_ancestor_of",
    "find_owned_element_of",
    "set_attribute",
    "name_of",
    "id_of",
    "owner_of",
    "descendants_of",
    "qualified_name_of",
    "type_of",
    "find_owned_element_of",
    "associations_of",
    "is_descendant_of",
    "ElementType",
    "attributes_of",
    "Collection",
    "collection",
    "sort_collection",
    "extend_collection",
    "Model",
    "dump",
    "of",
    "Preprocessor",
    "Validator",
    "is_association",
    "Association",
    "association",
    "Visitor",
    "element",
)
