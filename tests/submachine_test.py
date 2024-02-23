import stateforward as sf
import asyncio
import pytest
from tests.mock import mock, expect


class e1(sf.Event):
    pass


class e2(sf.Event):
    pass


class SM(sf.AsyncStateMachine):
    class s1(sf.State):
        class s1_1(sf.State):
            pass

        class s1_2(sf.State):
            pass

        class s1_3(sf.State):
            pass

    class s2(sf.State):
        @sf.decorators.behavior
        async def activity(self, event=None):
            await asyncio.sleep(1)
            return "s2"

    class s3(sf.State):
        @sf.decorators.behavior
        async def activity(self, event=None):
            await asyncio.sleep(1)

    initial = sf.initial(s1.s1_1)
    transitions = sf.collection(
        sf.transition(source=s1.s1_1, target=s1.s1_2),
        # sf.transition(source=s1.s1_2, target=s1.s1_3),
        # sf.transition(e1, source=s1, target=s1.s1_1),
    )


@pytest.mark.asyncio
async def test_local_transition():
    sm = mock(SM())
    await sm.interpreter.start()
    expect.only(sm.s1, sm.s1.s1_1, sm.s1.s1_2).was_entered()
    # sm.reset_mocked()
    # await sm.dispatch(e1())
    # expect.only(sm.s1.s1_1).was_entered()
