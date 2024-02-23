"""

## Microwave Module Documentation

The `microwave` module defines an asynchronous state machine representing the behavior and operations of a microwave appliance using the `stateforward` (aliased as `sf`) library. This module includes the definition of various events, behaviors, and the `Microwave` class, which is an extension of `sf.AsyncStateMachine`.

### Classes and Events

- **Microwave:** This is the main class representing a microwave. It is an asynchronous state machine with states and transitions that simulate the different functionalities of a microwave.
  - Includes states such as `door`, `power`, `clock`, `light`, `oven_light`, `magnetron`, `turntable`, and `exhaust_fan`.
  - Contains methods `power_on` and `power_off` to simulate the power control.

- **DoorOpenEvent, DoorCloseEvent:** Represent the events of the microwave's door being opened or closed.

- **OvenLightOnEvent, OvenLightOffEvent:** Represent the events of turning the oven light on or off.

- **ExhaustFanOnEvent, ExhaustFanOffEvent:** Represent events for turning the exhaust fan on with various speeds, or turning it off.

- **ClockSetEvent:** Represents the event of setting the microwave's clock.

- **CookStartEvent:** Represents the event of starting the cooking process with a set duration.

### Behaviors

- **display_time:** A behavior function for displaying the current time of the microwave's clock.

- **display_clear:** A behavior function for clearing the display.

### Helper Functions

- **throw:** A helper function that raises an exception.

- **door_is_open:** A helper function to check if the microwave's door is open.

### Microwave2

- **Microwave2:** A class that inherits from `Microwave`, allowing for potential extension or customization.

### Module Execution

If this module is run as the main program, an instance of `Microwave` is created and the state machine is started, demonstrating its initial state and behaviors after power on event.

## State Machine Description

The `Microwave` class uses nested states and regions to define the complex behavior of the microwave appliance. Each feature of a microwave, like the door, power, clock, and light, are implemented as regions with their own states and transitions. This modular design allows each feature to operate semi-independently, resulting in a comprehensive simulation of a microwave's functionalities.

The state machine also makes use of asynchronous programming by defining states and transitions that are meant to be awaited. This means the state machine can work well with other asynchronous operations, making it suitable for integration in an event-driven or non-blocking runtime environment.

## Developer Notes

While the module does not include usage and example sections, the detailed class and method definitions provide a clear indication of how the microwave state machine is intended to be used and extended. Developers can use this module as a starting point for building state machines for appliances or other systems that require complex state management with asynchronous behavior.
"""
import stateforward as sf
import asyncio
from dataclasses import dataclass
from datetime import timedelta, datetime


class DoorOpenEvent(sf.Event):
    """
    A simple class that represents a 'door open' event within a system or application.
    This class serves as a marker or signal indicating that a door has been opened. It is intended for use as part of an event-driven architecture where components of the system respond to various events. The DoorOpenEvent does not include any additional data or functionality and is typically subclassed or instantiated by event-handling mechanisms to notify listeners or observers that a door has been opened.
    
    Attributes:
        Inherits all attributes from the `sf.Event` base class, but does not add any attributes of its own.

    """
    pass


class DoorCloseEvent(sf.Event):
    """
    A class representing an event that signifies the closing of a door.
    Inherits from the `sf.Event` class provided by the framework in use. This class
    serves as a specific type of event that can be dispatched and listened for within
    an event-driven architecture. It does not have any additional attributes or
    methods beyond what is provided by its parent class `sf.Event`.
    
    Attributes:
        inherited attributes from `sf.Event`.

    """
    pass


class OvenLightOnEvent(sf.Event):
    """
    A simple event class that signifies that the oven light has been turned on.
    This class inherits from `sf.Event` and represents a specific event that can be used
    in applications that monitor or handle states of an oven, particularly the state
    of the oven light. It does not hold any additional data or methods; it serves as
    a signaling mechanism for event-driven systems to indicate the occurrence of the
    oven light being turned on.

    """
    pass


class OvenLightOffEvent(sf.Event):
    """
    A class representing an event where the oven light is turned off.
    This class serves as a specific event type within an event-driven system or framework
    dealing with an oven's state changes. It inherits from `sf.Event`, presumable a base
    event class provided by the system's framework. The `OvenLightOffEvent` class does
    not add any additional attributes or methods; it functions as a simple, semantic
    indicator for when the oven light is deactivated.
    
    Attributes:
        Inherits all attributes from the base class `sf.Event`.
    
    Methods:
        Inherits all methods from the base class `sf.Event`.

    """
    pass


