from typing import TypeVar, Generic, Callable, Union, Sequence
from stateforward.model.element import Element
import asyncio
from enum import Enum

T = TypeVar("T")
Q = TypeVar("Q")

__all__ = ("Interpreter", "Processing")


class Processing(Enum):
    pending = "pending"
    complete = "complete"
    incomplete = "incomplete"
    deferred = "deferred"


class Interpreter(Element, Generic[T, Q]):
    """
    The Interpreter class is responsible for processing and handling elements within a model.

    It interfaces with the model by maintaining lists of active elements, a dispatch logic for events,
    and checks for activity states. It can be subclassed to provide specific interpretation logic,
    such as asynchronous processing capabilities.

    Attributes:
        queue (Union[type[Q], Q]): The type or instance of a queue used by the interpreter to handle
            elements. This attribute should be overridden by a subclass to provide a specific queue type or instance.
        idle (Union[asyncio.Event]): An event that signals whether the interpreter is idle.
            For asynchronous interpreters, this is an asyncio Event instance.
        active (dict[Element, T]): A dictionary mapping elements to activity markers. Activity markers can be of any
            type that signifies the state of processing of each element.
        dispatch (Union[Callable[[Element], asyncio.Task], Callable[[Element], None]]):
            A callable that takes an element and returns an asyncio Task (for asynchronous interpreters)
            or None (for synchronous interpreters). This method is responsible for handling the dispatching logic.
        is_active (Callable[[Element], bool]): A method that takes an element and returns a boolean
            indicating whether the element is under active processing by the interpreter.
        start (Callable[[], asyncio.Task]): A method that starts the interpreter's processing loop.
            In an asynchronous environment, it returns an asyncio Task instance.
        terminate (Union[Callable[[], asyncio.Future], Callable[[], "Interpreter"]]):
            A method that stops the interpreter's processing loop and performs any necessary clean-up steps.
            In an asynchronous environment, it returns an asyncio Future instance.

    Type Parameters:
        T: The type used to indicate activity markers for elements.
        Q: The type of queue used for managing elements to be processed.
    """

    queue: Union[type[Q], Q] = None
    idle: Union[asyncio.Event] = None
    active: dict[Element, T] = None
    dispatch: Union[Callable[[Element], asyncio.Task], Callable[[Element], None]] = None
    is_active: Callable[[Sequence[Element]], bool] = None
    start: Callable[[], asyncio.Task] = None
    terminate: Union[Callable[[], asyncio.Future], Callable[[], "Interpreter"]] = None

    def __init__(self, *args, **kwargs):
        self.active = {}
        self.queue = self.queue()
