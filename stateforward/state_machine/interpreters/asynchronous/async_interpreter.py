"""

The `async_interpreter` module provides an asynchronous execution framework specifically designed for state-based systems, utilizing asynchronous I/O provided by Python's asyncio library. It is built upon the concept of interacting with different models, events, queues, and clocks within state-based systems. This module contains several key classes and components, each working together to execute sequences of operations in a non-blocking manner. Key components include `InterpreterStep`, `AsyncInterpreter`, and `Null`, as well as crucial controllable constructs such as `queue`, `clock`, `stack`, and `log`. The module defines the functioning of an asynchronous interpreter for state machine workflows, providing methods for event handling, concurrency management, and execution control. Notably, the `AsyncInterpreter` class inherits from `model.Element` and is parameterized to work with various model types, enriching its capability to interface with different state machine elements. This module is essential for scenarios where asynchronous event handling and state management are paramount, and it relies heavily on the asyncio event loop and future constructs for its operation.
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
    A placeholder class designed to represent a Future with no value.
    This class is a subclass of `asyncio.Future` and is intended for scenarios where a Future-like object is required, but no actual result is expected. Upon initialization, it immediately sets its own result to `None`.
    
    Attributes:
        None:
             This class does not have any public attributes besides those provided by its superclass.
    
    Methods:
        __init__:
             Constructs a new `Null` object and sets its result to `None`.
            The `Null` class does not have its own methods, but inherits all methods from `asyncio.Future`.

    """

    def __init__(self):
        """
        Initializes a new instance of the class.
        This constructor method sets up the initial state of the object by calling its superclass initializer and setting the result attribute to None.

        """
        super().__init__()
        self.set_result(None)


NULL = Null()


class InterpreterStep(Enum):
    """
    An enumeration to represent the status of an interpretation step.
    This class is an enumeration (Enum) which categorizes the state of an interpretation step into one of three possible statuses:
    
    Attributes:
        complete (str):
             A status indicating that the interpretation step is complete and no further action is required.
        incomplete (str):
             A status indicating that the interpretation step is not fully resolved and may require additional information or action.
        deferred (str):
             A status that denotes a delay in the completion or evaluation of the interpretation step, potentially awaiting external input or another event.

    """

    complete = "complete"
    incomplete = "incomplete"
    deferred = "deferred"


