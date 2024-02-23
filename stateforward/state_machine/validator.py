"""

The `validator` module is responsible for ensuring the correctness and consistency of state machine definitions. It accomplishes this through the `StateMachineValidator` class, which contains various validation methods to enforce the rules and constraints required for state machines to behave as expected. Each method within this validator class targets a specific component of a state machine, such as states, transitions, vertices, regions, pseudostates, and completion events. The validation process checks for common errors such as improperly defined states, transitions without paths, or misconfigured pseudostates, and raises exceptions or warnings when inconsistencies are detected.

The `StateMachineValidator` class inherits from `model.Validator` and overrides methods to provide custom validation logic for each type of state machine element. These methods leverage the `stateforward.model` and `stateforward.core` modules to analyze the elements of the state machine. The validator also utilizes a logger, acquired through the `create_logger` method, to report warning messages during the validation process. This logger is named 'StateMachineValidator' and is configured to handle logging appropriately.

Each validation method in the `StateMachineValidator` class is designed to be called with the specific type of state machine element that it is meant to validate. For example, `validate_final_state` checks if final states do not define any exit behavior or outgoing transitions. On the other hand, `validate_transition` checks if the transitions follow the correct path, that they have appropriate guards and events based on their type, and that they adhere to internal transition rules. Additionally, the methods `validate_vertex`, `validate_region`, `validate_pseudostate`, and `validate_completion_event` provide similar targeted validations for their respective state machine components.

Overall, the `validator` module plays a critical role in ensuring that a state machine is well-defined and free of structural errors before it is executed.
"""
from stateforward import model
from stateforward import core
from stateforward.state_machine.log import create_logger
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

logger = create_logger("StateMachineValidator")


