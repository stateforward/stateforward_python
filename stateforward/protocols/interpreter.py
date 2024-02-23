"""

## Module `interpreter`

This module contains the implementation of the `Interpreter` protocol, which is responsible for processing state-forwarding models and handling their execution flow. It uses asynchronous I/O for its operations, leveraging Python's `asyncio` library. The module depends on several other components like `Queue`, `Clock`, and `Future` to manage the scheduling of tasks and the progression of time within the simulation.

### Classes

- `InterpreterStep`: An `Enum` representing the state of a step within the `Interpreter`. Possible values are `complete`, `incomplete`, and `deferred`.

- `Interpreter`: A protocol that defines the interface for an interpreter instance. These instances are responsible for orchestrating elements of the state-forwarding model. They manage a queue, a clock, a stack of futures, and a logging instance.

### Interpreter Protocol Methods

- `__init__`: Constructor for the interpreter. It takes a `Queue` instance and an optional `logging.Logger` instance as parameters.

- `send`: Takes an event of type `model.Element` and schedules it for processing, returning a `Future` representing the eventual result of processing this event.

- `start`: Initiates the interpreter loop which can be provided through the `loop` parameter; if `None`, the default event loop is used.

- `wait`: Waits on a collection of `tasks`, which can be either `asyncio.Task` or `asyncio.Future` objects. It accepts an optional `name` to identify the wait operation and a `return_when` strategy that governs when the wait should return.

- `run`: An asynchronous method that runs the interpreter to completion.

- `step`: An abstract asynchronous method that should be implemented to perform a single step of the interpreter's operation.

- `is_active`: Checks whether the provided `elements` are active within the current state model context.

- `push`: Associates an `element` with a `future` object, pushing it onto the interpreter's stack.

- `pop`: Removes an `element` from the interpreter's stack, providing a `result` to the associated future.

- `terminate`: Cleans up and terminates the interpreter's operation.

### Attributes

- `model`: An attribute of the generic type `T`, which is bound to `model.Model` and represents the model instance that the interpreter is operating on.
"""
import typing
from stateforward import model
from enum import Enum
import asyncio
from stateforward.protocols.future import Future
from stateforward.protocols.clock import Clock
from stateforward.protocols.queue import Queue
import logging


T = typing.TypeVar("T", bound=model.Model)


class InterpreterStep(Enum):
    """
    An enumeration to represent the possible states of an interpreter step.
    This enum classifies the status of a step within an interpreter's execution process. Each member of the enumeration represents a distinct state that indicates the completeness of the current step being processed.
    
    Attributes:
        complete (str):
             A member indicating the interpreter step has been successfully completed without any pending actions.
        incomplete (str):
             A member indicating the interpreter step is not yet finished and may require further processing.
        deferred (str):
             A member indicating the interpreter step's execution has been postponed and will be revisited later.

    """

    complete = "complete"
    incomplete = "incomplete"
    deferred = "deferred"


