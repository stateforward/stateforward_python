"""

The `association` module defines utilities and types for managing associations through proxy mechanisms. The module's central feature is the `Association` type, which is a union of Annotated types using NewType to represent either a `CallableProxyType` or a `ProxyType`. 

This module also provides the function `is_association`, which checks if a given value is an instance of either `ProxyType` or `CallableProxyType`, and hence can be considered an association according to the module's definition.

The `association` function within the module is responsible for creating an association to the passed element. If the given element is not already an association, it will be wrapped in a proxy using the `proxy` function from the `weakref` module. If it is an association, it is returned unchanged. This enables users to maintain and handle associations to objects that should not be strongly referenced while still allowing for the invocation of callable methods if available.

The module also includes a `__get__` method, typically used for extending descriptor classes. This method aids in retrieving the association for a given instance, falling back to the class method's behavior if the instance is `None`. The use of this method is internally focused and supports the machinery of the association types.
"""
from typing import Annotated, Union, NewType, TypeVar, Any
from weakref import ProxyType, CallableProxyType, proxy

T = TypeVar("T")

# Define a new type 'Association' which is a union of Annotated types using NewType.
# It represents an association with either a 'CallableProxyType' or a 'ProxyType'.
Association = Union[
    Annotated[T, NewType("Association", CallableProxyType)],
    Annotated[T, NewType("Association", ProxyType)],
]


def is_association(value: Any) -> bool:
    """
    Determines whether the provided value is an instance of `ProxyType` or `CallableProxyType`.
    
    Args:
        value (Any):
             The value to be checked if it's an association proxy or callable proxy.
    
    Returns:
        bool:
             True if the value is an instance of `ProxyType` or `CallableProxyType`, otherwise False.

    """
    return isinstance(value, (ProxyType, CallableProxyType))


def association(element: T) -> Association[T]:
    """
    Creates an association proxy object from a given element.
    If the element is not already an association proxy object, it will create a new proxy for it using the `proxy` function. If it is already an association proxy object, it simply returns the element as-is.
    
    Args:
        element (T):
             The element to be converted into or verified as an association proxy object.
    
    Returns:
        Association[T]:
             An association proxy object for the given element.

    """
    new_association = proxy(element) if not is_association(element) else element
    return new_association