class StateMachineValidator(model.Validator):
    """
    A validator class for state machines based on the UML state machine model.
    This class provides several methods to validate different components
    of a state machine such as final states, vertices, regions, transitions, pseudostates,
    and completion events. It checks for various constraints and raises exceptions
    or warnings if the components of the state machine do not meet the expected criteria.
    
    Attributes:
    
    Raises:
        Exception:
             Raised when final states have exit behavior or outgoing activity,
            when a region must have an initial state or cannot be owned by both
            a state and a state machine, and similar situations that violate the state machine model.
        ValueError:
             Raised when vertices are not contained in a region, when transitions lack a path or
            have incorrect configurations, when completion events have invalid ownership, and
            other cases where value conditions are not met.
        Warning:
             Logged when a vertex has no incoming or outgoing transitions.
    
    Methods:
        validate_final_state:
             Ensures that final states do not have exit behaviors or outgoing activity.
        validate_vertex:
             Verifies that vertices are properly contained within a region and logs a warning if
            they lack transitions.
        validate_region:
             Checks that a region has an initial state if it is part of a state machine
            and ensures it is not owned by both a state and a state machine.
        validate_transition:
             Validates transitions, checking for correct paths, guards, events, and source-target rules.
        validate_pseudostate:
             Ensures that pseudostates follow the rules of their specific kind (e.g., choice, initial, join).
        validate_completion_event:
             Verifies that completion events are owned by a state.

    """

    def validate_final_state(self, final_state: core.FinalState):
        """
        Checks if the provided final_state object complies with the constraints of a final state.
        This method ensures that the final_state argument does not have an exit behavior and that there
        are no outgoing activities from it. If either of these conditions is violated, an exception is raised.
        
        Args:
            final_state (core.FinalState):
                 An instance of FinalState to be validated.
        
        Raises:
            Exception:
                 If the final_state has an exit behavior or outgoing activities.

        """
        if hasattr(final_state, "exit"):
            raise Exception(
                f"Final state {model.qualified_name_of(final_state)} cannot have exit behavior"
            )
        elif final_state.outgoing.length > 0:
            raise Exception(
                f"Final state {model.qualified_name_of(final_state)} cannot have activity"
            )

    def validate_vertex(self, vertex: type[core.Vertex]):
        """
        Checks if the given vertex adheres to certain conditions within its state machine.
        This method ensures that a vertex is contained within a region and raises an error if it is not. It also logs a warning if the vertex has no incoming or outgoing transitions, indicating that it is disconnected from the state machine.
        
        Args:
            vertex (type[core.Vertex]):
                 The vertex to validate. It must be an instance or subclass of core.Vertex.
        
        Raises:
            ValueError:
                 If the vertex is not contained within a Region.
        
        Returns:

        """
        if vertex.container is None or not model.element.is_subtype(
            vertex.container, core.Region
        ):
            raise ValueError(
                f"Vertex {model.qualified_name_of(vertex)} must be contained in a Region"
            )
        if vertex.outgoing.length == 0 and vertex.incoming.length == 0:
            logger.warning(
                f"Vertex {model.qualified_name_of(vertex)} has no incoming or outgoing transitions"
            )

    def validate_region(self, region: type[core.Region]):
        """
        Validates if the given region meets the criteria of ownership and initial state requirement.
        This method ensures that a region associated with a state machine has an initial state defined, and it also checks for an invalid condition where a region is simultaneously owned by both a state and a state machine, raising errors when these conditions are not met.
        
        Args:
            region (type[core.Region]):
                 The region to be validated.
        
        Raises:
            Exception:
                 If the region is associated with a state machine but has no initial state.
            ValueError:
                 If the region is owned by both a state and a state machine at the same time.

        """
        if region.state_machine is not None and region.initial is None:
            raise Exception(
                f"Region {model.qualified_name_of(region)} must have initial state"
            )
        elif region.state_machine is not None and region.state is not None:
            raise ValueError(
                f"Region {model.qualified_name_of(region)} cannot be owned by a state and a state machine"
            )

    def validate_transition(self, transition: type[core.Transition]):
        """
        Checks the validity of a state transition within a state machine.
        This method verifies that a transition is properly constructed according to several rules:
        - The transition must have a valid path.
        - Transitions leading to a join pseudostate must not have a guard or associated events.
        - Internal transitions must originate from a state, and the source and target of the transition must be the same.
        - Transitions from an outgoing pseudostate cannot have associated events.
        If any of the validation checks fail, a ValueError will be raised with a specific error message detailing the reason.
        
        Args:
            transition (type[core.Transition]):
                 The transition that is being validated.
        
        Raises:
            ValueError:
                 If the transition is not correctly constructed according to the rules specified.

        """
        if transition.path is None:
            raise ValueError(
                f"Transition {model.qualified_name_of(transition)} doesn't have a path"
            )
        elif (
            model.element.is_subtype(transition.target, core.Pseudostate)
            and transition.target.kind is core.PseudostateKind.join
            and (
                transition.guard is not None
                or not all(
                    model.element.is_subtype(event, core.CompletionEvent)
                    for event in transition.events.elements()
                )
                is not None
            )
        ):
            print(transition.guard, list(transition.events.elements()))
            raise ValueError(
                f"Transition {model.qualified_name_of(transition)} to join {model.qualified_name_of(transition.target)} must not have a guard or events"
            )
        elif transition.kind is core.TransitionKind.internal and not (
            model.element.is_subtype(transition.source, core.State)
            or transition.source != transition.target
        ):
            raise ValueError(
                f"Transition {model.qualified_name_of(transition)} with kind internal must have a State as its source, and its source and target must be equal"
            )
        elif (
            model.element.is_subtype(transition.source, core.Pseudostate)
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

    def validate_pseudostate(self, element: type[core.Pseudostate]):
        """
        Validates the state of a pseudostate in a state machine to ensure it adheres to specific rules based on its kind.
        This method checks a pseudostate element for conformity to the rules that pertain to its kind. For example, choice pseudostates should not have a guard on the last transition, initial pseudostates should not have incoming transitions and must have exactly one outgoing transition without a guard, and join pseudostates must have all incoming transitions originating from different regions. Violations of these rules will result in a ValueError being raised.
        
        Args:
            element (type[core.Pseudostate]):
                 The pseudostate element to validate.
        
        Raises:
            ValueError:
                 If the pseudostate's configuration violates the rules for its kind.

        """
        if element.kind == core.PseudostateKind.choice:
            last_transition = tuple(element.outgoing)[-1]
            if last_transition.guard is not None:
                raise ValueError(
                    f"choice psuedostate {model.qualified_name_of(element)} has a guard on the last transition"
                )
        elif element.kind == core.PseudostateKind.initial:
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
        elif element.kind == core.PseudostateKind.join:
            containers = set()
            for transition in element.incoming.elements():
                if model.qualified_name_of(transition.source.container) in containers:
                    print(
                        model.qualified_name_of(transition.source.container), containers
                    )
                    raise ValueError(
                        f"All {tuple(model.qualified_name_of(t) for t in element.incoming.elements())} incoming a join core.Vertex ({model.qualified_name_of(element)}) must originate in different Regions"
                    )
                containers.add(model.qualified_name_of(transition.source.container))

    def validate_completion_event(self, event: type[core.CompletionEvent]):
        """
        Validates if the given completion event is associated with a State type.
        This method checks whether the provided completion event is owned by an object of the State type, and raises a ValueError with a descriptive message if that is not the case. It is meant to ensure that completion events, which signify the end of a specific state, are properly linked to State instances in the model.
        
        Args:
            event (type[core.CompletionEvent]):
                 The completion event to validate.
        
        Raises:
            ValueError:
                 If the event is not owned by a State type or if any other validity condition is not met.

        """
        logger.debug("validating completion event")
        if not model.element.is_subtype(model.owner_of(event), core.State):
            raise ValueError(
                f"CompletionEvent {model.qualified_name_of(event)} must be owned by a State"
            )