@dataclass(unsafe_hash=True)
class ExhaustFanOnEvent(sf.Event):
    """
    A data class representing an event to turn on the exhaust fan of a microwave.
    This event includes a speed attribute which denotes the desired speed level for the exhaust fan.
    The speed level is an integer that should correspond to a predetermined setting within the microwave's system.
    This class is a subclass of `sf.Event` from the library providing the state machine functionality.
    
    Attributes:
        speed (int):
             The speed level for the exhaust fan. The actual use of this value depends on implementation
            details of the microwave's state machine. If not specified, it defaults to `None` indicating
            that no specific speed level is set with this event.

    """
    speed: int = None


class ExhaustFanOffEvent(sf.Event):
    """
    A simple event class that signifies an exhaust fan has been turned off.
    This class is a subclass of `sf.Event` and does not introduce additional methods or attributes. It is used within an event-driven system to indicate when an exhaust fan has ceased operation. The class serves as a signal within systems that track or respond to exhaust fan states.
    
    Attributes:
        Inherits all attributes from `sf.Event` without modification.
    
    Note:
        This class should be used in the context of an event-driven architecture, where it can be dispatched to event listeners that handle the turning off of an exhaust fan accordingly.

    """
    pass


class ClockSetEvent(sf.Event):
    """
    A class representing an event that triggers when the clock time is set.
    This class inherits from sf.Event and encapsulates functionality related to clock time-setting events.
    It contains a single class attribute 'time' that stores the datetime when the event is set.
    
    Attributes:
        time (datetime, optional):
             The date and time when the clock is set. Defaults to None. This attribute
            is meant to be populated with the specific datetime when an instance of ClockSetEvent is created.

    """
    time: datetime = None


@dataclass(unsafe_hash=True)
class CookStartEvent(sf.Event):
    """
    A data class representing an event that triggers the start of the cooking process in a microwave.
    
    Attributes:
        duration (timedelta, optional):
             The length of time for which the cooking process needs to run.

    """
    duration: timedelta = None


@sf.decorators.behavior
def display_time(self, event: sf.Event = None):
    """
    Displays the current time in ISO 8601 format.
    This is a state machine behavior method that prints the time attribute of the state
    machine's model. If an event triggers this behavior, the event is ignored as it
    is not utilized within the method.
    
    Args:
        event (Optional[sf.Event]):
             The event that triggered this behavior, which is
            not utilized within the function. It defaults to None if not provided.

    """
    print(self.model.time.isoformat())


@sf.decorators.behavior
def display_clear(self, event: sf.Event):
    """
    Clears the microwave display by printing an empty line.
    This function is designed to be a behavior callback associated with state transitions
    where the microwave display needs to be cleared. It takes an event, but does not
    use it within the function body, printing an empty line to the standard output regardless
    of the event.
    
    Args:
        event (sf.Event):
             The event that triggers this behavior. It is unused inside the function.

    """
    print("")


def throw(exception: Exception):
    """
    
    Raises a specified exception.
    
    Args:
        exception (Exception):
             The exception object to be raised.
    
    Raises:
        Exception:
             The exception passed to the function.

    """
    raise exception


def door_is_open(self, event: sf.Event = None):
    """
    Determines if the door is currently open by checking the state against the interpreter stack.
    
    Args:
        event (sf.Event, optional):
             The event object which can optionally be used to determine the door's state. Defaults to None.
    
    Returns:
        (bool):
             True if the door's 'open' state is present in the interpreter stack, False otherwise.

    """
    return self.model.door.open in self.model.interpreter.stack


