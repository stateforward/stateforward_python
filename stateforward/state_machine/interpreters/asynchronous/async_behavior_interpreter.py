"""

The `async_behavior_interpreter` module is designed to provide an asynchronous interpreter for state machines, specifically tailored for handling behaviors encoded into event-driven systems. It extends functionality from a base `AsyncInterpreter`, and is meant to work within a broader framework that manages state transitions and event processing called `stateforward`. This interpreter deals with asynchronous event queues and utilizes Python's `asyncio` library to manage concurrent execution of behaviors associated with state machine events.

The primary class provided by this module is `AsyncBehaviorInterpreter`, which inherits from the `AsyncInterpreter` class and introduces additional mechanisms to manage deferred events within the state machine's execution flow. Events are accumulated from various sources such as the internal model pool, an asynchronous queue, and a deferred list, ensuring that all events are processed in an ordered and non-repetitive fashion.

The `AsyncBehaviorInterpreter` class introduces two key asynchronous methods: `step` and `exec_event_processing`. The `step` method orchestrates the processing of events by maintaining a stack for event execution, processing events from the queue, checking for deferred events, and tirelessly fetching events until all have been handled. The `exec_event_processing` method, which is to be implemented, is responsible for handling the processing logic for each event encountered.

The `AsyncBehaviorInterpreter` also provides a synchronous method `compile` meant to be overridden by subclasses as a classmethod. This method's role is typically to compile or prepare the state machine for execution, though it is abstract in the context of the provided schema.

Additional utility methods such as `exec_behavior` facilitate the execution of behaviors associated with events, handling both synchronous and asynchronous operations seamlessly.

The module is robust in its logging capabilities, ensuring that event processing is transparent and debuggable. A `Logger` interface is expected for this purpose, and a default logger is created if none is provided upon instantiation of the interpreter.

The module leverages `asyncio` for handling concurrency and asynchronous operations, and incorporates custom abstractions such as `StateMachine`, `Clock`, `Queue`, and `Logger` provided by the `stateforward` framework. It is a key component within the framework for implementing asynchronous behavior-driven state machines.
"""
from stateforward import core, model
import typing
import asyncio

from stateforward.state_machine.log import create_logger
from stateforward.protocols.logger import Logger
from stateforward.protocols.interpreter import InterpreterStep
from stateforward.state_machine.clocks import Clock
from stateforward.protocols import Queue
from stateforward.state_machine.interpreters.asynchronous.async_interpreter import (
    AsyncInterpreter,
)


