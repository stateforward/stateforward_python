import pytest
import pytest_asyncio
import asyncio
from tests.mock import mocked, Mocked, mock, expect
from datetime import datetime
from examples.microwave import (
    Microwave,
    DoorOpenEvent,
    DoorCloseEvent,
    OvenLightOnEvent,
    OvenLightOffEvent,
    ExhaustFanOffEvent,
    ClockSetEvent,
    ExhaustFanOnEvent,
)
from stateforward.state_machine.log import create_logger


@pytest_asyncio.fixture
async def microwave():
    microwave = mock(Microwave())
    print("WE ARE STARTING HERE")
    await microwave.interpreter.start()
    yield microwave
    # await microwave.interpreter.terminate()


@pytest.mark.asyncio
async def test_microwave_initial_state(microwave: Mocked[Microwave]):
    expect.only(
        microwave.door.closed,
        microwave.power.on.light.off,
        microwave.power.on.oven_light.off,
        microwave.power.on.turntable.off,
        microwave.power.on.exhaust_fan.on.low,
        microwave.power.on,
        microwave.power.on.exhaust_fan.on,
        microwave.power.on.clock.flashing,
        microwave.power.on.clock.flashing.off,
        microwave.power.on.magnetron.off,
    ).was_entered()
    expect.only(
        microwave.door.initial.transition,
        microwave.power.initial.transition,
        microwave.power.on.light.initial.transition,
        microwave.power.on.oven_light.initial.transition,
        microwave.power.on.turntable.initial.transition,
        microwave.power.on.exhaust_fan.initial.transition,
        microwave.power.on.clock.initial.transition,
        microwave.power.on.magnetron.initial.transition,
    ).was_executed()


@pytest.mark.asyncio
async def test_door_open(microwave: Mocked[Microwave]):
    await microwave.dispatch(DoorOpenEvent())
    expect.only(microwave.door.open, microwave.power.on.light.on).was_entered()
    expect.only(microwave.door.closed, microwave.power.on.light.off).was_exited()


@pytest.mark.asyncio
async def test_door_close(microwave: Mocked[Microwave]):
    await test_door_open(microwave)
    await microwave.dispatch(DoorCloseEvent())
    expect.only(microwave.door.closed, microwave.power.on.light.off).was_entered()
    expect.only(microwave.door.open, microwave.power.on.light.on).was_exited()


@pytest.mark.asyncio
async def test_power_off(microwave: Mocked[Microwave]):
    await microwave.power_off()
    expect.only(microwave.power.off).was_entered()
    expect.only(
        microwave.power.on.light.off,
        microwave.power.on.oven_light.off,
        microwave.power.on.turntable.off,
        microwave.power.on,
        microwave.power.on.exhaust_fan.on,
        microwave.power.on.exhaust_fan.on.low,
        microwave.power.on.clock.flashing,
        microwave.power.on.clock.flashing.off,
        microwave.power.on.magnetron.off,
    ).was_exited()


@pytest.mark.asyncio
async def test_power_on(microwave: Mocked[Microwave]):
    await test_power_off(microwave)
    await microwave.power_on()
    await asyncio.sleep(
        0.1
    )  # TODO fix this we want the event to propagate through the interpreter
    expect.only(
        microwave.power.on.light.off,
        microwave.power.on.oven_light.off,
        microwave.power.on.turntable.off,
        microwave.power.on.exhaust_fan.on.low,
        microwave.power.on,
        microwave.power.on.exhaust_fan.on,
        microwave.power.on.clock.flashing,
        microwave.power.on.clock.flashing.off,
        microwave.power.on.magnetron.off,
    ).was_entered()
    expect.only(microwave.power.off).was_exited()


@pytest.mark.asyncio
async def test_exhaust_fan_off(microwave: Mocked[Microwave]):
    await microwave.dispatch(ExhaustFanOffEvent())
    assert microwave.power.on.exhaust_fan.transition_to_off.was_executed()
    expect.only(
        microwave.power.on.exhaust_fan.on, microwave.power.on.exhaust_fan.on.low
    ).was_exited()
    expect.only(microwave.power.on.exhaust_fan.off).was_entered()


