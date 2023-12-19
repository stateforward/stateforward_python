from stateforward import elements, model
import typing
import asyncio

from stateforward.state_machine.log import create_logger, Logger
from stateforward.state_machine.clocks import Clock
from stateforward.protocols import Queue


class AsyncBehaviorInterpreter(model.Interpreter, clock=Clock):
    deferred: list[elements.Event] = None

    def __init__(self, queue: Queue = None, log: Logger = None):
        super().__init__(
            queue=queue or asyncio.Queue(),
            log=log or create_logger(model.qualified_name_of(self)),
        )
        self.deferred = []

    async def step(self):
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
                    if results is model.InterpreterStep.deferred:
                        deferred.append(event)
                    else:
                        if model.owner_of(event) is None:
                            stack.append((self.pop(event), results))
                        if results is model.InterpreterStep.complete:
                            processed = []
                            break
                    processed.append(event)
                continue
            break
        self.deferred = deferred
        for future, results in stack:
            future.set_result(results)

    async def exec_behavior(
        self, behavior: elements.Behavior, event: typing.Optional[elements.Event]
    ):
        behavior_name = model.qualified_name_of(behavior)
        self.log.debug(f"Executing {behavior_name}")
        value = behavior.activity(event)
        if asyncio.isfuture(value) or asyncio.iscoroutine(value):
            value = await value
        return value

    async def exec_event_processing(
        self, event: elements.Event
    ) -> model.InterpreterStep:
        pass
