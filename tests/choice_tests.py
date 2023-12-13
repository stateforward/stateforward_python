import stateforward as sf
from tests.mock import mock, expect
import pytest


class ChoiceEvent(sf.Event):
    pass


class TestSMInterface:
    flag: int = 0

    async def should_transition_to_s2(self, event: sf.Event) -> bool:
        return self.model.flag == 0

    async def should_transition_to_s3(self, event: sf.Event) -> bool:
        return self.model.flag == 1

    async def transition_to_s2_effect(self, event: sf.Event) -> None:
        pass


class TestSM(sf.AsyncStateMachine, TestSMInterface):
    def __init__(self, flag: int = 0):
        self.flag = flag

    class s1(sf.State):
        pass

    class s2(sf.State):
        pass

    class s3(sf.State):
        pass

    initial = sf.initial(s1)
    choice_1 = sf.choice(
        sf.transition(
            target=s2,
            guard=TestSMInterface.should_transition_to_s2,
            effect=TestSMInterface.transition_to_s2_effect,
        ),
        sf.transition(
            target=s3,
            guard=TestSMInterface.should_transition_to_s3,
        ),
        sf.transition(target=s2),
    )

    transition_to_choice_1 = sf.transition(ChoiceEvent, source=s1, target=choice_1)


@pytest.mark.asyncio
async def test_choice_0():
    sm = mock(TestSM(flag=0))
    print(
        sm.__id__,
        sm.choice_1.__id__,
        sm.choice_1.outgoing[0].__id__,
        sm.choice_1.outgoing[1].__id__,
    )
    assert sm.choice_1.outgoing[0].target.__id__ == sm.s2.__id__

    await sm.__interpreter__.start()
    await sf.send(ChoiceEvent(), sm)
    expect.only(sm.s2).was_entered()
    assert sm.choice_1.outgoing[0].effect.activity.call_count == 1
    await sm.__interpreter__.terminate()


@pytest.mark.asyncio
async def test_choice_1():
    sm = mock(TestSM(flag=1))
    await sm.__interpreter__.start()
    await sf.send(ChoiceEvent(), sm)
    expect.only(sm.s3).was_entered()
    # expect.only(sm.choice_1.outgoing[0].effect).is_started()

    await sm.__interpreter__.terminate()


@pytest.mark.asyncio
async def test_choice_2():
    sm = mock(TestSM(flag=3))
    await sm.__interpreter__.start()
    await sf.send(ChoiceEvent(), sm)
    expect.only(sm.s2).was_entered()
    # expect.only(sm.choice_1.outgoing[0].effect).is_started()

    await sm.__interpreter__.terminate()
