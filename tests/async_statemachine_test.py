import pytest
import stateforward as sf
from unittest.mock import AsyncMock


class TestSM(sf.AsyncStateMachine):
    class s1(sf.State):
        entry = sf.behavior(AsyncMock())
        do_activity = sf.behavior(AsyncMock())
        exit = sf.behavior(AsyncMock())

    initial = sf.initial(s1)


@pytest.mark.asyncio
async def test_state_entry():
    sm = TestSM()
    await sm.interpreter.start()
    assert sm.s1.entry.activity.call_count == 1


@pytest.mark.asyncio
async def test_state_entry_with_exception():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            entry = sf.behavior(AsyncMock(side_effect=Exception))

        initial = sf.initial(s1)

    sm = SM()
    with pytest.raises(Exception):
        await sm.interpreter.start()


@pytest.mark.asyncio
async def test_state_do_activity_with_exception():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            do_activity = sf.behavior(AsyncMock(side_effect=Exception))

        initial = sf.initial(s1)

    sm = SM()
    await sm.interpreter.start()
    with pytest.raises(Exception):
        await sm.interpreter.terminate()
