import typing

T = typing.TypeVar("T", bound=typing.Any)


class Queue(typing.Protocol[T]):
    def task_done(self) -> None:
        ...

    def join(self) -> None:
        ...

    def qsize(self) -> int:
        ...

    def empty(self) -> bool:
        ...

    def full(self) -> bool:
        ...

    def put(
        self,
        item: T,
        block: typing.Optional[bool] = True,
        timeout: typing.Optional[float] = None,
    ) -> None:
        ...

    def get(
        self,
        block: typing.Optional[bool] = True,
        timeout: typing.Optional[float] = None,
    ) -> T:
        ...

    def put_nowait(self, item) -> None:
        ...

    def get_nowait(self) -> T:
        ...
