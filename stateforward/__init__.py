"""
!!! warning "StateForward Python is in alpha"
    This is a work in progress and is not ready for production use yet. The API and implementation are subject to changes on minor versions.
    See the Roadmap for planned features and the [Contributing](#contributing) section for ways to contribute.

## About StateForward Python
StateForward Python is where code complexity meets simplicity.
This library is your ally in evolving spaghetti code into elegant, robust state machines.
Say goodbye to the dense forest of if-else statements and welcome a world where adding features doesn’t mean unraveling a complex knot.

With StateForward Python, you’re building on solid ground.
Your code becomes a clear map of states and transitions, making it easily extendable and a joy to maintain.
It's about writing software that grows with grace, ensuring that your project's future is as structured and reliable as its present.

## Installation

```bash
pip install stateforward
```

## Usage
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

"""
from . import elements
from .elements import *

from . import state_machine
from .state_machine import *
from . import model
from .model import *
from . import protocols
