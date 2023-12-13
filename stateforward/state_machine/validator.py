from stateforward import model
from stateforward import elements
from stateforward.state_machine.log import create_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from stateforward.elements import StateMachine

logger = create_logger("StateMachineValidator")


class StateMachineValidator(model.Validator):
    def validate_final_state(self, final_state: elements.FinalState):
        if hasattr(final_state, "exit"):
            raise Exception(
                f"Final state {model.qualified_name_of(final_state)} cannot have exit behavior"
            )
        elif hasattr(final_state, "outgoing"):
            raise Exception(
                f"Final state {model.qualified_name_of(final_state)} cannot have do activity"
            )

    def validate_vertex(self, vertex: type[elements.Vertex]):
        if vertex.container is None or not model.element.is_subtype(
            vertex.container, elements.Region
        ):
            raise ValueError(
                f"Vertex {model.qualified_name_of(vertex)} must be contained in a Region"
            )
        if vertex.outgoing.length == 0 and vertex.incoming.length == 0:
            logger.warning(
                f"Vertex {model.qualified_name_of(vertex)} has no incoming or outgoing transitions"
            )

    def validate_region(self, region: type[elements.Region]):
        if region.state_machine is not None and region.initial is None:
            raise Exception(
                f"Region {model.qualified_name_of(region)} must have initial state"
            )
        elif region.state_machine is not None and region.state is not None:
            raise ValueError(
                f"Region {model.qualified_name_of(region)} cannot be owned by a state and a state machine"
            )

    def validate_transition(self, transition: type[elements.Transition]):
        if transition.path is None:
            raise ValueError(
                f"Transition {model.qualified_name_of(transition)} doesn't have a path"
            )
        elif (
            model.element.is_subtype(transition.target, elements.Pseudostate)
            and transition.target.kind is elements.PseudostateKind.join
            and (
                transition.guard is not None
                or not all(
                    model.element.is_subtype(event, elements.CompletionEvent)
                    for event in transition.events.elements()
                )
                is not None
            )
        ):
            print(transition.guard, list(transition.events.elements()))
            raise ValueError(
                f"Transition {model.qualified_name_of(transition)} to join {model.qualified_name_of(transition.target)} must not have a guard or events"
            )
        elif transition.kind is elements.TransitionKind.internal and not (
            model.element.is_subtype(transition.source, elements.State)
            or transition.source != transition.target
        ):
            raise ValueError(
                f"Transition {model.qualified_name_of(transition)} with kind internal must have a State as its source, and its source and target must be equal"
            )
        elif (
            model.element.is_subtype(transition.source, elements.Pseudostate)
            and transition.events is not None
        ):
            raise ValueError(
                f"Transition {model.qualified_name_of(transition)} from outgoing Pseudostate may not have a Event."
            )
        # elif transition.target is not None:
        #     source_container = transition.source.container
        #     target_container = transition.target.container
        #     if (
        #         source_container != target_container
        #         and source_container.state == target_container.state
        #     ):
        #         raise ValueError(
        #             f"Transition {model.qualified_name_of(transition)} cannot cross Regions of the same State"
        #         )

    def validate_pseudostate(self, element: type[elements.Pseudostate]):
        if element.kind == elements.PseudostateKind.choice:
            last_transition = tuple(element.outgoing)[-1]
            if last_transition.guard is not None:
                raise ValueError(
                    f"choice psuedostate {model.qualified_name_of(element)} has a guard on the last transition"
                )
        elif element.kind == elements.PseudostateKind.initial:
            if not element.outgoing.length:
                raise ValueError(
                    f"initial psuedostate {model.qualified_name_of(element)} has no outgoing transitions"
                )
            elif element.incoming.length:
                raise ValueError(
                    f"initial psuedostate {model.qualified_name_of(element)} has incoming transitions"
                )
            outgoing = element.outgoing[0]
            if outgoing.guard is not None:
                raise ValueError(
                    f"initial psuedostate {model.qualified_name_of(element)} has a guard on the outgoing transition"
                )
        elif element.kind == elements.PseudostateKind.join:
            containers = set()
            for transition in element.incoming.elements():
                if model.qualified_name_of(transition.source.container) in containers:
                    print(
                        model.qualified_name_of(transition.source.container), containers
                    )
                    raise ValueError(
                        f"All {tuple(model.qualified_name_of(t) for t in element.incoming.elements())} incoming a join elements.Vertex ({model.qualified_name_of(element)}) must originate in different Regions"
                    )
                containers.add(model.qualified_name_of(transition.source.container))

    def validate_completion_event(self, event: type[elements.CompletionEvent]):
        logger.debug("validating completion event")
        if not model.element.is_subtype(model.owner_of(event), elements.State):
            raise ValueError(
                f"CompletionEvent {model.qualified_name_of(event)} must be owned by a State"
            )
