"""

The "Clock" module provides an interface for working with time within an application.

This module defines a "Clock" class that follows Python's typing.Protocol, which outlines methods expected to
be implemented by concrete classes. The purpose of the protocol is to define a common interface for time
operations, allowing for different implementations that can interoperate within the application's ecosystem.

The "Clock" class has a single class attribute, "multiplier", which is set to a default value of 0.001. This
implies that the class is dealing with time at a millisecond granularity by default, but this can be overridden
in concrete implementations if needed.

The "Clock" class defines one method, "now", which is expected to return the current datetime. Concrete
classes that implement the "Clock" protocol should provide their own mechanism to return the current time,
potentially with their own internal logic or time source (e.g., system time, a remote time server, or a
simulated clock for testing purposes).

Consumers of this module and the "Clock" class should ensure that any concrete implementation respects the
interface outlined by the protocol, especially the "now" method signature, to ensure compatibility and
interchangeability among different time systems.
"""
import typing
from datetime import datetime


class Clock(typing.Protocol):
    """
    A protocol defining the structure of a Clock-like object.
    This protocol specifies that any Clock-like object should have a class attribute named
    `multiplier`, with a default value of 0.001, indicating that the basic time unit of this
    Clock is milliseconds. It also requires the implementation of an instance method
    `now()`, which should return the current time as a `datetime` object.
    
    Attributes:
        multiplier (float):
             A class-level constant defining the time unit. The default
            value of 0.001 indicates that time is measured in milliseconds.
    
    Methods:
        now:
            Should be implemented by classes that follow this protocol to provide
            the current time.
    
    Returns:
        datetime:
             The current time as a `datetime` object.

    """
    multiplier: float = 0.001  # 1ms

    def now(self) -> datetime:
        """
        
        Returns the current date and time as a datetime object.
        
        Returns:
            datetime:
                 The current date and time.

        """
        ...
