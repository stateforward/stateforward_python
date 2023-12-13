from stateforward.model import element
from datetime import datetime, timedelta, time
import typing
from enum import Enum


class Clock(element.Element):
    multiplier: float = 1.0  # multiplier for the interval in seconds
    start_time: typing.Union[datetime, None] = None

    def __init__(
        self, start_time: typing.Optional[datetime] = None, scale: float = None
    ):
        self.start_time = start_time or datetime.utcnow()
        self.multiplier = scale or self.multiplier

    def now(self) -> datetime:
        if self.start_time is None:
            return datetime.utcnow()
        return self.start_time + timedelta(
            seconds=(datetime.utcnow() - self.start_time).total_seconds()
            * self.multiplier
        )
