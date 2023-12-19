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
    def __init__(self):
        super().__init__()
        self.set_result(None)


NULL = Null()


class InterpreterStep(Enum):
    complete = "complete"
    incomplete = "incomplete"
    deferred = "deferred"


class Interpreter(model.Element, typing.Generic[T]):
    queue: Queue = None
    clock: Clock
    stack: dict[model.Element, asyncio.Future] = None
    loop: asyncio.AbstractEventLoop = None
    log: logging.Logger = logging.getLogger(__name__)
    running: asyncio.Event = None

    def __init__(self, queue: Queue, log: logging.Logger = None):
        self.stack = {}
        self.queue = queue
        self.running = asyncio.Event()
        self.log = log or self.log

    def send(self, event: model.Element):
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
        async def wait_for_tasks(_tasks=tasks, _return_when=return_when):
            done, pending = await asyncio.wait(_tasks, return_when=_return_when)
            return await done.pop()

        return self.loop.create_task(
            wait_for_tasks(),
            name=name or "_and_".join(task.get_name() for task in tasks),
        )

    async def run(self) -> None:
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
        pass

    def is_active(self, *elements: model.Element) -> bool:
        return all(element in self.stack for element in elements)

    def push(
        self, element: model.Element, future: typing.Union[Future, asyncio.Task] = NULL
    ):
        if element in self.stack:
            raise ValueError(
                f"element {model.qualified_name_of(element)} already exists"
            )
        future = self.stack.setdefault(element, future)
        return typing.cast(Future, future)

    def pop(self, element: model.Element, *, result: typing.Any = NULL):
        future = self.stack.pop(element, Null())
        if result is not NULL and not future.done():
            future.set_result(result)
        return typing.cast(Future, future)

    def terminate(self):
        self.running.clear()
        task = self.pop(self)
        task.cancel()
        return task

    model: T = None