class Interpreter(typing.Protocol[T]):
    """
    A protocol class that defines the interface for an interpreter capable of handling events,
    managing an event loop, and interacting with a queue and a clock system.
    
    Attributes:
        queue:
             An instance of Queue where the interpreter manages scheduled events.
        clock:
             An instance of Clock that provides timing functionality.
        stack:
             A dictionary mapping model components to their corresponding futures.
        log:
             A Logger instance where the interpreter can log messages.
    
    Methods:
        __init__:
             Constructor that initializes the interpreter with a given queue and an optional logger.
        send:
             Sends an event to the interpreter for processing and returns a Future.
        start:
             Initiates the event loop for the interpreter with an optional loop argument.
        wait:
             Waits for the completion of the given tasks or futures and returns a collected Task.
        run:
             Asynchronous method that starts running the interpreter event loop.
        step:
             Asynchronous method that performs a single step in the interpreter processing.
        is_active:
             Checks if any of the provided elements are currently active within the interpreter.
        push:
             Associates an element with a future or task in the interpreter's stack.
        pop:
             Removes an element from the stack and handles its corresponding result.
        terminate:
             Ends the interpreter's execution and cleans up resources.
        model:
             A generic type placeholder for the model handled by the interpreter.

    """

    queue: Queue
    clock: Clock
    stack: dict[model.Element, Future]
    log: logging.Logger

    def __init__(self, queue: Queue, log: logging.Logger = None):
        """
        Initializes the instance with a Queue and an optional Logger object.
        
        Args:
            queue (Queue):
                 The queue to be used by the instance for storing or processing tasks.
            log (logging.Logger, optional):
                 The logger to be used for logging information, warnings, errors, etc. Defaults to None, in which case no logging will be performed.

        """
        ...

    def send(self, event: model.Element) -> Future:
        """
        Sends an event to be processed asynchronously.
        This method accepts an event object, wraps it in a Future, and schedules it for asynchronous processing.
        The method returns a Future object that can be used to retrieve the result of the event processing at a later time.
        
        Args:
            event (model.Element):
                 The event to send for processing.
        
        Returns:
            Future:
                 The future object representing the asynchronous operation of the event processing.

        """
        ...

    def start(
        self,
        loop: asyncio.AbstractEventLoop = None,
    ):
        """
        Starts the asynchronous event loop for the instance.
        
        Args:
            loop (asyncio.AbstractEventLoop, optional):
                 The event loop to run the instance on. If None is provided, the default event loop is used.

        """
        ...

    def wait(
        self,
        *tasks: typing.Union[asyncio.Task, asyncio.Future],
        name: str = None,
        return_when: str = asyncio.FIRST_COMPLETED,
    ) -> asyncio.Task:
        """
        Waits for the completion of given tasks or futures until a condition is met.
        This method is used to asynchronously wait for either any or all of the specified tasks or futures to complete, depending on the `return_when` parameter. It can be used to orchestrate the execution of different asynchronous operations in a non-blocking manner.
        
        Args:
            *tasks (typing.Union[asyncio.Task, asyncio.Future]):
                 An unpacked tuple of tasks or futures.
                These are the asynchronous operations that `wait` will wait on.
            name (str, optional):
                 A name for the group of tasks being waited on. This name is not
                directly used by the `wait` function but can be useful for logging and debugging purposes.
            return_when (str):
                 A string that specifies when the function should return. The default
                value is `asyncio.FIRST_COMPLETED`, which means the function will return as soon as any task or future is done.
                Other possible values are `asyncio.FIRST_EXCEPTION`, which returns when any task or future raises an exception,
                and `asyncio.ALL_COMPLETED`, which returns only when all tasks or futures are completed.
        
        Returns:
            asyncio.Task:
                 A single asyncio.Task instance that can be awaited. This task completes when
                the condition specified in `return_when` is met.

        """
        ...

    async def run(self) -> None:
        """
        Asynchronously executes the function's main logic.
        This function is designed to be called within an asynchronous context. It runs
        the primary task or series of tasks that the class instance is responsible
        for managing. As it is an async function, it should be awaited when called
        to ensure proper execution and handling of the event loop.
        
        Returns:
            None:
                 This function does not return any value.

        """
        ...

    async def step(self) -> None:
        """
        Performs an asynchronous step operation for the object. This function is intended to be overridden by subclasses to implement specific asynchronous behavior. The default implementation does nothing and is meant to be a placeholder.
        
        Returns:

        """
        pass

    def is_active(self, *elements: model.Element) -> bool:
        """
        Determines if the given elements are active.
        This method checks if the specified elements within the model are currently active. 'Active' in this context refers to the
        elements being in a state where they are in use or in operation within the model. Each element provided as an argument
        to the function is checked, and the function returns True only if all elements are active, otherwise False.
        
        Args:
            *elements (model.Element):
                 Variable number of Element objects to check for active status.
        
        Returns:
            bool:
                 True if all elements are active, False otherwise.

        """
        ...

    def push(self, element: model.Element, future: typing.Union[Future, asyncio.Task]):
        """
        Adds a new element to a collection with an optional future or task associated with it.
        
        Args:
            element (model.Element):
                 The element to be added to the collection.
            future (typing.Union[Future, asyncio.Task]):
                 A future or task that is
                associated with the element being added. This is optional and can be
                used to track the completion or result of an asynchronous operation
                related to the element.
        
        Raises:
            TypeError:
                 If the provided future is neither a Future nor an asyncio.Task instance.

        """
        ...

    def pop(self, element: model.Element, result: typing.Any):
        """
        Pops an element from the given structure and returns the result.
        This method is designed to remove the specified element from the structure it is called upon,
        and optionally returns the result of this operation.
        
        Args:
            element (model.Element):
                 The element to remove from the structure.
            result (typing.Any):
                 The result to return after the element has been popped.
        
        Returns:
            typing.Any:
                 The specified return result after the popping operation.

        """
        ...

    def terminate(self):
        """
        Terminates the current process or operation.
        This method provides the functionality to cease the operation for the associated object. It is meant to be implemented as a cleanup action to safely shut down or close resources such as file handlers, network connections, or database connections before the termination of the process.
        
        Raises:
            NotImplementedError:
                 If the method has not been implemented by the subclass.

        """
        ...

    model: T = None
