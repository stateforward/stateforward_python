from stateforward.model import element
from datetime import datetime, timedelta
import typing


class Clock(element.Element):
    multiplier: float = 0.001  # multiplier for the interval in seconds defaults to 1ms
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
