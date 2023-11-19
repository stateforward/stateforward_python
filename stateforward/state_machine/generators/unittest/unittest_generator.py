import stateforward as sf
from unittest.mock import AsyncMock


class UnitTestGenerator(sf.model.Visitor):
    def generate(self, model: sf.StateMachine):
        pass
