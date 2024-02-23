"""

A module that defines the `Preprocessor` class, which inherits from the `Visitor` class.

The `Preprocessor` class serves as a base class for creating preprocessors that can visit different nodes in a data structure, such as a syntax tree or a graph. It extends the functionality provided by the `Visitor` class by allowing for preprocessing of these nodes. The preprocessors are expected to implement methods with a prefix 'preprocess' which corresponds to the type of node they will visit and operate on.

The `__all__` definition specifies that the only symbol that should be publicly available when importing this module is 'Preprocessor'.

The module also contains a special function `__get__` within an unspecified class. This function seems to be associated with a descriptor object for handling method retrieval. When the `instance` parameter is `None`, it treats the method as a classmethod and redirects the call to the classmethod's `__get__` function. Otherwise, it accesses the function associated with the instance through the `__func__` attribute and returns it bound to the `instance` and `owner`.
"""
from stateforward.model.visitor import Visitor


__all__ = ("Preprocessor",)


class Preprocessor(Visitor, visit_method_prefix="preprocess"):
    """
    A class that extends the functionality of the Visitor class, designated for preprocessing tasks.
    The Preprocessor class inherits from the Visitor class and provides an interface for preprocessing-related visitation methods. It uses a specific method prefix 'preprocess' to differentiate its methods from those in the Visitor class. This class serves as a base class and is typically subclassed to implement specific preprocessing logic required for various tasks.
    
    Attributes:
        visit_method_prefix (str):
             A string prefix used to identify preprocessing methods distinct from those in the base Visitor class.

    """

    pass