@pytest.mark.asyncio
async def test_exhaust_fan_on_high(microwave: Mocked[Microwave]):
    await microwave.dispatch(ExhaustFanOnEvent(speed=3))
    expect.only(
        microwave.power.on.exhaust_fan.on.high, microwave.power.on.exhaust_fan.on
    ).was_entered()
    expect.only(microwave.power.on.exhaust_fan.on.low).was_exited()
    expect.only(
        microwave.power.on.exhaust_fan.transition_to_fan_on[1],
        microwave.power.on.exhaust_fan.speed_choice.outgoing[0],
    ).was_executed()
    await microwave.dispatch(ExhaustFanOffEvent())
    expect.only(microwave.power.on.exhaust_fan.off).was_entered()
    expect.only(
        microwave.power.on.exhaust_fan.on.high, microwave.power.on.exhaust_fan.on
    ).was_exited()


@pytest.mark.asyncio
async def test_exhaust_fan_on_medium(microwave: Mocked[Microwave]):
    await microwave.dispatch(ExhaustFanOnEvent(speed=2))
    expect.only(
        microwave.power.on.exhaust_fan.on.medium, microwave.power.on.exhaust_fan.on
    ).was_entered()
    expect.only(microwave.power.on.exhaust_fan.on.low).was_exited()
    expect.only(
        microwave.power.on.exhaust_fan.transition_to_fan_on[1],
        microwave.power.on.exhaust_fan.speed_choice.outgoing[1],
    ).was_executed()
    await microwave.dispatch(ExhaustFanOffEvent())
    expect.only(microwave.power.on.exhaust_fan.off).was_entered()
    expect.only(
        microwave.power.on.exhaust_fan.on.medium, microwave.power.on.exhaust_fan.on
    ).was_exited()


@pytest.mark.asyncio
async def test_exhaust_fan_off(microwave: Mocked[Microwave]):
    await microwave.dispatch(ExhaustFanOffEvent())
    expect.only(microwave.power.on.exhaust_fan.off).was_entered()
    expect.only(
        microwave.power.on.exhaust_fan.on.low, microwave.power.on.exhaust_fan.on
    ).was_exited()


@pytest.mark.asyncio
async def test_oven_light_region(microwave: Mocked[Microwave]):
    await microwave.dispatch(OvenLightOnEvent())
    expect.only(microwave.power.on.oven_light.on).was_entered()
    expect.only(microwave.power.on.oven_light.off).was_exited()
    expect.only(microwave.power.on.oven_light.transitions[0]).was_executed()
    await microwave.dispatch(OvenLightOffEvent())
    expect.only(microwave.power.on.oven_light.off).was_entered()
    expect.only(microwave.power.on.oven_light.on).was_exited()
    expect.only(microwave.power.on.oven_light.transitions[1]).was_executed()


@pytest.mark.asyncio
async def test_clock_flashing(microwave: Mocked[Microwave]):
    microwave.reset_mocked()
    await asyncio.sleep(2.1)
    expect.only(microwave.power.on.clock.flashing.on).was_entered()
    expect.only(microwave.power.on.clock.flashing.off).was_exited()
    microwave.reset_mocked()
    await asyncio.sleep(2.1)
    expect.only(microwave.power.on.clock.flashing.off).was_entered()
    expect.only(microwave.power.on.clock.flashing.on).was_exited()


@pytest.mark.asyncio
async def test_clock_set(microwave: Mocked[Microwave]):
    await microwave.dispatch(ClockSetEvent(time=datetime.now()))
    expect.only(microwave.power.on.clock.ticking).was_entered()


# @pytest.mark.asyncio
# async def test_cook_start(microwave: Mocked[Microwave]):
#     pass
