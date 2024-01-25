"""

A module for managing time within a simulation or an application that requires time manipulation.

This module defines a `Clock` class that inherits from `element.Element`. It provides functionality to get the current time considering a potentially modified scaling factor, allowing for the simulation of time at different speeds.

Attributes:
    multiplier (float): A scaling factor for the clock that determines how quickly the simulated time progresses relative to the real-world time. A multiplier of 1.0 means time progresses at the normal rate. The default value is 1 millisecond (0.001).
    start_time (Union[datetime, None]): The start time from which the clock begins. If `None`, the clock will use the current UTC time. This value is set during the initialization of the `Clock` instance.

Methods:
    __init__(self, start_time: Optional[datetime]=None, scale: float=None):
        Initializes a new instance of the `Clock` class with an optional start time and an optional scaling factor.
        Args:
            start_time (Optional[datetime]): The UTC datetime representing when the `Clock` should start. If not provided, the current UTC time is used.
            scale (float): The time scaling factor to apply. If not provided, the default multiplier is used.

    now(self) -> datetime:
        Retrieves the current simulated time of the `Clock` instance. If the start time is not defined, the current UTC time is returned. Otherwise, it calculates the simulated time taking the multiplier into account.
        Returns:
            datetime: The current simulated time or the current UTC time if the start time is not set.

Note: Documentation automatically generated by https://undoc.ai
"""
from stateforward.model import element
from datetime import datetime, timedelta
import typing


class Clock(element.Element):
    """
    A class that represents a clock with an adjustable time speed.
        This clock allows setting a start time and a multiplier for the speed of time. The multiplier affects the rate at which the clock's time advances relative to the real time. The default multiplier makes the clock's time advance 1,000 times faster than real time. If no start time is provided upon initialization, the current UTC time is used.
        Attributes:
            multiplier (float): The multiplier for the clock's time speed compared to real time. Defaults to 0.001 (1 millisecond).
            start_time (Union[datetime, None]): The start time for the clock. Defaults to None, which results in the current UTC time being used at initialization.
        Methods:
            now(): Returns the current time as per the clock's configured speed and start time.
        Note:
            The 'now' method returns the current time as per the clock's setting, which is the start_time adjusted by the elapsed time multiplied by the multiplier.
    """
    multiplier: float = 0.001  # multiplier for the interval in seconds defaults to 1ms
    start_time: typing.Union[datetime, None] = None

    def __init__(
        self, start_time: typing.Optional[datetime] = None, scale: float = None
    ):
        """
        Initializes the object with an optional start time and scale multiplier.
            If the start_time is not provided, the current UTC time is used. If the scale is not provided,
            the default multiplier value is applied. The multiplier is used for scaling the difference
            in time for the purpose of this object.
            Args:
                start_time (datetime, optional): The start time reference for this object. Defaults to None,
                    which means the current UTC time will be used.
                scale (float, optional): The time scale multiplier. Defaults to None, which means the object's default
                    multiplier will be used.
            Raises:
                TypeError: If the start_time is not a datetime object or None.
                ValueError: If the scale is not a float or None.
        """
        self.start_time = start_time or datetime.utcnow()
        self.multiplier = scale or self.multiplier

    def now(self) -> datetime:
        """
        Returns the current time adjusted by the object's start_time and multiplier attributes.
        If the start_time attribute is None, the current UTC time is returned, otherwise, the method calculates the elapsed time since start_time, scales it by the multiplier, and then adds the result to the start_time to return the adjusted current time.
        Returns:
            datetime: The current time adjusted according to start_time and multiplier, or the current UTC time if start_time is None.
        """
        if self.start_time is None:
            return datetime.utcnow()
        return self.start_time + timedelta(
            seconds=(datetime.utcnow() - self.start_time).total_seconds()
            * self.multiplier
        )
