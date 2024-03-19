"""

This module provides utility functions that facilitate working with state machines within the StateForward framework. It includes several functions which are designed to define substates and regions within a state machine, as well as a mechanism to send events to state machine instances.

### Functions

- `submachine_state`
  This function creates a new state within the state machine with the additional attributes provided. The function uses `redefine` from the `model` module to create a modified version of the state machine and assigns this new state as a 'submachine'. The resulting state can optionally be named using the `name` parameter or given additional attributes using keyword arguments.

- `submachine_region`
  It returns a region within a submachine state, which represents a part of a state machine that can run concurrently with other regions. The region is created as an instance of 'elements.Region' with its own elements, including an initial state that is automatically created using the `elements.initial` function.

- `send`
  This function is responsible for sending events to either all state machine instances or a specific element within a state machine. It can handle events asynchronously and can return a single `Awaitable` or a list of `Awaitables` depending on whether the event is sent to a single element or multiple instances, respectively. The function can accept either an `elements.Event`, an `model.Element` instance, or a string identifier for a target state machine element. If an element is not specified, the event is broadcasted to all instances.

### Types and Members

The module uses several types and members from the `stateforward` package. It imports `model` which provides tools for defining and manipulating model elements, and `elements` which contains classes that represent the different components of a state machine such as `StateMachine`, `State`, `Event`, and `Region`.

### Usage

The functions in this module are designed to be used for creating and managing the structure of state machines and their behaviors concerning event handling. It provides a more granular control over the definition of states and the flow of events within a stateful system. By utilizing these functions, developers can build sophisticated and complex state machine structures capable of handling intricate workflows and state transitions within the StateForward framework.
"""
from stateforward import model
from types import FunctionType
from stateforward.core import elements, decorators
import typing


def submachine_state(
    state_machine: type[elements.StateMachine], name: str = None, **attributes
):
    """
    Creates a state that represents a submachine within a larger state machine.
    This function redefines the given state machine to be a State sub-class with the specified attributes. Additionally, it designates the created state as a submachine, which allows it to function as an independent state machine within a parent state machine.

    Args:
        state_machine (type[elements.StateMachine]):
             The type of the state machine which is to be used as a submachine.
        name (str, optional):
             The name of the submachine state to be created. If not provided, defaults to None.
        **attributes:
             Arbitrary keyword arguments that will be used to define the properties of the submachine state.

    Returns:
        elements.State:
             A new State instance that is subclassed from the specified state machine and incorporates the given attributes.

    """
    if (entry := attributes.get("entry", None)) is not None:
        if isinstance(entry, FunctionType):
            attributes["entry"] = decorators.behavior(entry)
        print("entry", entry)
    state = model.redefine(
        state_machine,
        bases=(elements.State, state_machine),
        name=name or state_machine.__name__,
        **attributes,
    )

    model.set_attribute(state, "submachine", state)
    # model.set_attribute(submachine, "submachine_state", state)
    return state


def submachine_region(state_machine: type[elements.StateMachine], **attributes):
    """
    Creates a submachine region based on the provided state machine and optional attributes.
    This function instantiates a submachine state through the `submachine_state` function and
    initializes a new region object with a name derived from the state machine's name, appending 'SubmachineRegion' to it.
    The new region is augmented with the created submachine state and an initial placeholder element.

    Args:
        state_machine (type[elements.StateMachine]):
             The state machine type to base submachine region on.
        **attributes:
             Variable length keyword argument list to override or add attributes to the created submachine state.

    Returns:

    """
    state = submachine_state(state_machine, **attributes)
    region = model.new(
        f"{state_machine.name}SubmachineRegion",
        (elements.Region,),
        owned_elements=(state, elements.initial(state)),
    )
    return region


def send(
    event: elements.Event,
    element: typing.Optional[typing.Union[model.Element, str]] = None,
) -> typing.Union[typing.Awaitable, list[typing.Awaitable]]:
    """
    Sends an event to one or more state machine interpreters.
    This function dispatches the specified event to the interpreter associated with the given element, or to all interpreters if no element is provided. It can handle both individual element objects or their string identifiers as the 'element' argument. If multiple interpreters are targeted, the result is a list of Awaitable objects, each representing the asynchronous operation of sending the event to a particular interpreter.

    Args:
        event (elements.Event):
             The event to be dispatched to the state machine interpreters.
        element (Optional[Union[model.Element, str]], optional):
             The element or its identifier to which the event will be sent. If None, the event is sent to all interpreters. Defaults to None.

    Returns:
        Union[Awaitable, list[Awaitable]]:
             An awaitable if a single element's interpreter is targeted, else a list of awaitables, each for the corresponding interpreter's send operation.

    """
    if element is None:
        return [
            model.of(element).interpreter.send(event)
            for element in model.Model.__all_instances__.values()
        ]

    if isinstance(element, str):
        element = model.Model.__all_instances__[element]
    return model.of(element).interpreter.send(event)
