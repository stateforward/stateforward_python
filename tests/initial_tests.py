import pytest
import stateforward as sf
from tests.mock import mock, expect


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

        initial = sf.initial(s1.s2.s3)

    sm = mock(SM())
    await sm.interpreter.start()
    expect.only(sm.s1, sm.s1.s2, sm.s1.s2.s3).was_entered()
    expect.only(sm.initial.transition).was_executed()
    await sm.interpreter.terminate()
