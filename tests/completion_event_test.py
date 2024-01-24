import stateforward as sf
import asyncio
import pytest
from tests.mock import mock, expect


class SM(sf.AsyncStateMachine):
    class s1(sf.State):
        @sf.decorators.behavior
        async def activity(self, event=None):
            await asyncio.sleep(1)
            return "s1"

    class s2(sf.State):
        @sf.decorators.behavior
        async def activity(self, event=None):
            await asyncio.sleep(1)
            return "s2"

    class s3(sf.State):
        @sf.decorators.behavior
        async def activity(self, event=None):
            await asyncio.sleep(1)

    initial = sf.initial(s1)
    transitions = sf.collection(
        sf.transition(source=s1, target=s2),
        sf.transition(source=s2, target=s3),
    )


@pytest.mark.asyncio
async def test_completions():
    sm = mock(SM())
    print(sm.interpreter)
    await sm.interpreter.start()
    expect.only(sm.s1).was_entered()
    sm.reset_mocked()
    await asyncio.sleep(1.1)
    expect.only(sm.s2).was_entered()
    sm.reset_mocked()
    await asyncio.sleep(1.1)
    expect.only(sm.s3).was_entered()
