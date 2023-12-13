import stateforward as sf
import asyncio
from dataclasses import dataclass
from datetime import timedelta, datetime


class DoorOpenEvent(sf.Event):
    pass


class DoorCloseEvent(sf.Event):
    pass


class OvenLightOnEvent(sf.Event):
    pass


class OvenLightOffEvent(sf.Event):
    pass


@dataclass(unsafe_hash=True)
class ExhaustFanOnEvent(sf.Event):
    speed: int = None


class ExhaustFanOffEvent(sf.Event):
    pass


class ClockSetEvent(sf.Event):
    time: datetime = None


@dataclass(unsafe_hash=True)
class CookStartEvent(sf.Event):
    duration: timedelta = None


@sf.decorators.behavior
def display_time(self, event: sf.Event = None):
    print(self.model.time.isoformat())


@sf.decorators.behavior
def display_clear(self, event: sf.Event):
    print("")


def throw(exception: Exception):
    raise exception


def door_is_open(self, event: sf.Event = None):
    return self.model.door.open in self.model.interpreter.stack


class Microwave(sf.AsyncStateMachine):
    """
    An example of a state machine for a microwave that doesn't use submachines
    """

    time: datetime = datetime.fromisoformat("2021-01-01T00:00:00")
    cook_time: timedelta = None

    @sf.decorators.call_event
    async def power_on(self):
        pass

    @sf.decorators.call_event
    async def power_off(self):
        pass

    class door(sf.Region):
        class open(sf.State):
            pass

        class closed(sf.State):
            pass

        initial = sf.initial(closed)
        transitions = sf.collection(
            sf.transition(DoorCloseEvent, source=open, target=closed),
            sf.transition(DoorOpenEvent, source=closed, target=open),
        )

    class power(sf.Region):
        class off(sf.State):
            pass

        class on(sf.State):
            class clock(sf.Region):
                class ticking(sf.State):
                    pass

                class flashing(sf.State):
                    class on(sf.State):
                        entry = sf.redefine(display_time)

                    class off(sf.State):
                        entry = sf.redefine(display_clear)

                    # initial = sf.initial(on)
                    flashing_transitions = sf.collection(
                        sf.transition(sf.after(seconds=2), source=on, target=off),
                        sf.transition(sf.after(seconds=2), source=off, target=on),
                    )

                initial = sf.initial(flashing.off)
                transitions = sf.collection(
                    sf.transition(
                        ClockSetEvent,
                        source=flashing,
                        target=ticking,
                        effect=lambda self, event: setattr(
                            self.model, "time", event.time
                        ),
                    ),
                    sf.transition(sf.after(seconds=1), source=ticking, target=ticking),
                )

            class light(sf.Region):
                class off(sf.State):
                    pass

                class on(sf.State):
                    pass

                initial = sf.initial(off)
                transitions = sf.collection(
                    sf.transition(
                        source=off, target=on, guard=door_is_open
                    ),  # completion transition
                    sf.transition(DoorCloseEvent, source=on, target=off),
                )

            class oven_light(sf.Region):
                class on(sf.State):
                    pass

                class off(sf.State):
                    pass

                initial = sf.initial(off)
                transitions = sf.collection(
                    sf.transition(OvenLightOnEvent, source=off, target=on),
                    sf.transition(
                        OvenLightOffEvent,
                        source=on,
                        target=off,
                    ),
                )

            # class cooking(sf.Region):
            class magnetron(sf.Region):
                off = sf.simple_state("off")
                on = sf.simple_state("on")

                initial = sf.initial(off)

            class turntable(sf.Region):
                class rotating(sf.State):
                    class clockwise(sf.State):
                        pass

                    class counterclockwise(sf.State):
                        pass

                    initial = sf.initial(clockwise)

                class off(sf.State):
                    pass

                initial = sf.initial(off)
                transitions = sf.collection(
                    sf.transition(CookStartEvent, source=off, target=rotating),
                    sf.transition(source=rotating, target=off, guard=door_is_open),
                )

            class exhaust_fan(sf.Region):
                def speed_is_high(self, event: ExhaustFanOnEvent) -> bool:
                    return event.speed == 3

                def speed_is_medium(self, event: ExhaustFanOnEvent) -> bool:
                    return event.speed == 2

                class on(sf.State):
                    low = sf.simple_state("low")
                    medium = sf.simple_state("medium")
                    high = sf.simple_state("high")

                speed_choice = sf.choice(
                    sf.transition(target=on.high, guard=speed_is_high),
                    sf.transition(target=on.medium, guard=speed_is_medium),
                    sf.transition(target=on.low),
                )

                off = sf.simple_state("off")

                initial = sf.initial(on.low)
                transition_to_off = sf.transition(
                    ExhaustFanOffEvent, source=on, target=off
                )

                # Transitioning to fan speed choice
                transition_to_fan_on = sf.transition(
                    ExhaustFanOnEvent,
                    source=(off, on),
                    target=speed_choice,
                )

        initial = sf.initial(on)

    transitions = sf.collection(
        sf.transition(power_on, source=power.off, target=power.on),
        sf.transition(power_off, source=power.on, target=power.off),
    )


if __name__ == "__main__":

    async def main():
        sf.dump(Microwave)
        microwave = Microwave()

        await microwave.interpreter.start()
        print(microwave.state)
        assert microwave.power.on in microwave.state
        print(microwave.state)

    asyncio.run(main())
