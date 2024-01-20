import pytest
import stateforward as sf
from tests.mock import mock, expect
from unittest.mock import AsyncMock


@pytest.mark.asyncio
async def test_initial_simple():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            pass

        initial = sf.initial(s1)

    sm = mock(SM())
    await sm.interpreter.start()

    print(sm.state)
    expect.only(sm.s1).was_entered()
    # expect.only(sm.initial.transition).was_executed()
    await sm.interpreter.terminate()


@pytest.mark.asyncio
async def test_initial_multiple_regions():
    def create_sm(regions: int):
        class SM(sf.AsyncStateMachine):
            for x in range(regions):
                exec(
                    f"""class r{x}(sf.Region):
        class s1(sf.State):
            pass
        initial = sf.initial(s1)
                """
                )

        return SM

    for x in range(1, 10):
        SM = create_sm(x)
        sm = mock(SM())
        await sm.interpreter.start()
        regions = tuple(getattr(sm, f"r{x}") for x in range(x))
        expect.only(*(r.s1 for r in regions)).was_entered()
        expect.only(*(r.initial.transition for r in regions)).was_executed()
        await sm.interpreter.terminate()


#
@pytest.mark.asyncio
async def test_initial_to_nested_state():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            class s2(sf.State):
                class s3(sf.State):
                    pass

        class s4(sf.State):
            pass

        initial = sf.initial(s1.s2.s3)

    sm = mock(SM())
    await sm.interpreter.start()
    expect.only(sm.s1, sm.s1.s2, sm.s1.s2.s3).was_entered()
    expect.only(sm.initial.transition).was_executed()
    await sm.interpreter.terminate()


#
@pytest.mark.asyncio
async def test_initial_to_nested_state_with_completion_transition():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            class s2(sf.State):
                class s3(sf.State):
                    pass

        class s4(sf.State):
            pass

        initial = sf.initial(s1.s2.s3)
        transitions = sf.collection(sf.transition(source=s1.s2.s3, target=s4))

    sm = mock(SM())
    await sm.interpreter.start()
    print(sm.s1.entry.activity.call_count)
    assert sm.s1.entry.activity.call_count == 1, "s1 entry should be called once"
    expect.only(sm.s1, sm.s1.s2, sm.s1.s2.s3, sm.s4).was_entered()
    expect.all(sm.initial.transition, sm.transitions[0]).was_executed()
    await sm.interpreter.terminate()


@pytest.mark.asyncio
async def test_initial_effect():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            pass

        effect = AsyncMock()

        initial = sf.initial(s1, effect=effect)

    sm = mock(SM())
    await sm.interpreter.start()
    expect.only(sm.s1).was_entered()
    assert sm.effect.call_count == 1


@pytest.mark.asyncio
async def test_initial_effect_exception():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            pass

        async def effect(*args, **kwargs):
            raise Exception("This is an error")

        initial = sf.initial(s1, effect=effect)

    sm = mock(SM())
    with pytest.raises(Exception) as excinfo:
        await sm.interpreter.start()
        assert excinfo.value == "This is an error"


@pytest.mark.asyncio
async def test_initial_explicit_declaration():
    class SM(sf.AsyncStateMachine):
        class s1(sf.State):
            pass

        class initial(sf.Initial):
            pass

        initial_transition = sf.transition(source=initial, target=s1)

    sm = mock(SM())

    await sm.interpreter.start()
    expect.only(sm.s1).was_entered()


@pytest.mark.asyncio
async def test_initial_guard_prohibited():
    with pytest.raises(Exception) as excinfo:

        class SM(sf.AsyncStateMachine):
            class s1(sf.State):
                pass

            class initial(sf.Initial):
                pass

            guard = AsyncMock(return_value=False)

            initial_transition = sf.transition(source=initial, target=s1, guard=guard)
