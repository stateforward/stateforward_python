from typing import Callable, Union, Sequence, Type
from datetime import datetime, timedelta
from stateforward import model
from stateforward.elements import elements


def submachine_state(
    state_machine: type[elements.StateMachine], name: str = None, **attributes
):
    state = model.redefine(state_machine, bases=(elements.State,), **attributes)
    model.set_attribute(state, "submachine", state)
    # state = model.new_element(
    #     name or state_machine.name,
    #     (elements.State,),
    #     submachine=submachine,
    # )
    return state


def submachine_region(state_machine: type[elements.StateMachine], **attributes):
    state = submachine_state(state_machine, **attributes)
    region = model.new(
        f"{state_machine.name}SubmachineRegion",
        (elements.Region,),
        owned_elements=(state, elements.initial(state)),
    )
    return region


def send(event: elements.Event, element: model.Element):
    return element.model.interpreter.send(event)
