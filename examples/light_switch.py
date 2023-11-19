"""
## Introduction

The `light_switch` module is part of the `stateforward` examples and showcases the implementation of an asynchronous state machine to model the behavior of a light switch. The example defines states for the light switch, such as `On`, `Off`, and `Flashing`, as well as events that trigger state transitions, such as turning the light `OnEvent` or `OffEvent`.
!!! example "Light Switch Example"
    === "Diagram"
        Here is a simple example of a light switch state machine using StateForward Python.
        ``` mermaid
        stateDiagram-v2
            direction LR
            Off: Off
            Off: entry / print("Light off entry")
            Off: exit / print("Light off exit")
            [*] --> Off
            On: On
            On: entry / print("Light on entry")
            On: exit / print("Light on exit")
            Off --> On : OnEvent
            On --> Off : OffEvent


        ```
    === "Code"
        ```python
        import stateforward as sf
        import asyncio


        class OnEvent(sf.Event):
            pass


        class OffEvent(sf.Event):
            pass


        class LightSwitch(sf.AsyncStateMachine):
            class On(sf.State):
                @sf.decorators.behavior
                async def entry(self, event: OnEvent):
                    print("Light on entry")

                @sf.decorators.behavior
                async def exit(self, event: OffEvent):
                    print("Light on exit")

            class Off(sf.State):
                @sf.decorators.behavior
                async def entry(self, event: OnEvent):
                    print("Light off entry")

                @sf.decorators.behavior
                async def exit(self, event: OffEvent):
                    print("Light off exit")

            initial = sf.initial(Off)
            transitions = sf.collection(
                sf.transition(OnEvent, source=Off, target=On),
                sf.transition(OffEvent, source=On, target=Off),
            )


        async def main():
            # instantiate a light switch
            light_switch = LightSwitch()
            # start the interpreter and wait for it to be settled
            await light_switch.interpreter.start()
            # output the current states of the state machine
            print(light_switch.state)
            # dispatch a OnEvent to the state machine
            await sf.dispatch(OnEvent(), light_switch)
            # output the current states of the state machine
            print(light_switch.state)
            # dispatch a OffEvent to the state machine
            await sf.dispatch(OffEvent(), light_switch)
            print(light_switch.state)


        asyncio.run(main())
        ```
    === "Output"
        ```bash
        Light off entry
        (<__main__.LightSwitch.region.region_0.Off object at 0x10683e590>,)
        Light off exit
        Light on entry
        (<__main__.LightSwitch.region.region_0.On object at 0x10683dd90>,)
        Light on exit
        Light off entry
        (<__main__.LightSwitch.region.region_0.Off object at 0x10683e590>,)
        Light off exit
        ```

## Components of the Light Switch State Machine

### Events

- `OnEvent`: An event representing the action of turning the light on.
- `OffEvent`: An event representing the action of turning the light off.
- `FlashEvent`: An event that triggers the flashing mode, derived from the custom `ChangeEvent`.

### States

- `On`: The state representing the light being turned on.
- `Off`: The state representing the light being turned off.
- `Flashing`: The state representing the light in a flashing mode. Transition to this state is determined by the condition `lambda self, event=None: self.model.flashing`.

### Behaviors

The module defines `PrintBehavior` as a simple behavior that prints a message to the console upon entering and exiting states.

## Defining the Light Switch State Machine

The `LightSwitch` state machine is derived from `AsyncStateMachine` and specifies the states and transitions. It includes an attribute `flashing`, which is a boolean flag used to conditionally trigger the flashing state.

## Transitions

Transitions between states are defined using the `transition` function from the `stateforward` framework; it specifies what event causes the transition, the source state, and the target state, along with optional guards and effects.

## Asynchronous Operation

The state machine is designed to operate asynchronously, making use of Python's `asyncio` library. This allows for concurrent operation within an event-driven system.

## Running the Example

The module includes an asynchronous `light_switch_main` function that initializes the state machine, starts it, and dispatches events to trigger state transitions. One can observe the behavior of the light switch by calling this function within an event loop.

## Conclusion

The `stateforward.example.light_switch` module serves as an educational tool for understanding the `stateforward` framework and is an example of how to model and simulate a simple system with state machines in Python.

---

To learn more about other parts of the `stateforward` framework or to adapt the light switch example for your own use case, please refer to the rest of the documentation.
"""
import stateforward as sf
import asyncio


class OnEvent(sf.Event):
    pass


class OffEvent(sf.Event):
    pass


class PrintBehavior(sf.Behavior):
    def activity(self, event: sf.Event = None):
        print(
            f"{self.qualified_name}<{id(self)}> -> {event.qualified_name if event is not None else None}"
        )


class LightSwitch(sf.AsyncStateMachine):
    flashing = False
    FlashEvent = sf.change(lambda self, event=None: self.model.flashing)

    class On(sf.State):
        entry = sf.bind(PrintBehavior)
        exit = sf.bind(PrintBehavior)

    class Off(sf.State):
        entry = sf.bind(PrintBehavior)
        exit = sf.bind(PrintBehavior)

    class Flashing(sf.State):
        pass

    initial = sf.initial(Off)
    transitions = sf.collection(
        sf.transition(OnEvent, source=Off, target=On),
        sf.transition(OffEvent, source=On, target=Off),
        sf.transition(FlashEvent, source=Off, target=Flashing),
    )


async def light_switch_main():
    light_switch = LightSwitch()
    await light_switch.interpreter.start()  # awaiting the event ensures the state machine is idle before we send an event
    print(light_switch.state)
    await sf.dispatch(OnEvent(), light_switch)
    print(light_switch.state)
    await sf.dispatch(OffEvent(), light_switch)
    print(light_switch.state)
    light_switch.flashing = True
    await asyncio.sleep(2)
    print(light_switch.state)
    print(light_switch, light_switch.flashing)


asyncio.run(light_switch_main())
