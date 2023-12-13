"""
This module contains decorators that can be used to create new element classes for state machines.
"""
from typing import Callable, TypeVar, ParamSpec, Type, Any, Optional
from functools import wraps
from stateforward import elements
from stateforward import model

T = TypeVar("T")
R = TypeVar("R")
# P = ParamSpec("P")

# def name_of(decorated: Any) -> str:
#     return decorated.__name__ if isinstance(decorated, type) else decorated.__qualname__


def behavior(
    decorated: Callable[[elements.Behavior, Optional[elements.Event]], R],
    subtype: Optional[type[elements.Behavior]] = elements.Behavior,
) -> type[elements.Behavior]:
    """
    Decorator used to define a new behavior class from a behavior function.

    This decorator takes a function defining a behavior and returns a new subclass of Behavior
    that wraps the function. The resulting class can be used within state machines to associate
    behaviors with states.

    Args:
        decorated (Callable[[Behavior, Optional[Event]], R]): A behavior function that takes a
            Behavior instance and an optional Event as arguments and returns a result of type R.

    Returns:
        type[Behavior]: A new class that subclasses `Behavior`, encapsulating the decorated
            behavior function.

    Example:
        @behavior
        def my_behavior(self, event: Optional[Event]):
            # Implement behavior logic here.
            pass

    The `my_behavior` function is now wrapped in a new subclass of `Behavior` and can be used
    within the state machine framework to define state behavior.
    """

    @wraps(decorated)
    def wrapper(_decorated: Callable = decorated) -> Callable[[elements.Behavior], R]:
        return model.element.new(
            getattr(_decorated, "__name__", repr(_decorated)),
            bases=(subtype,),
            activity=_decorated,
        )

    return wrapper(decorated)


def constraint(
    decorated: Callable[[elements.Constraint, elements.Event], bool]
) -> Type[elements.Constraint]:
    """
    A decorator to create new Constraint elements in a model.

    `constraint` is utilized to wrap a function that defines the condition of a new
    Constraint element within the domain model. This decorator automatically creates
    a new element class that inherits from `elements.Constraint` and associates the
    wrapped function with the new class as its condition-checking method.

    The decorated function is expected to return a boolean indicating whether the
    constraint is met (`True`) or violated (`False`).

    ### Parameters:
    - `decorated`: A callable that represents the condition of the constraint. This callable
      should accept two parameters:
      - The `self` parameter, as an instance of `elements.Constraint`
      - The `event` parameter, as an instance of `elements.Event` representing the event
        that should be evaluated against the constraint.

    ### Returns:
    - A new class derived from `elements.Constraint` that uses the decorated callable as the
      condition method for evaluating the constraint.

    ### Example:

    ```python
    import stateforward as sf

    @sf.decorators.constraint
    def example_constraint(self, event: sf.Event):
        # Logic to determine if the constraint is met
        return some_condition_check(event)

    ```
    """

    @wraps(decorated)
    def wrapper(
        _decorated: Callable[[elements.Constraint, elements.Event], bool] = decorated
    ):
        return model.new(
            getattr(_decorated, "__name__", repr(_decorated)),
            bases=(elements.Constraint,),
            condition=_decorated,
        )

    return wrapper(decorated)


def call_event(
    decorated: Callable[[elements.CallEvent, elements.Event], Any]
) -> Type[elements.CallEvent]:
    """
    Decorator that turns a function into a specialized CallEvent class in a state machine.

    This decorator is utilized to create a subclass of elements.CallEvent with the provided function acting
    as the 'operation' for that event type. CallEvent is typically used to represent invocations of behavior
    that are triggered by an event. By extending elements.CallEvent through this decorator, a function can be
    integrated into the state machine as a callable event that encapsulates specific operation logic.

    Args:
        decorated: The function to be decorated. It takes an instance of elements.CallEvent and an instance of
                   elements.Event as parameters and can return any type. The returned value can be used within
                   the state machine to determine subsequent actions or transitions.

    Returns:
        A type that is a subclass of elements.CallEvent, representing a callable event with the decorated
        function as its operation logic.

    Example:
        @call_event
        def example_call_event(call_event: elements.CallEvent, event: elements.Event):
            # Operation logic for the call event.
            # This code is executed when the call event is triggered.
            perform_some_operation()

        # example_call_event is now a CallEvent subclass with operation defined by the example_call_event function.
    """

    @wraps(decorated)
    def wrapper(_decorated: Callable[..., Any] = decorated) -> Type[elements.CallEvent]:
        return model.element.new(
            _decorated.__name__,
            bases=(elements.CallEvent,),
            operation=_decorated,
        )

    return wrapper(decorated)
