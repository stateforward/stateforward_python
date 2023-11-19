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
    Determine whether the provided value is a ProxyType or CallableProxyType.

    Parameters:
    - value (Any): The value to check.

    Returns:
    - bool: True if 'value' is an instance of ProxyType or CallableProxyType, False otherwise.
    """
    return isinstance(value, (ProxyType, CallableProxyType))


def association(element: T) -> Association[T]:
    """
    Create a weak proxy reference to 'element'. If 'element' is already a proxy, it is returned as is.

    A weak proxy reference allows one to access an object without preventing it from being
    automatically destroyed by Python’s garbage collector.

    Parameters:
    - element (T): The original object to which the association (proxy reference) will be created.

    Returns:
    - Association[T]: A weak proxy reference to 'element'.
    """
    new_association = proxy(element) if not is_association(element) else element
    return new_association
