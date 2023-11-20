from stateforward import elements, model
from typing import Any, Union, TypeVar, Coroutine
import asyncio
from stateforward.state_machine.log import log


T = TypeVar("T")


NULL = type("NULL", (object,), {})()


class AsyncBehaviorInterpreter(model.Interpreter[asyncio.Future], queue=asyncio.Queue):
    loop: asyncio.AbstractEventLoop
    idle: asyncio.Event
    tasks: dict[model.Element, asyncio.Future]
    log: log

    def __init__(self):
        super().__init__()
        self.idle = asyncio.Event()
        self.idle.set()
        self.deferred = []
        self.log = log.getLogger(self.qualified_name)

    def dispatch(self, event: elements.Event):
        self.log.debug(f"Dispatching {event.qualified_name}")
        # clear the idle flag
        self.idle.clear()
        # put the event in the queue
        self.queue.put_nowait(event)
        return self.loop.create_task(self.idle.wait(), name="dispatching")

    def start(
        self,
    ) -> asyncio.Task:
        if self not in self.active:
            self.log.debug(f"starting")
            self.idle.clear()
            self.loop = asyncio.get_running_loop()
            run = self.loop.create_task(
                self.run(self.model), name=f"{self.model.qualified_name}.run"
            )
            self.add_active(self, run)
        return self.loop.create_task(self.idle.wait(), name="idle")

    async def run(self, behavior):
        try:
            await self.process()
        except asyncio.CancelledError as exception:
            pass
        except Exception as exception:
            raise exception

    async def terminate(self):
        self.remove_active(self)

    def add_active(
        self, element: Union[model.Element, model.Collection], value: Any = NULL
    ) -> Any:
        if not asyncio.isfuture(value):
            future = self.loop.create_future()
            future.set_result(value)
        else:
            future = value
        self.active[element] = future
        return future

    def remove_active(
        self,
        element: Union[model.Element, model.Collection],
        results: Any = NULL,
    ):
        active = self.active.pop(element, None)
        if active is None:
            return
        elif not active.done():
            if results is not NULL:
                active.set_result(results)
            else:
                active.cancel()
        elif active.exception():
            raise active.exception()

    def get_active(self, element: model.Element) -> Any:
        if element in self.active:
            return self.active.get(element)
        future = self.loop.create_future()
        future.set_result(NULL)
        return future

    def is_active(self, *element: Union[str, model.Element]):
        return all(_element in self.active for _element in element)

    async def process(self):
        while self.active:
            await self.process_events()
            await asyncio.sleep(0)

    async def process_events(self):
        self.idle.clear()
        processed = []
        events = []
        deferred = self.deferred[:]
        while events := list(
            dict.fromkeys(
                (
                    # include active events in the event pool
                    *(event for event in self.model.pool if event in self.active),
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
                    results = await self.process_event(event)
                    # add the event to the list of processed events
                    if results is model.Processing.complete:
                        processed = []
                        break
                    elif results is model.Processing.deferred:
                        deferred.append(event)
                    processed.append(event)
                continue
            break
        self.deferred = deferred
        self.idle.set()

    async def step(self):
        pass

    def raise_exception(self, exception: Exception):
        raise exception

    def execute_behavior(self, behavior: elements.Behavior, event: elements.Event):
        if behavior is not None and behavior.activity is not None:

            async def execute(_self=self, _behavior=behavior, _event=event):
                value = _behavior.activity(_event)
                if asyncio.iscoroutine(value):
                    try:
                        value = await value
                    except asyncio.CancelledError as e:
                        raise e
                return value

            task = self.add_active(
                behavior,
                self.loop.create_task(execute(), name=behavior.name),
            )
            task.add_done_callback(lambda _: self.remove_active(behavior))
            return task
        return self.loop.create_task(asyncio.sleep(0), name="no_op")

    async def process_event(self, event: elements.Event):
        pass
