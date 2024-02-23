from unittest.mock import AsyncMock

import pytest
import stateforward as sf


class TestSM(sf.AsyncStateMachine):
    class s1(sf.State):
        entry = sf.behavior(AsyncMock())
        activity = sf.behavior(AsyncMock())
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
async def test_state_activity_with_exception():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            activity = sf.behavior(AsyncMock(side_effect=Exception))

        initial = sf.initial(s1)

    sm = SM()
    await sm.interpreter.start()
    with pytest.raises(Exception):
        await sm.interpreter.terminate()


@pytest.mark.asyncio
async def test_final_state():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            pass

        class s2(sf.State):
            pass

        initial = sf.initial(s1)

        final = sf.final_state()

        transitions = sf.collection(
            sf.transition(source=s1, target=s2),
            sf.transition(source=s2, target=final),
        )

    sm = SM()
    await sm.interpreter.start()
    assert sm.interpreter.is_active() is False
