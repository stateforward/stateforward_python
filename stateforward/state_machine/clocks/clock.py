"""

The `clock` module provides the `Clock` class which extends from the `element.Element` base class. It is designed to manage time in a flexible manner, allowing the simulation or manipulation of the time progression through a scale multiplier.

The `Clock` class contains two main attributes:
- `multiplier`: A float that represents the scale by which the actual time interval is multiplied. By default, it is set to `0.001`, which means that time is scaled to milliseconds. This can be changed upon initialization or later during the execution of the program.
- `start_time`: A `datetime` object that marks the starting point of the clock. If not specified during instantiation, it defaults to the current UTC time.

The class provides an initializer (`__init__`) which takes two optional parameters:
- `start_time`: A `datetime` object to set the starting time of the clock. If not provided, it uses the current UTC time.
- `scale`: A float that sets the multiplier for the interval. It defaults to the existing class attribute `multiplier` if not provided.

The `Clock` class also includes a method `now` that returns the current time. This time is calculated based on the `start_time` and adjusted by the `multiplier` to simulate different time progressions (faster or slower). If `start_time` is `None`, the method simply returns the current UTC time.

Additionally, the module contains a `compile` class method annotated with `@classmethod` within a comment block, but its implementation is omitted from the documentation as it does not pertain directly to the `Clock` class's functionality.
"""
from stateforward.model import element
from datetime import datetime, timedelta
import typing


class Clock(element.Element):
    """
    A class representing a scalable clock which can simulate the passage of time at different speeds.
    
    Attributes:
        multiplier (float):
             A scaling factor for the time interval, where by default 1 millisecond (0.001)
            is used as a scaling unit.
        start_time (Union[datetime, None]):
             The reference start time from which the clock begins, or None
            if it uses the current UTC time when an object is initialized.
    
    Methods:
        __init__(self, start_time:
             Optional[datetime]=None, scale: float=None):
            Initializes the Clock instance with a start_time and a given scaling factor.
            If no start_time is provided, the current UTC time is used. If no scaling factor
            is provided, the default multiplier is used.
        now(self) -> datetime:
            Retrieves the current time according to the clock's scaling factor and the time elapsed
            since the start_time. If start_time was not set, it returns the current UTC time.

    """
    multiplier: float = 0.001  # multiplier for the interval in seconds defaults to 1ms
    start_time: typing.Union[datetime, None] = None

    def __init__(
        self, start_time: typing.Optional[datetime] = None, scale: float = None
    ):
        """
        Initializes a new instance of the class.
        This constructor sets up the instance with an optional start time and scale. If no start time is provided, the current UTC time is used. Similarly, if no scale value is provided, the default scale defined in the class instance is used.
        
        Args:
            start_time (Optional[datetime], optional):
                 The start time for the instance. Defaults to None, in which case the current UTC time is used.
            scale (float, optional):
                 A multiplier value for scaling. Defaults to None, in which the default class scale value is used.

        """
        self.start_time = start_time or datetime.utcnow()
        self.multiplier = scale or self.multiplier

    def now(self) -> datetime:
        """
        Calculates the adjusted current time for an instance based on its start time and a time multiplier.
        This method determines the 'current' time for the object by either returning the real current UTC time if the object's
        start time is not set, or by calculating the time that has passed since the object's start time, adjusting it with
        the specified multiplier, and then adding this adjusted duration to the start time.
        
        Returns:
            datetime:
                 The adjusted current time for the instance if the start time is set, otherwise the real current UTC time.

        """
        if self.start_time is None:
            return datetime.utcnow()
        return self.start_time + timedelta(
            seconds=(datetime.utcnow() - self.start_time).total_seconds()
            * self.multiplier
        )
