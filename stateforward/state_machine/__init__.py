"""
The state machine package allows defining states, transitions between states, and the behavior to execute upon entering or exiting states. Additionally, asynchronous behavior is supported to handle operations that need to execute in the background or are dependent on asynchronous events. States can have nested regions and sub-states, forming a hierarchy known as a statechart.

## Key Concepts and Classes

### StateMachine

- Base class for defining a state machine.
- Uses the concepts of states, regions, and transitions to model complex behavior.
- Can be extended to represent the specific logic of an application's state machine.

### State

- Represents a specific condition or status of part of a system.
- Can contain behaviors to perform on entry or exit.
- Can be simple or composite, with composite states containing nested regions and states.

### Transition

- Represents a change from one state to another triggered by an event and, optionally, a guard condition.

### Event

- Used as triggers for transitions.
- Can be any meaningful occurrence or condition change that affects the state machine.

## Preprocessor

- Responsible for preparing a state machine for execution by turning definitions into a runtime model with relationships between elements.

## Interpreters

Interpreters handle the execution of the state machine according to its definition and incoming events.

### AsyncStateMachineInterpreter

- A specialized interpreter for running state machines asynchronously.
- Processes events, manages state transitions, and invokes the defined behaviors.
- Uses the `asyncio` library to handle concurrency and background operations.

## Creating a State Machine

To create a state machine, you extend the `StateMachine` class and define your states, transitions, and behaviors within it. You can use decorators and helper functions to simplify the definition of behaviors and transitions.

## Handling Events

Events are the primary way to trigger transitions in the state machine. You can define custom events and dispatch them to the state machine using the interpreter's `dispatch` method. The state machine will handle these events according to the defined transitions and behaviors.

## Example Usage

Examples are provided in the form of subclasses of `StateMachine`, demonstrating how to define and interact with state machines. Common scenarios such as a light switch state machine and a traffic signal state machine are provided for illustrative purposes.

If you have any questions or need further assistance, please refer to the code documentation strings or contact the development team.
"""
from .elements import AsyncStateMachine
from .preprocessor import StateMachinePreprocessor
from .interpreters import AsyncStateMachineInterpreter
from .validator import StateMachineValidator
