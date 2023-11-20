from stateforward import elements
from stateforward.state_machine.preprocessor import StateMachinePreprocessor
from stateforward.state_machine.validator import StateMachineValidator
from stateforward.state_machine.interpreters import AsyncStateMachineInterpreter


class AsyncStateMachine(
    elements.StateMachine,
    elements.CompositeState,
    preprocessor=StateMachinePreprocessor,
    validator=StateMachineValidator,
    interpreter=AsyncStateMachineInterpreter,
):
    """
    Asynchronous state machine implementation that handles behaviors and state transitions.

    This class extends the generic Behavior and CompositeState classes to facilitate
    concurrent operations within the state machine. The AsyncStateMachine allows for the
    definition of states and transitions and manages the asynchronous execution of behavior
    activities triggered by events.

    Attributes:
        submachine_state (State): The reference to the submachine state if this state machine
                                  is used as a submachine within another state machine.

    Properties:
        state (tuple[State]): A tuple containing references to all the currently active states
                              within the state machine.
    """

    pass
