"""

## Module `elements`

This module defines the `AsyncStateMachine` class, which integrates functionality from the `stateforward` package. It represents an asynchronous state machine that is capable of performing state transitions in a non-blocking manner, suitable for event-driven applications.

### Classes

#### `AsyncStateMachine`

The `AsyncStateMachine` class is a subclass of `core.StateMachine` and `core.CompositeState`, indicating that it represents both a state machine and a composite state construct. It is designed to work asynchronously, allowing states to transition without waiting for blocking operations to complete.

##### Inheritance

- Inherits from `core.StateMachine`: Provides the core state machine functionality.
- Inherits from `core.CompositeState`: Allows for nested state structures within the state machine.

##### Composition

The `AsyncStateMachine` also includes three main components by composition:

- `preprocessor`: An instance of `StateMachinePreprocessor` class, which is responsible for preprocessing state machine definitions to ensure they are in the correct format for execution.
- `validator`: An instance of `StateMachineValidator` class, which validates the state machine's structure and behavior to make sure it conforms to certain standards before execution.
- `interpreter`: An instance of `AsyncStateMachineInterpreter` which is responsible for interpreting events and executing the appropriate state transitions in an asynchronous manner.

### Class Methods

#### `compile`

Annotated as a class method within the module, `compile` is intended to perform compilation of a `StateMachine` instance. While the purpose and behavior of the method are not detailed here, it suggests that there is a mechanism to transform or prepare a state machine for execution.

### Summary

The `elements` module provides the necessary classes and infrastructure for defining and operating asynchronous state machines within the `stateforward` package. It leverages inheritance and composition to build a powerful state management system that fits well within async-enabled Python applications.
"""
from stateforward import core
from stateforward.state_machine.preprocessor import StateMachinePreprocessor
from stateforward.state_machine.validator import StateMachineValidator
from stateforward.state_machine.interpreters import AsyncStateMachineInterpreter


class AsyncStateMachine(
    core.StateMachine,
    core.CompositeState,
    preprocessor=StateMachinePreprocessor,
    validator=StateMachineValidator,
    interpreter=AsyncStateMachineInterpreter,
):
    """
    A class that combines functionalities of a state machine with asynchronous processing capabilities. This class inherits from core.StateMachine and core.CompositeState, integrating a preprocessor and validator for state transitions, and an interpreter specifically designed to handle asynchronous operations within the state machine.
    
    Attributes:
        preprocessor (StateMachinePreprocessor):
             An instance of a preprocessor class used to prepare input data for state transitions.
        validator (StateMachineValidator):
             An instance of a validator class used to ensure the validity of state transitions according to the predefined rules and conditions.
        interpreter (AsyncStateMachineInterpreter):
             An instance of an interpreter designed to execute the state transitions asynchronously, handling asynchronous tasks as part of the state machine's operation.
            The AsyncStateMachine class does not define its own methods or properties, but instead, relies on the methods and properties inherited from its parent classes and the instances of the preprocessor, validator, and interpreter provided at instantiation.

    """

    pass
