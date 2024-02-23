"""

The `__init__` module serves as the initializer for the `Clock` class within its package. It primarily handles the importing of the `Clock` class from its respective module, allowing for instantiation and use of `Clock` objects in other parts of the application where the `__init__` module is imported.

The `Clock` class, which is imported by the `__init__` module, is a utility that simulates a clock with configurable time flow. The key features and attributes of the `Clock` class are as follows:

- `multiplier`: A float attribute that defines the speed at which time progresses in the `Clock` instance. It defaults to `0.001`, which means time progresses at a millisecond rate compared to real time.

- `start_time`: An attribute that can hold a `datetime` object representing the start time of the clock. It can also be `None` if not set, in which case the current UTC time is used.

- `__init__(self, start_time: typing.Optional[datetime]=None, scale: float=None)`: The constructor method for the `Clock` class allows for an optional `start_time` and a `scale` (multiplier) to be set upon instantiation. If `start_time` isn't provided, the current UTC time is used. If `scale` isn't provided, it defaults to the class attribute `multiplier`.

- `now(self) -> datetime`: This method calculates and returns the current time as per the `Clock` object's start time and multiplier. If no `start_time` was set, it returns the current UTC time.

By including the `Clock` class in the `__init__` module, it becomes a more accessible component for other modules within the package to create and manage simulated clock instances as needed for application-specific logic or time-based simulations.
"""
from .clock import Clock
