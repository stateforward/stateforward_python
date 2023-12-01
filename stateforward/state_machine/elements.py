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


): # testing # for this
    # bang

    pass
