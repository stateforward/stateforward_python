from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")


def instance_or_classmethod(decorated: Callable[P, R]) -> Callable[P, R]:
    """
    Decorator that converts a function into an instance or class method, depending on how it's accessed.

    This allows the function to act like a static method when called on the class and an instance
    method when called on an instance. It leverages the descriptor protocol to determine the behavior.

    Args:
        decorated (Callable[P, R]): The function to be converted.

    Returns:
        Callable[P, R]: A callable that behaves either as an instance method or a class method.
    """

    def __get__(self, instance, owner):
        if instance is None:
            return classmethod.__get__(self, instance, owner)
        return self.__func__.__get__(instance, owner)

    return type(
        decorated.__name__,
        (classmethod,),
        {"__get__": __get__},
    )(decorated)
