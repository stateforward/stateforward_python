from typing import Callable, Union, Sequence, Type
from datetime import datetime, timedelta
from stateforward import model
from stateforward.elements import elements


def submachine_state(
    state_machine: type[elements.StateMachine], name: str = None, **attributes
):
    submachine = model.redefine(state_machine, **attributes)
    state = model.new_element(
        name or state_machine.name,
        (elements.State,),
        submachine=submachine,
    )
    return state


def submachine_region(state_machine: type[elements.StateMachine], **attributes):
    state = submachine_state(state_machine, **attributes)
    region = model.new_element(
        f"{state_machine.name}SubmachineRegion",
        (elements.Region,),
        owned_elements=(state, elements.initial(state)),
    )
    return region


def dispatch(event: elements.Event, element: model.Element):
    return element.model.interpreter.dispatch(event)
