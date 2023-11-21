"""
![alt text](/assets/complete_statemachine.svg "Title")
"""
import stateforward as sf

e1 = sf.event("e1")


class e2(sf.Event):
    pass


e3 = sf.event("e3")


class Sample(sf.AsyncStateMachine):
    class s2(sf.State):
        class r1(sf.Region):
            class s1(sf.State):
                pass

            class s2(sf.State):
                pass

            initial = sf.initial(s1)

        class r2(sf.Region):
            class s1(sf.State):
                pass

            class s2(sf.State):
                pass

            initial = sf.initial(s2)

    initial = sf.initial(s2)

    entry_point_to_r2_s2 = sf.entry_point(sf.transition(target=s2.r2.s2))
    entry_point_to_r1_s2_and_r2_s1 = sf.entry_point(
        sf.transition(target=s2.r1.s2), sf.transition(target=s2.r2.s1)
    )
    exit_point_from_r2_s2 = sf.exit_point()
    r2_s2_to_exit_point = sf.transition(source=s2.r2.s2, target=exit_point_from_r2_s2)


class CompleteSM(sf.AsyncStateMachine):
    a1: int = 0

    s0 = sf.simple_state("s0")

    class s1(sf.State):
        class r1(sf.Region):
            class s1(sf.State):
                pass

            class s2(sf.State):
                pass

        r1_s1_to_r1_s2 = sf.transition(e1, source=r1.s1, target=r1.s2)
        r1_s2_to_r1_s1 = sf.transition(sf.after(seconds=1), source=r1.s2, target=r1.s1)

        class r2(sf.Region):
            class s1(sf.State):
                pass

            class s2(sf.State):
                pass

        r2_s2_to_r2_s1 = sf.transition(e2, source=r2.s2, target=r2.s1)
        r2_s1_to_r2_s2 = sf.transition(
            sf.when(lambda self: self.model.a1), source=r2.s1, target=r2.s2
        )

    s2 = sf.submachine_state(Sample, name="s2")

    initial = sf.initial(s0)
    s0_fork = sf.fork(sf.transition(target=s1.r1.s1), sf.transition(target=s1.r2.s2))
    s1_join = sf.join(s2)

    s1_r1_s1_transition_to_s1_join = sf.transition(source=s1.r1.s1, target=s1_join)
    s1_r2_s2_transition_to_s1_join = sf.transition(source=s1.r2.s1, target=s1_join)

    s1_transtion_to_s2_s1 = sf.transition(e3, source=s1, target=s2.s2)

    fork_transition = sf.transition(e2, source=s0, target=s0_fork)


if __name__ == "__main__":
    import asyncio

    async def main():
        sf.dump(CompleteSM)
        sm = CompleteSM()

        await sm.interpreter.start()
        print(sm.state)

    asyncio.run(main())
