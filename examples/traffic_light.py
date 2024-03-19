"""
# Overview of `stateforward.example.traffic_light.py` Module

The `stateforward.example.traffic_light.py` module is part of the `stateforward` package, which provides a framework for building state machines using the asyncio capabilities of Python. This specific module includes an example implementation of a traffic light state machine.

#### Features:
- Asynchronous state machine implementation for traffic lights.
- Custom events such as `PedestrianWalkButton` and `CarSensor`.
- Use of timers to automatically transition between states (`after` function).
- Guard functions that allow conditional transitions.

## Traffic Light Example Usage

Below is a possible sequence of operations for the `TrafficLight` state machine:

1. The traffic light starts in the `On` state with the `green` submachine state active.
2. When a `PedestrianWalkButton` event occurs, the light transitions to the `yellow` submachine state.
3. After 3 seconds (simulated by the `after` guard condition), the light transitions to the `red` submachine state.

## State Machine Diagram

Here is a mermaid.js diagram that visualizes the state machine for the traffic light example:

!!! example "Traffic Light"
    === "Signal Diagram"
        ```mermaid
        stateDiagram-v2
            direction LR
            Off: Off
            Off: entry / display(self)
            Off: exit / display(self)
            On: On
            On: entry / display(self)
            On: exit / display(self)
            [*] --> On
            On --> [*]
            On --> Off : after(1s) / guard self.flashing
            Off --> On : after(1s)

        ```
    === "Traffic Light Diagram"
        ```mermaid
        stateDiagram-v2
            direction LR
            state On {

            [*] --> green
            }

        ```
    === "Code"
```mermaid
stateDiagram-v2
    direction LR

    state On {
      initial --> green
      green --> yellow: PedestrianWalkButton
      yellow --> red: after(3s)
    }

    [*] --> On
    On --> Off: power_off
```

## Development Notes

### Event Classes

- `PedestrianWalkButton` - Represents the event of a pedestrian pressing the walk button.
- `CarSensor` - Represents the detection of a car waiting at the traffic light.
- `OffEvent` - Indicates that the traffic light has been turned off.
- `FlashingEvent` - Indicates the traffic light has entered a flashing state.

### Behavior Implementation

- `Signal` - A state machine used to represent a traffic signal mechanism that can switch between `On` and `Off` states.
- `TrafficLight` - A more complex state machine representing a traffic light system that can handle pedestrian interaction and power-off events.

### Guard Functions

- `walk_guard` - A guard function to allow the `Pedestrian` region to transition from `DontWalk` to `Walk`.

### Helper Functions

- `display` - A debugging function to visually display the traffic light's current state.

### Usage

To run the traffic light simulation, execute `traffic_light_main()` within an `asyncio` event loop, asynchronously starting the traffic light state machine and allowing for interaction through event dispatching.

### Concurrency

This example takes advantage of the `ConcurrencyKind.asynchronous` to ensure that the traffic light state machine runs in an asynchronous environment suitable for IO-bound and high-level structured network code.

"""
import stateforward as sf
import asyncio


class PedestrianWalkButton(sf.Event):
    pass


class CarSensor(sf.Event):
    pass


class OffEvent(sf.Event):
    pass


class FlashingEvent(sf.Event):
    pass


class WalkEvent(sf.Event):
    pass


class Signal(sf.AsyncStateMachine):
    flashing: bool = False

    class Off(sf.State):
        pass

    class On(sf.State):
        pass

    def set_flashing(self, *args, **kwargs):
        print("setting flashing to True")
        self.flashing = True

    initial = sf.initial(On)
    transitions = sf.collection(
        sf.transition(
            sf.after(seconds=0.5),
            source=On,
            target=Off,
            guard=lambda self, event: self.context.flashing,
        ),
        sf.transition(
            sf.after(seconds=0.5),
            source=Off,
            target=On,
            guard=lambda self, event: self.context.flashing,
        ),
        sf.transition(FlashingEvent, source=On, effect=set_flashing),
    )


def walk_guard(self, event):
    return self.model.On.red in self.model.interpreter.stack


def send_flashing_event(self, event):
    print("Sending flashing event")
    sf.send(FlashingEvent(), self.model)


def send_walk_event(self, event):
    # print("Sending walk event", self.model.On)
    sf.send(WalkEvent(), self.model)


class TrafficLight(sf.AsyncStateMachine):
    direction: str

    def __init__(self, direction: str):
        self.direction = direction
        super().__init__()

    @sf.decorators.call_event
    def power_off(self):
        pass

    class Off(sf.State):
        pass

    class On(sf.State):
        class Pedestrian(sf.Region):
            dont_walk = sf.submachine_state(Signal, name="dont_walk")

            walk = sf.submachine_state(Signal, name="walk")

            initial = sf.initial(target=dont_walk)
            transitions = sf.collection(
                sf.transition(
                    WalkEvent, source=dont_walk, target=walk, guard=walk_guard
                ),
                sf.transition(
                    sf.after(seconds=3),
                    source=walk,
                    effect=send_flashing_event,
                ),
            )

        red = sf.submachine_state(Signal, name="red", entry=send_walk_event)
        yellow = sf.submachine_state(Signal, name="yellow")
        green = sf.submachine_state(Signal, name="green")

        initial = sf.initial(target=green)

    initial = sf.initial(target=On)

    transitions = sf.collection(
        sf.transition(PedestrianWalkButton, source=On.green, target=On.yellow),
        sf.transition(sf.after(seconds=3), source=On.yellow, target=On.red),
        sf.transition(power_off, source=On, target=Off),
    )


DONT_WALK = "🚷"
WALK = "🚶"


def display(tl: "TrafficLight"):
    if tl.interpreter.is_active(tl.On.red):
        color = "🔴"
    elif tl.interpreter.is_active(tl.On.yellow):
        color = "🟡"
    elif tl.interpreter.is_active(tl.On.green):
        color = "🟢"
    else:
        color = "⚫️"
    if tl.interpreter.is_active(tl.On.Pedestrian.walk):
        pedestrian = WALK
    elif tl.interpreter.is_active(tl.On.Pedestrian.dont_walk):
        pedestrian = DONT_WALK
    else:
        pedestrian = None
    # else:
    #     pedestrian = "⚫️"
    formatting = {
        "🔴": "⚫️",
        "🟡": "⚫️",
        "🟢": "⚫️",
        DONT_WALK: "⚫️",
        WALK: "⚫️",
        color: color,
        pedestrian: pedestrian,
        "direction": tl.direction,
    }
    print(
        "{direction}\n＿＿\n⏐{🔴}⏐＿＿\n⏐{🟡}⏐⏐{🚷}⏐\n⏐{🟢}⏐⏐{🚶}⏐\n‾‾‾‾‾‾‾‾".format(
            **formatting
        )
    )


async def display_signal(tl):
    while True:
        await asyncio.sleep(1)
        display(tl)


async def traffic_light_main():
    tl = TrafficLight("north")
    asyncio.create_task(display_signal(tl))
    await tl.interpreter.start()
    await sf.send(PedestrianWalkButton(), tl)
    await asyncio.Future()


asyncio.run(traffic_light_main())
