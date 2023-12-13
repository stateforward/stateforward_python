import typing
from datetime import datetime


class Clock(typing.Protocol):
    multiplier: float = 0.001  # 1ms

    def now(self) -> datetime:
        ...
