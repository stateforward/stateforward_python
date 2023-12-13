import typing
import asyncio
from concurrent import futures

T = typing.TypeVar("T")
asyncio.Future


class Future(typing.Protocol[T]):
    remove_done_callback: typing.Optional[
        typing.Callable[[typing.Callable[["Future"], None]], None]
    ]

    def cancel(self) -> bool:
        ...

    def cancelled(self) -> bool:
        ...

    def running(self) -> bool:
        ...

    def done(self) -> bool:
        ...

    def add_done_callback(self, callback: typing.Callable[["Future"], None]):
        ...

    def result(self, timeout: typing.Optional[float] = None) -> T:
        ...

    def exception(self, timeout: typing.Optional[float] = None):
        ...

    def set_result(self, result: T):
        ...

    def set_exception(self, exception: Exception):
        ...

    def __await__(self, *args, **kwargs):
        ...

    @staticmethod
    def results(value: T) -> "Future":
        if asyncio.isfuture(value) or isinstance(value, futures.Future):
            return typing.cast(Future, value)
        future = futures.Future()
        future.set_result(value)
        return typing.cast(Future, future)


if __name__ == "__main__":
    foo = Future.results(1)
    print(foo.result())
