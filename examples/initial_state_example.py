import stateforward as sf
import asyncio


def make_region(initial_state: str = "S1"):
    class R(sf.Region):
        class S1(sf.State):
            pass

        class S2(sf.State):
            pass

        class S3(sf.State):
            pass

        initial = sf.initial(
            S1 if initial_state == "S1" else S2 if initial_state == "S2" else S3
        )

    return R


class SM(sf.AsyncStateMachine):
    R1 = make_region()
    R2 = make_region("S2")
    R3 = make_region("S3")


async def main():
    sf.dump(SM)
    sm = SM()
    await sm.interpreter.start()
    assert sm.state == (sm.R1.S1, sm.R2.S2, sm.R3.S3)


asyncio.run(main())