class AsyncBehaviorInterpreter(AsyncInterpreter, clock=Clock):
    """
    A class to interpret and manage asynchronous behaviors within an event-driven system. It utilizes a queue to process events and can defer processing of some events to a subsequent cycle.
    
    Attributes:
        deferred (list[core.Event]):
             A list to keep track of events that are deferred during processing.
        Inherits:
        AsyncInterpreter:
             Base class that provides the asynchronous event interpretation framework.
        Clock:
             (Inherited via AsyncInterpreter) Represents a time-keeping component.
    
    Methods:
        __init__(self, queue:
             Queue=None, log: Logger=None):
            Initializes the AsyncBehaviorInterpreter instance.
    
    Args:
        queue (Queue, optional):
             An asyncio Queue instance used to manage the event queue. Defaults to None, where an asyncio.Queue() will be created.
        log (Logger, optional):
             Logger instance for logging/debugging. Defaults to None, where a new logger is created based on the model's qualified name.
        step(self):
            Processes events in the queue, executing behaviors associated with each event and supporting deferral of events.
            Events are deduplicated and processed in order until the queue is emptied or all events are deferred. Results are collected and any completions are handled.
    
    Returns:
        exec_behavior(self, behavior:
             core.Behavior, event: typing.Optional[core.Event]):
            Executes the specified behavior with the associated event.
    
    Args:
        behavior (core.Behavior):
             The behavior object to execute.
        event (typing.Optional[core.Event]):
             The event related to the behavior, if any.
    
    Returns:
        exec_event_processing(self, event:
             core.Event) -> InterpreterStep:
            Method stub for processing an individual event.
    
    Args:
        event (core.Event):
             The event to be processed.
    
    Returns:
        InterpreterStep:
             The outcome of processing the event, indicating if the event is complete, pending, or deferred.

    """

    deferred: list[core.Event] = None

    def __init__(self, queue: Queue = None, log: Logger = None):
        """
        __init__(self, queue: Queue=None, log: Logger=None)
        Initializes a new instance of the enclosing class with optional queue and log parameters.
        This method sets up the class instance with a specified or default asynchronous queue and logging system. If no queue is provided, an asyncio Queue instance is created. If no logger is provided, a new logger is created based on the qualified name of the class instance via the create_logger function. The method also initializes a list to keep track of deferred tasks.
        
        Args:
            queue (Queue, optional):
                 An instance of a queue for task management. Defaults to None, in which case a new asyncio Queue is created.
            log (Logger, optional):
                 A logging instance to log messages and errors. Defaults to None, in which case a new logger is created based on the qualified name of the class instance.
        
        Attributes:
            deferred (List):
                 A list to store deferred tasks or activities that should be executed later.

        """
        super().__init__(
            queue=queue or asyncio.Queue(),
            log=log or create_logger(model.qualified_name_of(self)),
        )
        self.deferred = []

    async def step(self):
        """
        Performs a single step in the event processing cycle of the current state machine asynchronously.
        This async method processes events that are pending in the machine's queue, handling each event according to the state machine's logic. During the step, it ensures that each event is either processed completely or deferred for later processing. The state machine evaluates events from its internal queue, deferred events from the previous step, and new events that arrive during the cycle. Duplicate events are filtered out, ensuring that each unique event is processed only once per iteration. Processed events are logged for debugging purposes, and any events that are determined to be owned by no one are stacked for result assignment. If an event signals the completion of the processing cycle, the method will clear the list of processed events and break out of the loop for the current step.
        The method uses an internal while loop that runs as long as there are events to process. Events that have already been processed are skipped in subsequent iterations. Once all events are processed, the loop will end, updating the deferred list with any events that were not processed and need to be revisited in the next step. The method concludes by setting the result for any futures in the stack that have been processed, thus completing the step.
        
        Note that this method should be used within the context of an async function or coroutine due to its asynchronous nature.
        
        Returns:
            None:
                 This method does not return a value, as its purpose is to update the state machine's
                internal state based on event processing.

        """
        processed = []
        events = []
        deferred = self.deferred
        stack = []
        while events := list(
            dict.fromkeys(
                (
                    # include active events in the event pool
                    *(event for event in self.model.pool if event in self.stack),
                    # include deferred events from the previous iteration
                    *deferred,
                    # include events from the previous iteration
                    *events,
                    # include events from the queue
                    *(self.queue.get_nowait() for _ in range(self.queue.qsize())),
                )
            )
        ):
            # reset deferred events
            deferred = []
            # if all events have been processed this iteration is complete
            if not all(event in processed for event in events):
                # clear the idle flag to prevent interruptions
                while events:
                    # pop the first event from the list
                    event = events.pop(0)
                    results = await self.exec_event_processing(event)
                    self.log.debug(
                        f"Processed {model.qualified_name_of(event)} results {results} and {processed}"
                    )
                    # add the event to the list of processed events
                    if results is InterpreterStep.deferred:
                        deferred.append(event)
                    else:
                        if model.owner_of(event) is None:
                            stack.append((self.pop(event), results))
                        if results is InterpreterStep.complete:
                            processed = []
                            break
                    processed.append(event)
                continue
            break
        self.deferred = deferred
        for future, results in stack:
            future.set_result(results)

    async def exec_behavior(
        self, behavior: core.Behavior, event: typing.Optional[core.Event]
    ):
        """
        Asynchronously executes a behavior in response to an event.
        This function takes a behavior object and optionally an event object. It begins by logging the execution
        of the behavior using its qualified name. Afterwards, it executes the activity associated with the behavior,
        potentially waiting for the result if the activity is async (a future or coroutine). Finally, it returns the result of the behavior's activity.
        
        Args:
            behavior (core.Behavior):
                 The behavior object to execute.
            event (typing.Optional[core.Event]):
                 The event that triggers the execution of the behavior, if any.
        
        Returns:

        """
        behavior_name = model.qualified_name_of(behavior)
        self.log.debug(f"Executing {behavior_name}")
        value = behavior.activity(event)
        if asyncio.isfuture(value) or asyncio.iscoroutine(value):
            value = await value
        return value

    async def exec_event_processing(self, event: core.Event) -> InterpreterStep:
        """
        Processes a given event asynchronously within the system's event processing pipeline.
        This function serves as an asynchronous handler, tasked with interpreting and processing an event object. It forms an integral part of the event-driven architecture and is expected to be invoked with an event instance that it shall interpret, potentially yielding changes in system behavior or state as a result. Upon successful execution, it returns an instance of InterpreterStep, which encapsulates the outcome of processing the event.
        
        Args:
            event (core.Event):
                 An event instance that contains data and information to be processed by the system.
        
        Returns:
            InterpreterStep:
                 An object representing the result of the event processing. It includes information about what actions should be taken next within the system based on the interpretation of the event.
        
        Raises:
            Exception:
                 If the event processing fails or encounters an unexpected error, an exception may be thrown indicating the nature of the failure.

        """
        pass
