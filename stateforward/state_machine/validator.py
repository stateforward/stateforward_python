from stateforward import model
from stateforward import elements
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stateforward.elements import StateMachine


class StateMachineValidator(model.Validator):
    def validate_final_state(self, final_state: elements.FinalState):
        if hasattr(final_state, "exit"):
            raise Exception(
                f"Final state {final_state.qualified_name} cannot have exit behavior"
            )
        elif hasattr(final_state, "outgoing"):
            raise Exception(
                f"Final state {final_state.qualified_name} cannot have do activity"
            )

    def validate_region(self, region: type[elements.Region]):
        if region.state_machine is not None and region.initial is None:
            raise Exception(f"Region {region.qualified_name} must have initial state")
        elif region.state_machine is not None and region.state is not None:
            raise ValueError(
                f"Region {region.qualified_name} cannot be owned by a state and a state machine"
            )

    # def validate_state(self, state: type[elements.State]):
    #     if state.submachine is not None and state.region.length > 0:
    #         raise ValueError(
    #             f"State {state.qualified_name} is not allowed to have both a submachine and Regions."
    #         )

    def validate_transition(self, transition: type[elements.Transition]):
        if transition.path is None:
            raise ValueError(
                f"Transition {transition.qualified_name} doesn't have a path"
            )
        elif (
            model.is_subtype(transition.target, elements.Pseudostate)
            and transition.target.kind is elements.PseudostateKind.join
            and (
                transition.guard is not None
                or not all(
                    model.is_subtype(event, elements.CompletionEvent)
                    for event in transition.events.elements()
                )
                is not None
            )
        ):
            print(transition.guard, list(transition.events.elements()))
            raise ValueError(
                f"Transition {transition.qualified_name} to join {transition.target.qualified_name} must not have a guard or events"
            )
        elif transition.kind is elements.TransitionKind.internal and not (
            model.is_subtype(transition.source, elements.State)
            or transition.source != transition.target
        ):
            raise ValueError(
                f"Transition {transition.qualified_name} with kind internal must have a State as its source, and its source and target must be equal"
            )
        elif (
            model.is_subtype(transition.source, elements.Pseudostate)
            and transition.events is not None
        ):
            raise ValueError(
                f"Transition {transition.qualified_name} from outgoing Pseudostate may not have a Event."
            )
        else:
            source_container = transition.source.container
            target_container = transition.target.container
            if (
                source_container != target_container
                and source_container.state == target_container.state
            ):
                raise ValueError(
                    f"Transition {transition.qualified_name} cannot cross Regions of the same State"
                )

    def validate_pseudostate(self, element: type[elements.Pseudostate]):
        if element.kind == elements.PseudostateKind.choice:
            last_transition = tuple(element.outgoing.elements())[-1]
            if last_transition.guard is not None:
                raise ValueError(
                    f"choice psuedostate {element.qualified_name} has a guard on the last transition"
                )
        elif element.kind == elements.PseudostateKind.initial:
            if not element.outgoing.length:
                raise ValueError(
                    f"initial psuedostate {element.qualified_name} has no outgoing transitions"
                )
            elif element.incoming.length:
                raise ValueError(
                    f"initial psuedostate {element.qualified_name} has incoming transitions"
                )
            outgoing = element.outgoing.attributes[0]
            if outgoing.guard is not None:
                raise ValueError(
                    f"initial psuedostate {element.qualified_name} has a guard on the outgoing transition"
                )
        elif element.kind == elements.PseudostateKind.join:
            containers = set()
            for transition in element.incoming.elements():
                if transition.source.container.qualified_name in containers:
                    print(transition.source.container.qualified_name, containers)
                    raise ValueError(
                        f"All {tuple(t.qualified_name for t in element.incoming.elements())} incoming a join elements.Vertex ({element.qualified_name}) must originate in different Regions"
                    )
                containers.add(transition.source.container.qualified_name)