class Microwave(sf.AsyncStateMachine):
    """
    A class representing an asynchronous state machine for a microwave oven.
    This class models the microwave's behavior using various regions that represent different aspects of the microwave's functionality. Each region is made up of states and transitions that define how the microwave reacts to events and changes in condition. The available regions include power, door, clock, light, oven light, magnetron, turntable, and exhaust fan, with each having its own set of states and transitions.
    
    Attributes:
        time (datetime):
             The current time of the microwave's clock, initialized to a default value.
        cook_time (timedelta):
             The duration for which cooking should occur; can be set to a specific duration.
    
    Methods:
        power_on:
             Asynchronously triggered event which can cause a transition from the 'off' to 'on' power state.
        power_off:
             Asynchronously triggered event which can cause a transition from the 'on' to 'off' power state.
            Each region has its own inner classes defining the states and transitions associated with that region
            - The power region defines the behavior of the microwave when turning on and off.
            - The door region manages the states related to the microwave door being open or closed.
            - The clock region has states for the clock being in a ticking or flashing state.
            - The light region controls the light inside the microwave, turning on when the door is opened.
            - The oven light region controls the oven's cavity light.
            - The magnetron region controls the state of the microwave's magnetron, responsible for generating the microwaves.
            - The turntable region manages the rotation of the turntable inside the microwave.
            - The exhaust fan region handles the operation of the exhaust fan at different speeds.
            Transitions between states are defined for each region, dictated by events that trigger these state changes. Guards can be applied on transitions to add conditions for the transition to occur.
    
    Note:
        sf abbreviates the module used for creating the state machine framework, which is not defined in this docstring.

    """

    time: datetime = datetime.fromisoformat("2021-01-01T00:00:00")
    cook_time: timedelta = None

    @sf.decorators.call_event
    async def power_on(self):
        """
        Asynchronously powers on the system or device linked to the class instance.
        This method is designed to be triggered as an event, indicated by the `call_event` decorator. It performs the necessary actions to initiate the power-on process but contains no implementation within the definition provided.
        
        Raises:
            This method is not documented to raise any exceptions, but since it is a placeholder, exceptions could be raised in concrete implementations depending on the actions performed while powering on the system.
        
        Returns:
            The return value is not specified in this context, as the implementation of the method is yet to be defined. It is expected to return a value, typically a coroutine or a future, that the async event loop can await, or it might simply execute an action without returning anything if the power on operation is instantaneous.

        """
        pass

    @sf.decorators.call_event
    async def power_off(self):
        """
        Asynchronously powers off a device or system.
        This method serves as an event trigger for initiating a shutdown sequence.
        It is adorned with a decorator indicating that it is meant to be treated
        as a callable event within the system. The exact side-effects are determined by
        the underlying implementation which should be designed to perform the
        shutdown process asynchronously.
        The function is a coroutine, it must be awaited when invoked, and it
        may need to be called as part of an event loop in asynchronous workflows.
        No arguments are required or processed, and the method does not return any value.
        Since this function does not take any parameters and does not provide a return
        value, the primary use-case is to signal other parts of the application that a
        power off event is requested, upon which those parts can take the necessary
        shutdown or cleanup actions.

        """
        pass

    class door(sf.Region):
        """
        A class representing the door state within the microwave state machine.
        
        Attributes:
            initial:
                 The initial state which is set to 'closed' when the microwave's door state machine is initiated.
            States:
            open:
                 A state representing the door being open.
            closed:
                 A state representing the door being closed.
            Transitions:
            A collection of transitions that define the change of states:
                - When a `DoorCloseEvent` occurs, the door transitions from the 'open' state to the 'closed' state.
                - When a `DoorOpenEvent` occurs, the door transitions from the 'closed' state to the 'open' state.

        """
        class open(sf.State):
            """
            A class representing an open state within a state machine.
            This class inherits from State (`sf.State`) and is used to represent a state that is considered 'open'. Typically, this would imply that the state
            allows for certain operations to occur that may not be permissible in other states. As a subclass of `sf.State`, instances of `open` will have all the methods and attributes provided by the parent class. It serves as a template for creating more specific open states that would inherit from this class, providing a clear indication of their functionality within the system.
            
            Attributes:
                Inherits all attributes from the parent class `sf.State`.
            
            Methods:
                Inherits all methods from the parent class `sf.State`.

            """
            pass

        class closed(sf.State):
            """
            Represents a state indicating that something is in a closed condition.
            This class is derived from `sf.State` and typically represents a state in a
            state machine or similar systems to indicate a closed status.
            
            Attributes:
                Inherits all attributes from the parent class `sf.State`.

            """
            pass

        initial = sf.initial(closed)
        transitions = sf.collection(
            sf.transition(DoorCloseEvent, source=open, target=closed),
            sf.transition(DoorOpenEvent, source=closed, target=open),
        )

    class power(sf.Region):
        """
        A class representing the power region of a state machine in the context of a microwave appliance.
        This class encapsulates the states and transitions related to the power functionality of a microwave oven, and it is divided into several nested regions each representing a different aspect of the microwave's operation when powered on.
        
        Attributes:
            off (sf.State):
                 A simple state representing the microwave being powered off.
            on (sf.State):
                 A state representing the microwave being powered on with several nested regions:
            clock (sf.Region):
                 A region to manage the state of the microwave's clock which can be ticking or flashing.
            light (sf.Region):
                 A region to manage the state of the microwave's internal light, which can be on or off.
            oven_light (sf.Region):
                 A region to manage the state of the oven light.
            magnetron (sf.Region):
                 A region to manage the state of the microwave's magnetron, responsible for heating the food.
            turntable (sf.Region):
                 A region that manages the state of the rotating turntable within the microwave.
            exhaust_fan (sf.Region):
                 A region to manage the exhaust fan's state which can vary in speed.
        
        Methods:
            - There are no public methods defined in the 'power' class as the functionality is encapsulated within.

        """
        class off(sf.State):
            """
            A state class representing the 'off' state, inheriting from `sf.State`.
            This class is typically used to represent a state in a state machine where 'off' signifies
            that a particular component, feature, or system is in an inactive or non-operational state.
            Since it is an empty class, it serves as a placeholder or a default state with no
            additional functionality beyond what is provided by the `sf.State` base class.

            """
            pass

        class on(sf.State):
            """
            A state modeling class within a microwave oven control state machine that encapsulates several regions
            representing different aspects of the oven's behavior when it is in the 'on' state.
            The class defines regions for the clock, light, oven light, magnetron, turntable, and
            exhaust fan. Each region further contains states and transitions that model the specific
            behavior of that component.
            The clock region transitions between ticking and flashing states, with the flashing state
            providing on and off substates toggled every two seconds to flash the display.
            The light region models the simple on/off behavior of the oven light based on
            the door being open.
            The oven light region also controls the on/off state of an additional light source within
            the oven, possibly for internal lighting, based on external events.
            The magnetron region models the on/off behavior of the component that generates microwaves.
            The turntable region manages the behavior of the oven's rotating plate, allowing it to turn
            clockwise, counter-clockwise, or to be off, with transitions based on cooking events and door status.
            The exhaust fan region models more detailed behavior of the oven's fan, accounting for
            multiple speed settings (low, medium, high), and transitions between these speeds or off
            states based on events reflecting changes in fan speed or an event signaling the fan to turn off.
            This class is expected to be used within a larger state machine framework for a microwave oven,
            responding to various events such as clock setting, door opening or closing, cooking start, and
            exhaust fan operation changes.

            """
            class clock(sf.Region):
                """
                A region that represents the clock functionality within a state machine context.
                The clock has two main states, 'ticking' and 'flashing', which represent its behavior. The 'flashing' state itself
                contains two substates, 'on' and 'off', which toggle to simulate the flashing effect of the clock display.
                The flashing transition occurs every 2 seconds between the 'on' and 'off' states.
                
                Attributes:
                    ticking (sf.State):
                         Represents the clock in a steady state, where time progresses normally.
                    flashing (sf.State):
                         Represents the clock display in a flashing mode, useful for indicating when the time is unset or should be set.
                    Transitions:
                        A transition from the 'flashing' to 'ticking' state is triggered by a ClockSetEvent. This transition sets the clock's time based on the event's time attribute.
                        A self-transition on the 'ticking' state is set to occur every second, simulating the progression of time in this state.
                    Entry Actions:
                    display_time:
                         A function called upon entering the 'on' substate of 'flashing' to display the current time.
                    display_clear:
                         A function called upon entering the 'off' substate of 'flashing' to clear the display or make it blank.

                """
                class ticking(sf.State):
                    """
                    A class that represents the 'ticking' state in a state machine.
                    This class inherits from the 'sf.State' which is likely a part of a state framework or library. The 'ticking' state could represent a periodic or continuous action within the state machine context. As it currently stands without additional methods or properties, it serves as a placeholder or default implementation for the 'ticking' behavior in the state machine.
                    
                    Attributes:
                        Inherited from sf.State, the attributes will depend on what is defined in the sf.State class. The 'ticking' class does not define any additional attributes.

                    """
                    pass

                class flashing(sf.State):
                    """
                    A state machine class representing the flashing state of a microwave's clock.
                    
                    Attributes:
                        on (sf.State):
                             A nested state indicating that the microwave's clock display is on. An entry
                            action is defined to display the current time.
                        off (sf.State):
                             A nested state indicating that the microwave's clock display is off. An entry
                            action is defined to clear the display.
                        Transitions:
                        flashing_transitions (sf.collection):
                             A set of transitions that toggle between the 'on' and 'off' states at a specified
                            interval. Transitions occur after a 2-second delay, creating a blinking effect for the clock display.

                    """
                    class on(sf.State):
                        """
                        Class representing the 'on' state within a state machine.
                        This class extends sf.State and has a single behavior defined by the 'entry' attribute, which is a method
                        that should be executed when entering this state. The 'entry' attribute is linked to the 'display_time' function,
                        indicating that the current time should be displayed when the microwave is in the 'on' state.
                        
                        Attributes:
                            entry:
                                 A method to be executed upon entry to the 'on' state, which is defined by the
                                display_time function.

                        """
                        entry = sf.redefine(display_time)

                    class off(sf.State):
                        """
                        A state class representing the 'off' state in a state machine context.
                        
                        Attributes:
                            entry (method):
                                 A method that is bound to the 'entry' action of this state. It overrides the
                                'display_clear' function to clear the display when the microwave enters the 'off' state.

                        """
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
                """
                A region defining the behavior of the microwave's interior light.
                The light region has two states indicating whether the light is turned off or on. Transitions between these states are based on the door events of the microwave. If the door is open, the light turns on, and it turns off when the door is closed.
                
                Attributes:
                    off (sf.State):
                         The state representing the light being turned off.
                    on (sf.State):
                         The state representing the light being turned on.
                    Transitions:
                        A transition from 'off' to 'on' state guarded by the 'door_is_open' condition.
                        A transition from 'on' to 'off' state triggered by `DoorCloseEvent`.

                """
                class off(sf.State):
                    """
                    A class representing an inactive or 'off' state within a finite state machine.
                    This class is a simple subclass of the `sf.State` class, which is presumably a part of a state machine
                    framework. The `off` class does not define any additional attributes or methods and serves as a
                    placeholder for representing an 'off' state within the state machine. It can be used to signify
                    that a particular component or system is in an inactive state.
                    
                    Attributes:
                        Inherits all attributes from the parent `sf.State` class.
                    
                    Methods:
                        Inherits all methods from the parent `sf.State` class, and does not override or define new ones.

                    """
                    pass

                class on(sf.State):
                    """
                    A simple state class that inherits from `sf.State`.
                    This class serves as a placeholder for a state that can be used in state machines
                    which are based on `sf.State`. It does not provide any additional functionality
                    to the base class and is meant to be subclassed to implement specific behavior
                    for a state that is 'on'.
                    

                    """
                    pass

                initial = sf.initial(off)
                transitions = sf.collection(
                    sf.transition(
                        source=off, target=on, guard=door_is_open
                    ),  # completion transition
                    sf.transition(DoorCloseEvent, source=on, target=off),
                )

            class oven_light(sf.Region):
                """
                A class representing the oven light region within the state machine, with two possible states: 'on' and 'off'.
                The class models the oven light's behavior through two states indicating whether the oven light is
                turned on or turned off. It starts in the 'off' state as indicated by the 'initial' configuration.
                The transitions between the states are triggered by events. The light turns 'on' when the
                OvenLightOnEvent occurs and returns to 'off' when the OvenLightOffEvent occurs.
                
                Attributes:
                    None explicitly declared in this class.
                
                Methods:
                    None explicitly declared in this class. The state behavior and transitions are managed by the
                    state machine framework.

                """
                class on(sf.State):
                    """
                    A class that represents an 'on' state within a state machine framework.
                    This class is a subclass of the 'sf.State' class and is designed to represent
                    a specific state, presumably the 'on' state. As such, it encapsulates
                    all functionality and characteristics pertinent to this state within the
                    state machine's context. The class by itself does not provide any additional
                    behavior or properties over its superclass but serves as a placeholder or
                    an identifier for the 'on' state within the system it is used.
                    
                    Attributes:
                        Inherited from sf.State:
                             Refer to the superclass 'sf.State' documentation for inherited attributes.
                    
                    Methods:
                        Inherited from sf.State:
                             Refer to the superclass 'sf.State' documentation for inherited methods.

                    """
                    pass

                class off(sf.State):
                    """
                    A class representing an 'off' state within a state machine framework.
                    This class is a simple subclass of the `sf.State` class and does not define any additional methods or properties. It serves as a specific state, presumably indicating that something is turned off or inactive within the state machine's context. By inheriting from `sf.State`, it leverages all the functionality of a state within a state machine, such as entering, exiting, transitions, and possibly holding behavior that should occur when the state machine is in the 'off' state.
                    
                    Attributes:
                        Inherits all attributes from the parent `sf.State` class.

                    """
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
                """
                A class representing the magnetron region within a larger state machine, presumably for modeling the behavior of a microwave's magnetron.
                The magnetron class is derived from a region of a state machine and contains two basic states: 'on' and 'off'. The 'initial' static method designates the 'off' state as the initial state of this region.
                
                Attributes:
                    off (State):
                         Represents the magnetron being turned off.
                    on (State):
                         Represents the magnetron being turned on.
                
                Methods:
                    initial():
                         Static method that sets the initial state of the magnetron region to the 'off' state.

                """
                off = sf.simple_state("off")
                on = sf.simple_state("on")

                initial = sf.initial(off)

            class turntable(sf.Region):
                """
                A class representing the turntable region within the Microwave's state machine.
                This region models the behavior of the microwave's turntable, which can either be in a rotating or an off state.
                
                Attributes:
                    None
                
                Methods:
                    None
                    States:
                    rotating:
                         State
                        Represents the state where the turntable is rotating. It has
                    two substates:
                    - clockwise:
                         State
                        Represents the turntable rotating in a clockwise direction.
                    - counterclockwise:
                         State
                        Represents the turntable rotating in a counterclockwise direction.
                        The initial state when the turntable is rotating is set to 'clockwise'.
                    off:
                         State
                        Represents the state where the turntable is not rotating (i.e., off).
                        This is also the initial state of the turntable region when the microwave is not in use.
                    Transitions:
                        - A transition from the 'off' state to the 'rotating' state occurs when a CookStartEvent is triggered.
                        - A transition from the 'rotating' state to the 'off' state occurs when a guard condition 'door_is_open' is met.

                """
                class rotating(sf.State):
                    """
                    A state object representing the rotating state of a component, such as a turntable in a microwave.
                    
                    Attributes:
                        clockwise (sf.State):
                             A nested state indicating that the component is rotating in the clockwise direction.
                        counterclockwise (sf.State):
                             A nested state indicating that the component is rotating in the counterclockwise direction.
                            This class also defines the initial starting state for the rotating state which is set to 'clockwise'.

                    """
                    class clockwise(sf.State):
                        """
                        A class that represents a 'clockwise' state in a state machine.
                        This class is derived from the 'sf.State' class and is intended to represent a
                        state within a state machine that signifies a 'clockwise' movement or transition.
                        The class does not provide any additional methods or attributes and serves as a
                        placeholder for a specific state category in the context of the state machine.
                        
                        Attributes:
                            Inherits all attributes from the 'sf.State' class.

                        """
                        pass

                    class counterclockwise(sf.State):
                        """
                        A class representing a state in which an object or a system operates in a counterclockwise direction.
                        This class is a subclass of 'sf.State' and represents a specific state within a state machine or a state-based system where the primary characteristic is counterclockwise motion or behavior. The class does not implement any additional methods or attributes and serves as a placeholder to signify counterclockwise operation. External systems or functions utilizing this class will define the specific behaviors associated with a 'counterclockwise' state.
                        
                        Attributes:
                            Inherits all attributes from the superclass 'sf.State'.
                        
                        Methods:
                            Inherits all methods from the superclass 'sf.State' and may override them if counterclockwise-specific behavior is required.

                        """
                        pass

                    initial = sf.initial(clockwise)

                class off(sf.State):
                    """
                    A placeholder state class that inherits from `sf.State` with no additional functionality.
                    This class represents a state that can be used in state machines derived from the `sf.State` base class. It serves as a simple, unmodified state that does not introduce any new behavior or properties to the states that a state machine can be in.
                    
                    Attributes:
                        Inherits all attributes from the parent class `sf.State`.
                    
                    Methods:
                        Inherits all methods from the parent class `sf.State`.

                    """
                    pass

                initial = sf.initial(off)
                transitions = sf.collection(
                    sf.transition(CookStartEvent, source=off, target=rotating),
                    sf.transition(source=rotating, target=off, guard=door_is_open),
                )

            class exhaust_fan(sf.Region):
                """
                A class that defines the behavior of the exhaust fan within a state machine context.
                The `exhaust_fan` class inherits from `sf.Region` and specifies the different states that an exhaust fan can be in, as well as the transitions between these states. It includes mechanisms to handle events that change the exhaust fan's speed.
                
                Attributes:
                    speed_choice (sf.Choice):
                         A state choice mechanism to determine the next state of the fan based on the event guard conditions.
                    off (sf.SimpleState):
                         A simple state representing the fan being off.
                    initial (sf.Initial):
                         Identifies the initial state of the fan as being on with low speed.
                    transition_to_off (sf.Transition):
                         Defines the transition from any `on` state to the `off` state on receiving an `ExhaustFanOffEvent`.
                    transition_to_fan_on (sf.Transition):
                         Defines transitions to the `speed_choice` based on an `ExhaustFanOnEvent`.
                        The `on` inner class represents the fan being on with nested states for low, medium, and high speeds. Each nested state is also a `sf.SimpleState`. The `speed_choice` mechanism selects the appropriate speed state based on guard conditions defined in the `speed_is_high` and `speed_is_medium` methods.
                
                Methods:
                    speed_is_high(self, event:
                         ExhaustFanOnEvent) -> bool:
                        A guard function that determines if the fan speed should be high.
                    speed_is_medium(self, event:
                         ExhaustFanOnEvent) -> bool:
                        A guard function that determines if the fan speed should be medium.

                """
                def speed_is_high(self, event: ExhaustFanOnEvent) -> bool:
                    """
                    Determines if the exhaust fan's speed is at a high level.
                    Checks the speed attribute of a given ExhaustFanOnEvent instance and evaluates if it is equal to 3, indicating a high speed.
                    
                    Args:
                        event (ExhaustFanOnEvent):
                             The event object that includes the current speed of the exhaust fan.
                    
                    Returns:
                        (bool):
                             True if the fan's speed is high (speed equals 3), False otherwise.

                    """
                    return event.speed == 3

                def speed_is_medium(self, event: ExhaustFanOnEvent) -> bool:
                    """
                    Determines if the exhaust fan is operating at medium speed.
                    Checks the speed attribute of the given ExhaustFanOnEvent object to determine
                    if the exhaust fan is running at medium speed, which is defined by the speed
                    attribute being equal to 2.
                    
                    Args:
                        event (ExhaustFanOnEvent):
                             An event object containing the exhaust fan's
                            current status and properties.
                    
                    Returns:
                        (bool):
                             True if the fan's speed is medium, i.e., when speed attribute equals
                            2; otherwise, False.
                        

                    """
                    return event.speed == 2

                class on(sf.State):
                    """
                    A class representing the 'on' state within a state machine context.
                    This class is a subclass of `sf.State` and defines three nested states to represent
                    the speed of an exhaust fan when the microwave is operating. The nested states are defined
                    as simple states using the StateFlow (`sf`) library.
                    
                    Attributes:
                        low (sf.State):
                             Represents the low-speed state of the exhaust fan.
                        medium (sf.State):
                             Represents the medium-speed state of the exhaust fan.
                        high (sf.State):
                             Represents the high-speed state of the exhaust fan.
                            The class does not provide methods but serves as a container for the nested
                            states that represent different operational speeds of an exhaust fan component within
                            the broader context of a microwave's functioning state machine.

                    """
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


class Microwave2(Microwave):
    """
    A subclass of the Microwave class, which inherits all the properties and methods from the Microwave parent class. This class currently does not introduce any additional attributes or methods and serves as a placeholder for potential future enhancements or specific implementations that differentiate it from its superclass.

    """
    pass


if __name__ == "__main__":

    async def main():
        """
        Async function that initializes and starts a Microwave state machine.
        This function dumps the structure of the Microwave state machine for debugging, creates an instance of Microwave, starts the state machine's interpreter, and prints its state. It then asserts that the power is turned on and prints the state again.
        
        Raises:
            AssertionError:
                 If the power state of the microwave is not 'on' after starting the interpreter.

        """
        sf.dump(Microwave)
        microwave = Microwave()

        await microwave.interpreter.start()
        print(microwave.state)
        assert microwave.power.on in microwave.state
        print(microwave.state)

    asyncio.run(main())