class AsyncInterpreter(model.Element, typing.Generic[T]):
    """
    An asynchronous interpreter designed to operate with the provided state machine.
    This interpreter runs within the asyncio event loop and handles asynchronous task management
    and event processing for the state machine. It manages a queue of events and a stack to
    maintain the state of in-flight operations.
    
    Attributes:
        queue (Queue):
             The queue for managing incoming events.
        clock (Clock):
             An object managing the clock speed for the interpreter's operations.
        stack (dict[model.Element, asyncio.Future]):
             A dictionary mapping state machine elements
            to their associated futures/tasks.
        loop (asyncio.AbstractEventLoop):
             The event loop in which this interpreter operates.
        log (logging.Logger):
             Logger for the interpreter to output its activity.
        running (asyncio.Event):
             An event signaling whether the interpreter is currently running.
        stepping (asyncio.Lock):
             A lock to ensure step execution is done atomically.
        model (T):
             A generic type parameter representing the state machine model.
    
    Methods:
        __init__(self, queue:
             Queue, log: logging.Logger=None):
            Initializes the AsyncInterpreter with a queue and an optional logger.
        send(self, event:
             model.Element):
            Sends an event to be processed by the state machine.
        start(self, loop:
             asyncio.AbstractEventLoop=None):
            Starts the interpreter within the given or default event loop.
        wait(self, *tasks:
             typing.Union[asyncio.Task, asyncio.Future],
        name:
             str=None, return_when: str=asyncio.FIRST_COMPLETED) -> asyncio.Task:
            Waits for the given tasks to complete, returning an asyncio.Task wrapping the wait operation.
        run(self) -> None:
            The coroutine that runs the main event processing loop of the interpreter.
        step(self) -> None:
            Processes the next set of tasks from the stack.
        is_active(self, *elements:
             model.Element) -> bool:
            Checks if the given elements are active within the current stack.
        push(self, element:
             model.Element,
        future:
             typing.Union[Future, asyncio.Task]=NULL):
            Pushes a new element and associated future/task onto the stack.
        pop(self, element:
             model.Element, *, result: typing.Any=NULL):
            Pops an element and its associated task from the stack, handling its result.
        terminate(self) -> asyncio.Task:
            Terminates the interpreter, cleaning up and cancelling tasks as necessary.

    """

    queue: Queue = None
    clock: Clock
    stack: dict[model.Element, asyncio.Future] = None
    loop: asyncio.AbstractEventLoop = None
    log: logging.Logger = logging.getLogger(__name__)
    running: asyncio.Event = None
    stepping: asyncio.Lock = None

    def __init__(self, queue: Queue, log: logging.Logger = None):
        """
        Initializes the instance with a queue, an optional log, and internal attributes.
        This method sets up the data structures and synchronization primitives required for the operation
        of an instance. It assigns the queue to the instance, initializes a stack as a dictionary,
        prepares an asyncio event to manage the running state, and sets up logging.
        
        Args:
            queue (Queue):
                 A queue object used for inter-thread or inter-process communication.
            log (logging.Logger, optional):
                 A logger instance for logging messages. If not provided, it falls back to a default logger.
        
        Attributes:
            stack (dict):
                 A dictionary to hold instance-specific data.
            queue (Queue):
                 The queue object passed during initialization.
            running (asyncio.Event):
                 An event to indicate whether the instance is running.
            log (logging.Logger):
                 A logger instance for outputting logs.

        """
        self.stack = {}
        self.queue = queue
        self.running = asyncio.Event()
        self.log = log or self.log

    def send(self, event: model.Element):
        """
        Sends an event to be processed by the state machine.
        This method logs the receipt of the event, pushes it to the stack along with a new Future object, adds the event to a queue, and then awaits the processing of the event. The method returns the result of waiting for the future associated with the event to be completed.
        
        Args:
            event (model.Element):
                 The event to be sent to the state machine for processing.
        
        Returns:

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
        Starts an asynchronous task to run the state machine in an event loop.
        This method initializes the event loop for the state machine, logs the state machine's qualified name,
        and then creates and starts an asynchronous task for the state machine's `run` method.
        It pushes the running task into a tracking structure for managing tasks and then waits for the
        initialization to complete before proceeding.
        
        Args:
            loop (asyncio.AbstractEventLoop, optional):
                 The event loop in which the state machine will
                be run. If not provided, the current event loop will be used.
        
        Returns:
            A `wait` wrapper that is used to wait for two events:
                 the task that runs the state machine
                to complete, and a separate task that signals the state machine is running.

        """
        qualified_name = model.qualified_name_of(self)
        self.log.debug(f"Starting {qualified_name}")
        loop = self.loop = loop or asyncio.get_event_loop()
        task = loop.create_task(self.run(), name=qualified_name)
        self.push(self, task)
        return self.wait(task, self.loop.create_task(self.running.wait()))

    def wait(
        self,
        *tasks: typing.Union[asyncio.Task, asyncio.Future],
        name: str = None,
        return_when: str = asyncio.FIRST_COMPLETED,
    ) -> asyncio.Task:
        """
        Waits for the completion of one or more asyncio.Task or asyncio.Future objects.
        This function is a coroutine that accepts any number of asyncio.Task or asyncio.Future
        objects and an optional name for the underlying task that will wait for the
        provided tasks or futures to complete. The function will schedule the execution
        of these tasks or futures on the event loop, and wait until the conditions specified
        by return_when are met. return_when can indicate waiting for the first task to
        complete (asyncio.FIRST_COMPLETED), all tasks to complete (asyncio.ALL_COMPLETED),
        or the first task to not be cancelled (asyncio.FIRST_EXCEPTION).
        Upon completing the wait condition, the function will return the task that was created
        to perform the wait operation. If any of the awaited tasks or futures raise an
        exception during execution, the exception will be propagated.
        
        Args:
            *tasks (Union[asyncio.Task, asyncio.Future]):
                 An arbitrary number of asyncio.Task
                or asyncio.Future objects to be awaited.
            name (str, optional):
                 An optional name for the asyncio.Task that will be created
                to perform the waiting operation. If not provided, a name is generated by
                concatenating the names of the tasks with '_and_'.
            return_when (str):
                 The condition that determines when the wait operation
                should return. Must be one of asyncio.FIRST_COMPLETED, asyncio.ALL_COMPLETED,
                or asyncio.FIRST_EXCEPTION.
        
        Returns:
            asyncio.Task:
                 The task that was created to wait for the provided tasks or futures.

        """

        async def wait_for_tasks(_tasks=tasks, _return_when=return_when):
            """
            Waits for the completion of tasks, possibly returning before all tasks are finished based on a condition.
            This function asynchronously waits for the `_tasks` iterable of tasks to reach a completion state, which is determined by the `_return_when` condition. Once the condition is met, it retrieves one of the completed tasks from `done` set. If that task raised an exception, the exception is propagated by awaiting on the task object.
            
            Args:
                _tasks (Iterable[Task]):
                     The collection of asyncio.Task objects to wait on. Defaults to the `tasks` variable in the current context.
                _return_when (str):
                     The condition upon which the function should return. This condition dictates whether the function waits for all tasks to complete, or returns earlier. Defaults to the `return_when` variable in the current context.
            
            Returns:
                Tuple[Set[Task], Set[Task]]:
                     A tuple containing two sets. The first set contains all tasks that are done, and the second set contains all tasks that are pending.
            
            Raises:
                Any exception raised by a task:
                     If any task among `_tasks` raises an exception, that exception is propagated.

            """
            done, pending = await asyncio.wait(_tasks, return_when=_return_when)
            task = done.pop()
            if task.exception() is not None:
                await task

        return self.loop.create_task(
            wait_for_tasks(),
            name=name or "_and_".join(task.get_name() for task in tasks),
        )

    async def run(self) -> None:
        """
        Asynchronously runs the process associated with the class instance.
        This coroutine continuously executes the 'step' method and awaits for a sleep interval based on the 'clock.multiplier'. It checks if the instance is active and if the 'running' flag is set before each iteration. If the 'running' flag is cancelled, it logs a debug message indicating the cancellation. If the 'running' flag is still set after an interruption, it ensures that the 'terminate' method is called.
        
        Raises:
            asyncio.CancelledError:
                 If the coroutine is cancelled during its execution.

        """
        self.log.debug(
            f"Running {model.qualified_name_of(self)} clock multiplier {self.clock.multiplier}"
        )
        if self.is_active(self):
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
        Performs an asynchronous iteration step over a collection of futures stored in an instance's stack.
        This method iterates through the values of the instance's stack attribute, which is expected to be a mapping of futures. It checks if any of the futures have raised an exception. If an exception is encountered in any future, it is immediately raised, halting the iteration.
        
        Raises:
            Exception:
                 Any exception raised by a future in the stack.
        
        Returns:

        """
        for future in self.stack.values():
            if exception := future.exception() is not None:
                raise exception

    def is_active(self, *elements: model.Element) -> bool:
        """
        Checks if all specified elements are active within the current context.
        This method determines if all elements provided as arguments exist in the context's active stack.
        
        Args:
            *elements (model.Element):
                 Variable number of elements to check for activeness within the stack.
        
        Returns:
            bool:
                 True if all specified elements are active (i.e., they exist in the stack); False otherwise.

        """
        return bool(self.stack) and all(element in self.stack for element in elements)

    def push(
        self, element: model.Element, future: typing.Union[Future, asyncio.Task] = NULL
    ):
        """
        Pushes an element onto the stack with an associated future or task, ensuring uniqueness.
        This method adds an element to an internal stack, associating it with a future or an asyncio task, which may represent the element's processing state.
        If the element already exists within the stack, a ValueError is thrown to avoid duplication.
        The method ensures that each element can have only one corresponding future or task.
        
        Args:
            element (model.Element):
                 The element to push onto the stack.
            future (typing.Union[Future, asyncio.Task], optional):
                 A future or task to associate with the element.
                If not provided, the default value defined by NULL will be used.
        
        Returns:
            Future:
                 The future or task associated with the element. This can be either the provided argument
                or the one already associated with the element in case of previously existing entry.
        
        Raises:
            ValueError:
                 If the element is already present in the stack.

        """
        if element in self.stack:
            raise ValueError(
                f"element {model.qualified_name_of(element)} already exists"
            )
        future = self.stack.setdefault(element, future)
        return typing.cast(Future, future)

    def pop(self, element: model.Element, *, result: typing.Any = NULL):
        """
        Pops an element from the stack and sets the result if specified.
        This method retrieves the future associated with a stack element, removes the element from the stack,
        and optionally sets a result on the future. If the future is already done and contains an exception,
        the exception is raised. If `result` is provided and not NULL, it is used to set the future's result.
        
        Args:
            element (model.Element):
                 The element to be popped from the stack.
            result (typing.Any, optional):
                 The result to set on the future if not NULL. Defaults to NULL.
        
        Returns:
            typing.cast(Future, future):
                 The future associated with the popped element.
        
        Raises:

        """
        future = self.stack.pop(element, NULL)
        if future.done():
            if future.exception() is not None:
                raise future.result()
            elif result is not NULL:
                future.set_result(result)
        return typing.cast(Future, future)

    def terminate(self) -> asyncio.Task:
        """
        Cancels the asynchronous task associated with the current instance if it is still running.
        This method checks if the `running` attribute, presumably an instance of `threading.Event` or similar,
        is set. If it is, it clears the `running` attribute to stop the task. It then retrieves the current
        task using a `pop` method and inspects it. If the task is not yet completed, it will attempt
        to cancel it by calling its `cancel` method. The task object, now potentially canceled, is
        then recast as an `asyncio.Task` and returned.
        
        Returns:
            asyncio.Task:
                 The task associated with this instance after attempting to cancel it if necessary.

        """
        if self.running.is_set():
            self.running.clear()
        task = self.pop(self)
        if not task.done():
            task.cancel()
        return typing.cast(asyncio.Task, task)

    model: T = None
