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
    complete = "complete"
    incomplete = "incomplete"
    deferred = "deferred"


class Interpreter(typing.Protocol[T]):
    queue: Queue
    clock: Clock
    stack: dict[model.Element, Future]
    log: logging.Logger

    def __init__(self, queue: Queue, log: logging.Logger = None):
        ...

    def send(self, event: model.Element) -> Future:
        ...

    def start(
        self,
        loop: asyncio.AbstractEventLoop = None,
    ):
        ...

    def wait(
        self,
        *tasks: typing.Union[asyncio.Task, asyncio.Future],
        name: str = None,
        return_when: str = asyncio.FIRST_COMPLETED,
    ) -> asyncio.Task:
        ...

    async def run(self) -> None:
        ...

    async def step(self) -> None:
        pass

    def is_active(self, *elements: model.Element) -> bool:
        return all(element in self.stack for element in elements)

    def push(self, element: model.Element, future: typing.Union[Future, asyncio.Task]):
        ...

    def pop(self, element: model.Element, result: typing.Any):
        ...

    def terminate(self):
        ...

    model: T = None
