"""



Module `__init__` Overview
========================

This __init__ module is the entry point for a collection of protocols that represent a suite of asynchronous, event-driven tasks and utilities. Each protocol outlines a set of required methods and properties for classes implementing these interfaces. These protocols form the foundation for a system designed to facilitate the execution of tasks in reaction to various events in an asynchronous fashion. 

Included Protocols:
- `Clock`: Interface representing a time source, providing timing information.
- `Future`: Interface for future objects that encapsulate the asynchronous execution of a callable.
- `Queue`: Interface for queue implementations that store items in a first-in-first-out (FIFO) order.
- `Interpreter`: Interface representing the core logic for handling and coordinating events.
- `Logger`: Interface for logging various levels of events.

Each protocol has its own predefined set of methods, which must be fulfilled by any class implementing the protocol. This provides a clear and consistent contract for how objects interact within the system, ensuring that components can be used interchangeably as long as they adhere to the protocol specifications.

This module does not include any direct implementations of these protocols but rather establishes the necessary interfaces for consistent interaction among different components that will implement this behavior.

To use these protocols, developers should subclass and provide concrete implementations of the methods described in each protocol's documentation.

The module also handles imports from submodules, exposing the protocols to be easily imported from a single point, thereby increasing the convenience and maintainability of the codebase that relies on these interfaces.
"""
# ruff: noqa
from .clock import Clock
from .future import Future
from .queue import Queue
from .interpreter import Interpreter
from .logger import Logger
