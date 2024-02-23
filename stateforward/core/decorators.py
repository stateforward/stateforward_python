"""


    Wraps a callable that is intended to be used as an event handler for call events.
    
    The `call_event` decorator is designed to transform a callable into a subclass of `core.CallEvent`.
    The new subclass uses the decorated callable as an event handling operation.
    
    This decorator is typically used within the `stateforward` framework, where events are
    central to the state changes in a finite state machine.
    
    Args:
        decorated (Callable[[core.CallEvent, core.Event], Any]): The callable that will be transformed into
            a `core.CallEvent` subclass. This callable should take a `core.CallEvent` instance and a
            `core.Event` instance as arguments and return any type.
    
    Returns:
        Type[core.CallEvent]: A new subclass of `core.CallEvent` which encapsulates the decorated function as
            its event operation.

    Note that the decorator internally uses a wrapper function to perform the decoration, but it is the
    decorated callable that is returned.
"""
from typing import Callable, TypeVar, Type, Any, Optional
from functools import wraps
from stateforward import core
from stateforward import model

T = TypeVar("T")
R = TypeVar("R")


def behavior(
    decorated: Callable[[core.Behavior, Optional[core.Event]], R],
    subtype: Optional[type[core.Behavior]] = core.Behavior,
) -> type[core.Behavior]:
    """
    Creates a new behavior type based on a decorated callable and an optional behavior subtype.
    This function is a decorator that, when applied to a callable, constructs a new behavior type using a model element factory. It optionally takes a subtype of `core.Behavior` to be used as a base for the new behavior type. If a subtype is not provided, `core.Behavior` is used as the default base.
    The wrapped callable gets transformed into an `activity` attribute of the new behavior type. The name of the new behavior type is either taken from the `__name__` attribute of the decorated callable or its representation if `__name__` is not available.
    
    Args:
        decorated (Callable[[core.Behavior, Optional[core.Event]], R]):
             The callable to be decorated, which represents the logic of the behavior. The callable should have at least one parameter to accept an instance of `core.Behavior` and an optional second parameter to accept an instance of `core.Event`.
        subtype (Optional[type[core.Behavior]]):
             The subtype of `core.Behavior` to use as the base for the new behavior type. If not provided, `core.Behavior` is used as the default.
    
    Returns:
        type[core.Behavior]:
             A new subclass of `core.Behavior` or the provided subtype, with the decorated callable assigned as the `activity` method.

    """

    @wraps(decorated)
    def wrapper(_decorated: Callable = decorated) -> Callable[[core.Behavior], R]:
        """
        Decorates a function to create a new CallEvent type with the provided function as its operation.
        This function is intended to be used as a decorator, which when applied to another function, utilizes the functionality
        of the `model.element.new` method to create a new subclass of `core.CallEvent` with the decorated function as
        its operation. The name of the new CallEvent type will be the same as the name of the decorated function.
        
        Args:
            _decorated:
                 The function to be used as the operation for the new CallEvent type. The default value is the
                decorated function itself, which allows this wrapper to be used as a decorator.
        
        Returns:
            Type[core.CallEvent]:
                 A new subclass of core.CallEvent that encapsulates the provided operation function.

        """
        return model.element.new(
            getattr(_decorated, "__name__", repr(_decorated)),
            bases=(subtype,),
            activity=_decorated,
        )

    return wrapper(decorated)


def constraint(
    decorated: Callable[[core.Constraint, core.Event], bool],
) -> Type[core.Constraint]:
    """
    Decorate a function to turn it into a Constraint subclass.
    Takes a function that acts as a condition for a `core.Constraint` object and returns a new subclass of `core.Constraint`
    that can be used within the model to enforce that condition. The `decorated` function must take two arguments, namely
    an instance of `core.Constraint` and an instance of `core.Event`, and return a boolean indicating whether the condition
    is met or not.
    
    Args:
        decorated (Callable[[core.Constraint, core.Event], bool]):
             The function to be turned into a `core.Constraint` subclass.
            It should accept a `core.Constraint` instance and a `core.Event` instance and return a boolean.
    
    Returns:
        Type[core.Constraint]:
             A new subclass of `core.Constraint` that represents the condition defined by the `decorated` function.
        Note:
            The `wrapper` function inside `constraint` is a closure that captures the `decorated` function and uses it to create
            the new subclass of `core.Constraint`. This subclass is then returned when the `constraint` function is called.

    """

    @wraps(decorated)
    def wrapper(_decorated: Callable[[core.Constraint, core.Event], bool] = decorated):
        """
        Decorates a function to create a new specialized `core.CallEvent` type.
        This function takes another function (`_decorated`) intended to be used as an operation for a new `core.CallEvent` type. It applies the Python `wraps` decorator to carry over the metadata from `_decorated`. It uses `model.element.new` to dynamically create a new subclass of `core.CallEvent` with `_decorated` as the event operation.
        
        Args:
            _decorated (Callable[..., Any]):
                 The function to use as an operation for the new event type. Defaults to the `decorated` variable from the outer scope which is presumed to be a callable.
        
        Returns:
            Type[core.CallEvent]:
                 A new subclass of `core.CallEvent` that incorporates the `_decorated` function as an operation.

        """
        return model.new(
            getattr(_decorated, "__name__", repr(_decorated)),
            bases=(core.Constraint,),
            condition=_decorated,
        )

    return wrapper(decorated)


def call_event(
    decorated: Callable[[core.CallEvent, core.Event], Any],
) -> Type[core.CallEvent]:
    """
    Creates a CallEvent subclass that is associated with the provided callable.
    This function is a decorator factory which, when called with a function reference (`decorated`),
    returns a decorator. The decorator then constructs a new subclass of `core.CallEvent` that
    incorporates the `decorated` callable as its operation.
    
    Args:
        decorated (Callable[[core.CallEvent, core.Event], Any]):
             The callable to be associated
            with the CallEvent subclass. This callable typically performs an operation related to
            an event in the event-handling system.
    
    Returns:
        Type[core.CallEvent]:
             A new subclass of `core.CallEvent` that is tied to the `decorated`
            callable.

    """

    @wraps(decorated)
    def wrapper(_decorated: Callable[..., Any] = decorated) -> Type[core.CallEvent]:
        """
        A decorator function that wraps the given callable into a new type derived from `core.CallEvent`.
        This decorator takes a callable, typically representing an event handling function, and creates a new class type that inherits from `core.CallEvent` with the given callable as its operation. The newly created class type reflects the name of the decorated function and can be used to handle events within the system, where the type encapsulation is needed for event management.
        
        Args:
            _decorated (Callable[..., Any], optional):
                 The callable, usually a function, to be converted into a new `core.CallEvent` subclass. Defaults to the callable passed to the `call_event` decorator.
        
        Returns:
            Type[core.CallEvent]:
                 A newly created subclass of `core.CallEvent` that encapsulates the decorated callable as its operation.

        """
        return model.element.new(
            _decorated.__name__,
            bases=(core.CallEvent,),
            operation=_decorated,
        )

    return wrapper(decorated)
