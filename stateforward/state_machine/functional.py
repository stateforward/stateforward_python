from stateforward import model
from stateforward.elements import elements
import typing


def submachine_state(
    state_machine: type[elements.StateMachine], name: str = None, **attributes
):
    state = model.redefine(state_machine, bases=(elements.State,), **attributes)
    model.set_attribute(state, "submachine", state)
    return state


def submachine_region(state_machine: type[elements.StateMachine], **attributes):
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
    if element is None:
        return [
            model.of(element).interpreter.send(event)
            for element in model.all_instances().values()
        ]
    if isinstance(element, str):
        element = model.all_instances()[element]
    return model.of(element).interpreter.send(event)
