"""

The `decorators` module provides a decorator `instance_or_classmethod` that allows methods to be called on either an instance of a class or the class itself without the need to define the method specifically as an instance method or a class method. This decorator creates a custom descriptor that decides how to handle the method call based on whether `instance` is `None` or not.

The `instance_or_classmethod` function takes a `decorated` function as an argument and returns a callable that acts depending on the context of its call. This function defines a nested `__get__` function within it that overrides the special `__get__` method, which is part of the descriptor protocol in Python. This `__get__` method is used to determine how attributes of objects should be accessed.

If `instance` is `None`, which implies that the method is being called on the class, the `__get__` method delegates the call to the `__get__` method of `classmethod`, effectively turning the called method into a class method at that moment. If `instance` is not `None`, suggesting that the method is called on an instance of the class, the `__get__` method retrieves the function itself, allowing it to behave as an instance method.

This dynamic behavior adds flexibility to class design, especially when a method needs to behave differently depending on whether it is called by an instance or the class itself. It's implemented by creating a custom class type dynamically with the `type` function and then setting its `__get__` method to the one defined locally, applied to the `decorated` method. The module relies on Python's advanced features such as the descriptor protocol, the `classmethod` built-in decorator, and type creation on the fly with `type()`.
"""
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def instance_or_classmethod(decorated: Callable[P, R]) -> Callable[P, R]:
    """
    Transforms a function into a method that can behave either as a classmethod or an instance method.
    The function dynamically determines whether it should behave as a classmethod or an instance
    method upon being accessed. It modifies the '__get__' method of a new type, based on the 'classmethod'
    type, to change its behavior according to whether it is called from an instance or the class itself.
    
    Args:
        decorated (Callable[P, R]):
             The function that is to be converted into a dual-method. This function
            should be capable of handling both classmethod and instance method calls.
    
    Returns:
        Callable[P, R]:
             A callable object that can behave either as a classmethod or an instance method
            depending on how it is accessed.
    
    Raises:

    """

    def __get__(self, instance, owner):
        """
        Implements the descriptor protocol by returning a bound or unbound method.
        When '__get__' is invoked, it determines whether the method should behave as a class method or
        an instance method. If called on an instance, '__get__' returns the result of '__func__.__get__'. If called without an instance, '__get__' treats the method as a class method.
        
        Args:
            instance (object):
                 The instance that the method is accessed through, or 'None' if
                accessed through the owner.
            owner (type):
                 The owner class that this descriptor is a part of.
        
        Returns:
        
        Raises:
            TypeError:
                 If 'instance' is not an instance of 'owner'.

        """
        if instance is None:
            return classmethod.__get__(self, instance, owner)
        return self.__func__.__get__(instance, owner)

    return type(
        decorated.__name__,
        (classmethod,),
        {"__get__": __get__},
    )(decorated)
