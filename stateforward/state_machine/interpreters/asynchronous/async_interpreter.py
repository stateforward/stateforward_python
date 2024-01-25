"""

Module that provides an asynchronous interpreter, designed for executing and managing state machines in an asyncio environment.

This module houses the `AsyncInterpreter` class which acts as an interpreter for state machines defined by the `model.Model` class. It provides methods to start, run, wait for tasks, send events, and terminate the interpretation cycle. It also includes an `InterpreterStep` enum to define the step status and a constant `NULL` of a pre-resolved asyncio.Future.

Classes:
    InterpreterStep(Enum): Enumeration of possible interpreter step outcomes.
    AsyncInterpreter(Generic[T]): The main class that interprets and executes state machines.

Attributes:
    queue (Queue): An instance of the Queue protocol that serves as the event queue.
    clock (Clock): An implementation of the Clock protocol for event scheduling.
    stack (dict[model.Element, asyncio.Future]): A mapping to track the execution state of state machine elements.
    loop (asyncio.AbstractEventLoop): The event loop where the interpreter operates.
    log (logging.Logger): Logger instance to output debug information.
    running (asyncio.Event): An event to indicate whether the interpreter is running.

Functions:
    start(loop: asyncio.AbstractEventLoop=None): Starts the async interpreter.
    send(event: model.Element): Accepts an event, pushes it onto the stack, and enqueues it.
    step(): Progresses the state machine by one step, checking the status of tasks.
    is_active(*elements: model.Element): Checks if the provided elements are currently active.
    push(element: model.Element, future: typing.Union[Future, asyncio.Task]): Pushes an element onto the stack with an associated `Future` or task.
    pop(element: model.Element, result: typing.Any=NULL): Pops an element and its associated future from the stack.
    terminate(): Stops the async interpreter's execution.

Attributes:
    model: T: An instance of the generic type bound to `model.Model`, representing the state machine model.


Note: Documentation automatically generated by https://undoc.ai
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


class Null(asyncio.Future):
    """
    A class representing a Future that is immediately set to None upon initialization.
        This class is a derivative of asyncio.Future class used in asynchronous programming within the asyncio framework.
        The class overrides the default behaviour by immediately setting its result to None when an instance is created. It provides a convenient way to represent an already-resolved Future that has no value.
        Attributes:
            Inherits all attributes from asyncio.Future.
        Methods:
            Inherits all methods from asyncio.Future.
    """
    def __init__(self):
        """
            Initialize the instance.
            This method sets up the instance by calling the super class's initialization method
            and then setting the result attribute to None.
            Attributes:
                None
            Args:
                None
            Returns:
                None
        """
        super().__init__()
        self.set_result(None)


NULL = Null()


class InterpreterStep(Enum):
    """
    An enumeration to represent the possible states of an interpreter step.
        This class is a subclass of Enum and provides three states that an interpreter step can be in:
        - complete: Indicates that the interpreter step has been fully processed.
        - incomplete: Indicates that the interpreter step is not yet fully processed.
        - deferred: Indicates that the interpreter step has been put off for later processing or consideration.
        Attributes:
            complete (str): The string value 'complete' representing a finished interpreter step.
            incomplete (str): The string value 'incomplete' for a step that has not been completed.
            deferred (str): The string value 'deferred' for a step that has been postponed.
        The members of the enum can be directly used for comparisons and status checks within interpreter logic to ascertain the progress and handling of each interpreter step.
    """
    complete = "complete"
    incomplete = "incomplete"
    deferred = "deferred"


class AsyncInterpreter(model.Element, typing.Generic[T]):
    """
    An asynchronous interpreter that manages event processing for state machine execution.
    This class is responsible for starting, managing the event queue, tracking running tasks, and gracefully terminating the event loop. It provides methods to send events, start the interpreter, wait for tasks, perform a single event processing step, check activity status, push elements onto a stack, pop elements with optional result assignment, and terminate the event loop and all associated tasks.
    Attributes:
        queue (Queue): An instance of a queue used to manage incoming events.
        clock (Clock): An object to control timing-related operations.
        stack (dict[model.Element, asyncio.Future]): A mapping to keep track of currently active elements and their associated futures.
        loop (asyncio.AbstractEventLoop): The event loop where all asynchronous operations will be executed.
        log (logging.Logger): Logger instance to output debug messages.
        running (asyncio.Event): An event indicating whether the interpreter is currently running.
    Type Parameters:
        T: The type of the model the interpreter operates on.
    Constructor Args:
        queue (Queue): The queue for event management.
        log (Optional[logging.Logger]): A logger instance. If None, the default logger is used.
    Methods:
        send: Enqueue an event, return a future that completes when the event is processed.
        start: Start the event loop and internal tasks.
        wait: Wait on one or more async tasks or futures.
        run: The main loop of the interpreter, processing events as long as it is active.
        step: Process a single event from the queue.
        is_active: Check if the given elements are active in the interpreter.
        push: Add an element to the stack with an associated future or task.
        pop: Remove an element from the stack, handling future results or exceptions.
        terminate: Stop processing events, clear running state, and cancel the main task.
    """
    queue: Queue = None
    clock: Clock
    stack: dict[model.Element, asyncio.Future] = None
    loop: asyncio.AbstractEventLoop = None
    log: logging.Logger = logging.getLogger(__name__)
    running: asyncio.Event = None

    def __init__(self, queue: Queue, log: logging.Logger = None):
        """
            Initializes a new instance of the class.
            This method sets up the initial state by assigning the provided queue to an instance variable and creating an asyncio Event instance for managing the running state. It also initializes an empty dictionary for the stack and sets up logging, using the provided Logger if given, or the class's own logging mechanism otherwise.
            Args:
                queue (Queue): An instance of Queue that will be used to manage tasks or messages for the instance.
                log (logging.Logger, optional): A logging.Logger instance to handle logging. If not provided, the instance will use its default logging mechanism.
        """
        self.stack = {}
        self.queue = queue
        self.running = asyncio.Event()
        self.log = log or self.log

    def send(self, event: model.Element):
        """
        Sends an event to the internal queue to be processed asynchronously.
         Args:
           event (model.Element): The event object that needs to be sent.
         Returns:
           The result of awaiting on the event's future in the context of the current stack.
         This method performs several operations:
           1. Logs the receipt of the event using its qualified name for debugging purposes.
           2. Pushes the event onto an internal stack and associates it with an asyncio Future.
           3. Inserts the event into the queue for asynchronous processing.
           4. Awaits on the Future representing the outcome of the event processing,
              and returns the result once the processing completes.
         The method leverages asyncio's concurrency mechanisms to ensure that
         the event handling is performed asynchronously and doesn't block
         the execution of the program.
        """
        self.log.debug(f"Received {model.qualified_name_of(event)}")
        # push the event onto the stack
        future = self.push(event, asyncio.Future())
        # add the event to the queue
        self.queue.put_nowait(event)
        return self.wait(
            future,
            self.stack.get(self),
            name=f"{model.qualified_name_of(event)}.sent",
        )

    def start(
        self,
        loop: asyncio.AbstractEventLoop = None,
    ):
        """
            Initiates the state machine's run process asynchronously.
            This method starts the execution of the state machine by invoking its run method
            within an async event loop. If the loop is not provided, it fetches the current event loop.
            It logs the start operation, creates the associated task, sets up a synchronization
            primitive to wait for the state machine to signal it's running, and tracks the task in a stack.
            Parameters:
                loop (asyncio.AbstractEventLoop, optional): The event loop in which the run task
                    should be scheduled. If not provided, the current event loop is used.
            Returns:
                asyncio.Future: A future that can be awaited to wait for the state machine to
                    start running as well as the run task to be executed.
        """
        qualified_name = model.qualified_name_of(self)
        self.log.debug(f"Starting {qualified_name}")
        loop = self.loop = loop or asyncio.get_event_loop()
        task = loop.create_task(self.run(), name=qualified_name)
        started_task = self.loop.create_task(self.running.wait())
        self.push(self, task)
        return self.wait(task, started_task)

    def wait(
        self,
        *tasks: typing.Union[asyncio.Task, asyncio.Future],
        name: str = None,
        return_when: str = asyncio.FIRST_COMPLETED,
    ) -> asyncio.Task:
        """
        Wait for completion of given tasks or futures.
            This method creates an asyncio.Task that will complete when the specified condition defined by `return_when` is met for the provided `tasks`. By default, it will complete when the first task or future is completed.
            Args:
                *tasks (Union[asyncio.Task, asyncio.Future]): A variable number of asyncio tasks or futures to wait for.
                name (str, optional): The name to assign to the internally created asyncio.Task object. If not provided, a name is generated by concatenating the names of the input tasks with '_and_'.
                return_when (str, optional): The condition that determines when the wait operation is complete. This corresponds to the constants defined in `asyncio`. The default is 'asyncio.FIRST_COMPLETED', which means the function returns when any task is done.
            Returns:
                asyncio.Task: An instance of `asyncio.Task` that represents the operation of waiting for the specified tasks or futures to complete.
        """
        async def wait_for_tasks(_tasks=tasks, _return_when=return_when):
            """
            Async function that waits for the completion of a list of task objects.
                This function takes in an iterable of asyncio.Task objects and an optional parameter that determines the behavior of the wait operation.
                It waits for all the tasks to complete or for the condition specified by '_return_when' to be met. It then returns the result of one of the finished tasks.
                Args:
                    _tasks (Iterable[asyncio.Task]): An iterable of asyncio.Task objects to wait on.
                    _return_when (Any): An optional parameter that dictates when the function should return. It can be one of:
                        - FIRST_COMPLETED
                        - FIRST_EXCEPTION
                        - ALL_COMPLETED
                        The default is ALL_COMPLETED if not specified.
                Returns:
                    Any: The result of one completed task from the set of tasks that were waited on.
                Raises:
                    asyncio.InvalidStateError: If none of the tasks are finished and pop() is called on an empty set.
            """
            done, pending = await asyncio.wait(_tasks, return_when=_return_when)
            return await done.pop()

        return self.loop.create_task(
            wait_for_tasks(),
            name=name or "_and_".join(task.get_name() for task in tasks),
        )

    async def run(self) -> None:
        """
            Asynchronously run the task with the specified clock multiplier.
            This coroutine will enter a loop that continues to run as long as its `running` event is set. Inside
            the loop, it calls `step()` once per interval defined by the `clock.multiplier`. If the coroutine
            is cancelled, it catches the `asyncio.CancelledError` to log a debug message before exiting.
            If the `running` event is still set after the loop exits, the coroutine will ensure to call `terminate()`
            to properly shut down the task.
            Raises:
                asyncio.CancelledError: If the task execution is cancelled by an external event.
        """
        self.log.debug(
            f"Running {model.qualified_name_of(self)} clock multiplier {self.clock.multiplier}"
        )
        self.running.set()
        try:
            while self.running.is_set():
                await self.step()
                await asyncio.sleep(self.clock.multiplier)
        except asyncio.CancelledError:
            self.log.debug(f"Cancelled {model.qualified_name_of(self)}")
        if self.running.is_set():
            await self.terminate()

    async def step(self) -> None:
        """
            Asynchronously performs a single step by iterating through stacked futures.
            This function iterates through all futures contained in the instance's stack and checks if any future has
            raised an exception. If an exception has occurred, it is raised, halting the stepping process.
            Raises:
                exception: The exception raised by a future if it has encountered an error.
            Returns:
                None: Indicates that the step was completed without raising an exception.
        """
        for future in self.stack.values():
            if exception := future.exception() is not None:
                raise exception

    def is_active(self, *elements: model.Element) -> bool:
        """
            Determines if all given elements are active in the stack.
            Checks each element provided as an argument to determine if all of them are present in
            the stack managed by the current instance. If every element given is found in the stack,
            the method returns True, otherwise it returns False.
            Args:
                elements (model.Element): A variable number of Element instances to be checked against
                    the stack.
            Returns:
                bool: True if all elements are in the stack, False otherwise.
        """
        return all(element in self.stack for element in elements)

    def push(
        self, element: model.Element, future: typing.Union[Future, asyncio.Task] = NULL
    ):
        """
        Adds an element to the stack, ensuring that it doesn't already exist.
        This method will add the specified element to the stack if it's not already present, otherwise, it will raise a ValueError.
        If the element is successfully added, a `future` is associated with it which may either be a `Future` or an `asyncio.Task`. If no `future` is provided, a default value will be set.
        Args:
            element (model.Element): The element to be pushed onto the stack.
            future (typing.Union[Future, asyncio.Task], optional): The future to associate with the element. Defaults to NULL.
        Returns:
            Future: The future associated with the element.
        Raises:
            ValueError: If the element is already present in the stack.
        """
        if element in self.stack:
            raise ValueError(
                f"element {model.qualified_name_of(element)} already exists"
            )
        future = self.stack.setdefault(element, future)
        return typing.cast(Future, future)

    def pop(self, element: model.Element, *, result: typing.Any = NULL):
        """
            Pops the future associated with a stack element, processes its result, and handles exceptions.
            This method removes the future corresponding to the specified element from the stack, checks if the future
            has already been completed, and if so, checks for exceptions that might have occurred during its execution.
            If an exception is raised, it will be rethrown here. Otherwise, if a result has been provided via the 'result'
            parameter, and the future has not been set with a result already, it will be set with the provided result.
            Args:
                element (model.Element): The stack element associated with the future that needs to be popped.
                result (typing.Any, optional): The result to be set for the future if it hasn't been set already. Defaults to NULL.
                    This is useful in cases where the future's result is determined externally and should be explicitly assigned.
            Returns:
                Future: The future associated with the stack element. This future may either have the result set as provided,
                    be left as is if it's already completed, or raise an exception if one occurred during its execution.
            Raises:
                future.result(): If the future encountered an exception during its execution, that exception is raised.
        """
        future = self.stack.pop(element, NULL)
        if future.done():
            if future.exception() is not None:
                raise future.result()
            elif result is not NULL:
                future.set_result(result)
        return typing.cast(Future, future)

    def terminate(self):
        """
        Terminates the current task associated with the object instance.
        This method first clears the running state for the object, indicating that
        the associated task is no longer running. It then retrieves and removes the
        current task from the task list using the `pop` method. Finally, it cancels
        the retrieved task to stop it from running.
        Returns:
            object: The task that was cancelled during the termination process.
        Raises:
            KeyError: If the task associated with the object instance is not found
                      within the task list, resulting from a call to `pop`.
        """
        self.running.clear()
        task = self.pop(self)
        task.cancel()
        return task

    model: T = None
