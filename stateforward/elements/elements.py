from stateforward import model
from typing import (
    Callable,
    Union,
    ClassVar,
    Generic,
    TypeVar,
    ParamSpec,
    Any,
    cast,
    Optional,
)
from enum import Enum
from concurrent.futures import Future
from datetime import datetime, timedelta
import asyncio
import threading
import queue
from stateforward.protocols import Future
import multiprocessing

__all__ = [
    "StateMachine",
    "State",
    "Region",
    "Transition",
    "Vertex",
    "Pseudostate",
    "Initial",
    "Behavior",
    "PseudostateKind",
    "TransitionKind",
    "CallEvent",
    "AnyEvent",
    "FinalState",
    "CompositeState",
    "CompletionEvent",
    "Join",
    "Fork",
    "EntryPoint",
    "ExitPoint",
    "DeepHistory",
    "ShallowHistory",
    "Junction",
    "ChangeEvent",
    "TimeEvent",
    "Choice",
    "Constraint",
    "Event",
    "TransitionPath",
    "ConcurrencyKind",
    "EntryKind",
    "ChangeEvent",
]

T = TypeVar("T")
K = TypeVar("K")
P = ParamSpec("P")
R = TypeVar("R")


class ConcurrencyKind(str, Enum):
    """
    Enumeration for defining the concurrency kind of behaviors in a state machine.

    This enumeration specifies how behaviors and events are managed within a state machine
    in terms of their concurrency. It supports the following options:

    Attributes:
        threading (str): Indicates that behaviors are executed sequentially. When a behavior
            is triggered by an event, it will run to completion before the next behavior begins.
        threading (str): Specifies that each behavior runs in its own thread, allowing for
            true parallel execution of behaviors.
        multiprocessing (str): Behaviors are executed in a separate process, suitable
            for CPU-bound operations that require full utilization of CPU cores.
        asynchronous (str): Behaviors are managed asynchronously, and their execution can
            overlap in time, without necessarily running in parallel at the OS level.
            This option is ideal for I/O-bound operations.

    Example:
        class MyBehavior(Behavior, concurrency_kind=ConcurrencyKind.asynchronous):
            # Define asynchronous behavior implementation here
            pass
    """

    threading = "threading"
    multiprocessing = "multiprocessing"
    asynchronous = "asynchronous"


class Vertex(model.Element):
    """Represents a vertex in a state machine diagram.

    In the context of state machines, a vertex is an abstraction that encompasses
    various states and pseudo-states. It acts as a node in the state machine structure,
    where transitions can originate from or target this vertex.

    Attributes:
        outgoing (Collection['Transition']): A collection of transitions for which this
            vertex is the source. It represents all the transitions leading out from
            this vertex to other vertices.
        incoming (Collection['Transition']): A collection of transitions for which this
            vertex is the target. It contains all the transitions that lead into this
            vertex from other vertices.
        container ('Region'): The region (i.e., an encapsulating state or state machine)
            that this vertex belongs to. This reference provides the context within which
            the vertex exists.
    """

    outgoing: model.Collection["Transition"] = None  # initialize as None
    incoming: model.Collection["Transition"] = None  # initialize as None
    container: "Region" = None  # initialize as None


class FinalState(Vertex):
    """
    A FinalState represents a termination point of the enclosing StateMachine or
    composite State. It implies that the StateMachine or the composite State has
    completed its execution.

    When entering a FinalState, no Exit or Entry actions are executed, and it has no Effect Behavior.
    The StateMachine or composite State enclosing the FinalState is considered to have completed its
    execution. If the enclosing StateMachine or composite State is part of a containing StateMachine, it results
    in a completion event being propagated to the enclosing state.

    """


class TransitionKind(Enum):
    """
    Enum representing the various kinds of transitions that can occur in a state machine.

    Attributes:
        internal (str): Internal transition, triggered by an event, that doesn't cause a state change.
        local (str): Local transition, triggered by an event, that transitions to a substate without exiting the parent state.
        external (str): External transition, triggered by an event, that causes exiting and re-entering the state.
        self (str): Self-transition, re-entrant transition within the same state, useful for self-looping with a behavioral effect.
    """

    internal = "internal"
    local = "local"
    external = "external"
    self = "self"


class TransitionPath(model.Element):
    """
    Represents the path that a transition takes when being triggered.

    Attributes:
        enter (Collection[Vertex]): A collection of vertices to be entered during the transition.
        leave (Collection[Vertex]): A collection of vertices to be exited during the transition.
    """

    enter: model.Collection[Vertex] = None
    leave: model.Collection[Vertex] = None


class Transition(model.Element):
    """A Transition represents a change from one state or pseudostate to another.

    Attributes:
        source (Union[Vertex, "State", "Pseudostate"]): The origin Vertex from which the Transition originates.
        target (Union[Vertex, "State", "Pseudostate"]): The destination Vertex to which the Transition leads.
        container ("Region"): The Region that contains the Transition. The context in which it occurs.
        events (Collection["Event"]): A collection of Events that can trigger the Transition.
        effect ("Behavior"): The Behavior that is executed when the Transition is triggered.
        guard ("Constraint"): A Constraint that must evaluate to True for the Transition to occur.
        kind (TransitionKind): The kind of Transition (internal, local, external, or self).
        path (TransitionPath): The path of the Transition, defined by Vertex elements to enter and leave.
    """

    source: Union[Vertex, "State", "Pseudostate"] = None
    target: Union[Vertex, "State", "Pseudostate"] = None
    container: "Region" = None
    events: model.Collection["Event"] = None
    effect: "Behavior" = None
    guard: "Constraint" = None
    kind: TransitionKind = None
    path: TransitionPath = None


class PseudostateKind(Enum):
    """
    An enumeration for Pseudostate kinds in a state machine.

    The enumeration defines constants used to determine the type of a
    Pseudostate within a state machine.

    Attributes:
        initial (Enum): Represents the initial pseudostate that an enclosing state
            (or region) is in when the state machine is first started.
        choice (Enum): Represents a choice point, used to model a conditional branch.
            It allows a transition to complete successfully when more than one
            guard evaluates to True.
        join (Enum): Represents a join point where multiple concurrent transitions
            converge into a single outgoing transition.
        deep_history (Enum): Represents a history pseudostate that remembers the
            most deeply nested active state configuration.
        shallow_history (Enum): Represents a history pseudostate that remembers
            the immediate previous state configuration.
        fork (Enum): Represents a fork point where a single incoming transition
            splits into multiple concurrent outgoing transitions.
        entry_point (Enum): Represents an entry point into a submachine or composite
            state.
        exit_point (Enum): Represents an exit point out of a submachine or composite
            state.
        terminate (Enum): Represents a terminate pseudostate, which ends the
            execution of the entire state machine.

    Note:
        Pseudostates are typically used to model transitions to or from composite
        states or to model complex decision logic within a state machine.
    """

    initial = "initial"
    choice = "choice"
    join = "join"
    deep_history = "deep_history"
    shallow_history = "shallow_history"
    fork = "fork"
    entry_point = "entry_point"
    exit_point = "exit_point"
    junction = "junction"
    terminate = "terminate"


class Pseudostate(Vertex):
    """
    A pseudostate is an abstract vertex that encompasses different types of transient vertices in the state machine.

    The pseudostate serves as a kind of utility state during state transitions. There are several kinds of pseudostates,
    such as the initial pseudostate, which indicates the default entry point of a region or composite state, choice
    pseudostates, which are used to make decisions based on guard conditions, and more.

    Attributes:
        kind (PseudostateKind): The specific kind of the pseudostate, which dictates its behavior within the state machine.

    Inheritance:
        Inherits from Vertex.
    """

    kind: PseudostateKind = None


class Initial(Pseudostate, kind=PseudostateKind.initial):
    """
    An Initial pseudostate represents a starting point for a Region or StateMachine.

    It is a pseudostate that defines the default state when a Region is entered. An
    Initial pseudostate strictly has a single outgoing Transition and no incoming
    transitions.

    Attributes:
        kind (PseudostateKind): Denotes the kind of pseudostate. This is an enumeration
            with a fixed value of `PseudostateKind.initial` for this class, implying
            the pseudostate is of 'initial' type.
        transition (Transition): The transition that is triggered when the initial is entered
    Inheritance:
        Inherits from `Pseudostate` with a default `kind` set to `PseudostateKind.initial`.
    """

    transition: "Transition" = None


class EntryPoint(Pseudostate, kind=PseudostateKind.entry_point):
    """
    Represents an entry point in the state machine.

    Entry points are used in submachine state machines to specify a starting
    point when the submachine is entered from another state machine context.

    Attributes:
        kind (PseudostateKind): An enumeration that specifies the kind of
            pseudostate that this instance represents. For `EntryPoint`, the
            kind is `PseudostateKind.entry_point`.

    Inheritance:
        Inherits from `Pseudostate` with the kind set to `entry_point`.

    Usage:
        Entry points are instantiated during the state machine definition and
        are typically related to transitions leading to specific states within
        a submachine state. For example, an entry point can be defined to direct
        a transition to enter a submachine state machine at a particular named
        state rather than the initial state.

    Note:
        Entry points are conceptually similar to labeled entry points in
        complex activities, providing a way to start a submachine at locations
        other than the default initial state. This is useful for encapsulation
        and reusability of submachine state machines.
    """


class ExitPoint(Pseudostate, kind=PseudostateKind.exit_point):
    """
    Represents an Exit Point pseudostate in a State machine.

    Exit Point is a special kind of Pseudostate that marks a point where the state machine will
    transition to the parent State or Region. It is used in composite states or submachines to cross
    the boundary of a composite state.

    Attributes:
        kind (PseudostateKind): An enumeration literal denoting the kind of the Pseudostate,
                                which in this case is always 'exit_point'.

    Inheritance:
        Inherits from `Pseudostate` with the kind set to `exit_point`.

    Note:
        Exit Point pseudostates are not to be instantiated directly. They are meant to be used
        as part of the definition of a State machine within the context of State and Region elements.
    """


class DeepHistory(Pseudostate, kind=PseudostateKind.deep_history):
    """
    DeepHistory represents a type of Pseudostate that, when entered, will result in the activation of the
    most recent active configuration of the composite state that directly contains the deep history vertex.

    When the region is re-entered through the DeepHistory pseudostate, it restores the state configuration
    below the top level of the composite state. It does not restore the history of any regions within these
    sub-states (hence "deep").

    A DeepHistory pseudostate is commonly used in state machines that require a complex state hierarchy
    with the need to remember the precise state configuration. This can be useful in modal systems where
    returning to a prior state may require resuming nested states within that state.

    In case the region has never been entered before, the default entry state is used.

    Attributes:
        kind (PseudostateKind): This is not a typical class attribute, but rather an instance of an enumeration
                                that uniquely identifies the kind of Pseudostate as a 'deep history' state. This
                                enumeration member is passed to the parent class constructor (Pseudostate) during
                                class definition and is used to identify the specific type of pseudostate behavior
                                associated with the instance. The value is "PseudostateKind.deep_history" for the
                                DeepHistory class.
    """


class ShallowHistory(Pseudostate, kind=PseudostateKind.shallow_history):
    """
    ShallowHistory is a subtype of Pseudostate which represents a shallow history vertex within the state
    machine of a composite state. When a transition targets a shallow history pseudostate, the composite state
    is entered with its active substate configuration being the last active configuration recorded by the
    shallow history vertex. Unlike deep history, shallow history only recalls one level of substate nesting.

    When the region is entered through the shallow history pseudostate, it will enter the most recently visited
    direct substate, but not its children's history; i.e., it does not remember the history of nested substates.

    Attributes:
        kind (PseudostateKind): The kind attribute is inherited from the base Pseudostate class. For
                                ShallowHistory instances, this is always PseudostateKind.shallow_history.

    Inheritance:
        Inherits from `Pseudostate`, which in turn inherits from `Vertex`.
    """


class Junction(Pseudostate, kind=PseudostateKind.junction):
    """
    Represents a junction pseudostate in a state machine.

    A junction pseudostate is used to chain together multiple transitions. It allows
    complex transitions to be simplified into a series of simpler transitions without
    introducing additional states. A junction pseudostate is typically used to merge
    several incoming transitions into one outgoing transition that represents the shared
    parts of the transitions merged. It can also be used for making dynamic decisions
    about transition paths at runtime based on guard conditions.

    Attributes:
        kind (PseudostateKind): The kind of the pseudostate, which is the enumerated
            value `PseudostateKind.junction`. This attribute is inherited and its
            value is fixed for the Junction pseudostate.

    Inheritance:
        Inherits from `Pseudostate`, which in turn inherits from `Vertex`.

    Note:
        Unlike choice pseudostates, junctions do not allow for probabilistic choices.
        The guard conditions of the outgoing transitions of a junction pseudostate are
        evaluated to determine which path to take. There must be at least one
        outgoing transition with a guard condition evaluating to true. Otherwise, it
        will result in undefined behavior.
    """


class Join(Pseudostate, kind=PseudostateKind.join):
    """
    A Join pseudostate is used to merge several concurrent transitions emanating
    from source vertices in different orthogonal regions. The transitions entering
    a Join pseudostate cannot be triggered by events but are enabled when all
    the incoming transitions of the join are enabled. A Join pseudostate must
    have at least two incoming transitions and exactly one outgoing transition.

    Attributes:
        kind (PseudostateKind): An attribute derived from Pseudostate class,
                                indicating the specific kind of Pseudostate.
                                For Join, this is always set to PseudostateKind.join.

    """


class Choice(Pseudostate, kind=PseudostateKind.choice):
    """
    A pseudo state which models a dynamic conditional branch. It allows a transition
    to be made based on a condition or guard.

    Inherits from:
        Pseudostate (class): Base class for pseudostates in a state machine.

    Attributes:
        kind (PseudostateKind): The kind attribute set to PseudostateKind.choice,
                                representing the specific type of Pseudostate.

    Note:
        In an instance of this Choice pseudostate, the outgoing transitions should
        have guards which are mutually exclusive. When the Choice is reached, the
        guards are evaluated, and the first transition with a true guard is taken.
    """


class Fork(Pseudostate, kind=PseudostateKind.fork):
    """
    A Fork specifies a Pseudostate that serves as a splitting point in the
    StateMachine to create orthogonal regions where a single incoming Transition
    results in multiple outgoing Transitions to vertices in different orthogonal
    regions.

    Attributes:
        kind (PseudostateKind): The kind of the Pseudostate, initialized as
            PseudostateKind.fork.
    """


class Event(model.Element):
    """Represents an abstract event in a state machine.

    An `Event` is an occurrence of a significant situation that can trigger
    state transitions in the state machine or cause other actions to be taken.
    Events can be explicit, like a method call or a signal, or they can be
    implicit, such as the passing of time.

    Attributes:
        name (str): The name of the event.
        qualified_name (str): Fully qualified name that includes the hierarchy.
        type (Type['Event']): The Python type of this class.
        __redefined_element__ (Type['Event']): Element (if any) that this one redefines.
        __associations__ (dict[str, Association]): Associations linked to the event.
        owned_elements (list[ElementType]): Child elements owned by the event.
        model (Association['Model']): Association to the model that contains the event.
        attributes (dict[Any, Any]): Custom attributes associated with the event.
        owner (Optional[Association[ElementType]]): Association to the owner element.
    """


class AnyEvent(Event):
    """
    Class representing an event that can match any occurring event within a state machine.

    The `AnyEvent` is typically used within transitions to indicate that the transition
    can be triggered by any incoming event without specifying a particular type or condition.
    Inherits from the base `Event` class.

    """


class CallEvent(Event):
    """
    A specialized event representing a function call which corresponds to an operation.

    This event type can be used to encapsulate a call to a behavior as defined in a state machine.
    The execution of the corresponding operation may be associated with a transition,
    state entry, or state exit within the state machine.

    Attributes:
        results (Union[asyncio.Future, Future]): A future object that captures the result of the
            operation's execution. For synchronous call events, this will be an instance of concurrent.futures.Future,
            and for asynchronous call events, an instance of asyncio.Future.
        operation (Callable[P, R]): A callable representing the operation that is to be called when
            the event occurs. This operation can be any callable with a signature that accepts the specified
            parameter types 'P' and returns a value of type 'R'.
        __call__ (Callable[P, R]): A wrapper around the `operation` attribute that allows the
            CallEvent to be invoked as a callable, which in turn calls the operation with the provided arguments.

    Type Variables:
        P (ParamSpec): A ParamSpec type capturing the parameter types of the operation callable.
        R (TypeVar): A TypeVar representing the return type of the operation callable.
    """

    results: Union[asyncio.Future, Future] = None
    operation: Callable[P, R] = None
    __call__: Callable[P, R] = None


class TimeEvent(Event):
    """
    A type of event triggered by the passage of time.

    TimeEvent specifies the point in time or the duration of time,
    after which the event should occur. TimeEvent is used in various
    types of state machines for timed transitions.

    Attributes:
    - when (Union[datetime, timedelta]): The 'when' attribute can be an
      absolute point in time (datetime) or a duration that specifies a
      relative amount of time (timedelta) after which the event
      occurs.
    """

    when: Union[datetime, timedelta] = None


ConditionType = Union[threading.Condition, multiprocessing.Condition, asyncio.Condition]


class ChangeEvent(Event):
    """Represents events that are fired when a specified condition becomes true.

    The `ChangeEvent` is tied to a condition expression which, when evaluated to true,
    triggers the event processing. This can be useful for monitoring changes in the
    state of objects or systems and reacting to these changes.

    Attributes:
        condition (ConditionType): A lock object used to synchronize the evaluation
            of the condition expression. Different implementations of ConditionType
            may be used depending on whether the application is single-threaded,
            multi-threaded, or asynchronous.
        expr (Callable[[ChangeEvent, Event], bool]): A callable that takes the
            `ChangeEvent` itself and another `Event` as arguments, returning a boolean
            value. It represents the condition expression that, when evaluated to true,
            triggers the event.

    """

    condition: ConditionType = None
    expr: Callable[["Event"], bool] = None


class CompletionEvent(Event):
    """
    Represents a completion event in a state machine, indicating that a particular state has finished its activities.

    A CompletionEvent is implicitly triggered when a State has no other outgoing behavioral Transitions to process
    or when its internal activity has been completed. This event can be used to facilitate automatic transitions from
    one state to another without explicit external triggers.

    Attributes:
        transition (Transition): The transition associated with the completion event. This transition
                                 is activated when the completion event occurs.
    """

    transition: Transition = None


class Constraint(model.Element):
    """
    Represents a conditional expression that must evaluate to true for a transition to be triggered.

    The `Constraint` class encapsulates the logic that determines whether a particular transition
    within a state machine is allowed to be taken. The `condition` attribute is a callable that
    takes an instance of `Constraint` and an `Event` object and returns a boolean value.

    Attributes:
        condition (Callable[["Constraint", "Event"], bool]):
            A callable that represents the guard condition for the transition.
            It takes the `Constraint` instance and an `Event` as arguments and
            should return True if the transition condition is met, or False otherwise.
    """

    condition: Callable[["Event"], Union[Future, bool]] = None


class CompositeState(model.Element):
    """
    A class representing a CompositeState in a UML model. A CompositeState is a Vertex that
    contains other Vertexes, known as subvertexes, potentially organized into Regions.

    A CompositeState can represent more complex behavior in state machines, where states can be
    nested within other states. This concept supports the hierarchical nesting of states and
    the definition of orthogonal regions of parallel states.

    Attributes:
        region (Collection["Region"]): A collection of Region elements that defines the orthogonal
            regions within the composite state. The regions contain substates (subvertexes) and
            handle state transitions independently.

    Inherits from:
        Element (type[T]): Inherits methods and attributes from the Element class.
    """

    regions: model.Collection["Region"] = None


class State(Vertex, CompositeState):
    """
    State is a Vertex that is also a CompositeState.

    It can define behaviors for entry and exit, as well as an ongoing do_activity behavior. The State can also
    have a completion event, which indicates that the internal behavior and activities are complete, and potentially
    deferred events. States can also act as submachine states containing an entire StateMachine.

    Attributes:
        entry (Behavior): The behavior that is executed when entering the state.
        exit (Behavior): The behavior that is executed when exiting the state.
        do_activity (Behavior): The behavior that is executed while the state machine is in this state.
        completion (CompletionEvent): An event that is triggered when the state has completed its activity.
        deferred (Collection[Event]): Events that are not handled in the state but are deferred to the state machine
                                      for handling at a later time.
        submachine (StateMachine): If the state acts as a submachine, this will contain the state machine that
                                   specifies the internal behavior of the composite state.
    """

    entry: "Behavior" = None
    exit: "Behavior" = None
    do_activity: "Behavior" = None
    completion: CompletionEvent = None
    deferred: model.Collection[Event] = None
    submachine: "StateMachine" = None


class Region(model.Element):
    """Represents a region in a state machine.

    A region is a container for vertices (states and pseudostates) and defines a
    namespace for those elements. Each region can contain multiple subvertices and
    has at most one initial state. Regions can be part of composite states or state
    machines.

    Attributes:
        subvertex (Collection[Vertex]): The collection of vertices that this region
            contains.
        initial (Initial): The initial state of this region.
        state (Optional[State]): The state that contains this region, if any.
        state_machine (Optional[StateMachine]): The state machine that contains this
            region, if any.
    """

    state: Optional["State"] = None
    state_machine: Optional["StateMachine"] = None
    subvertex: model.Collection[Vertex] = None
    initial: Initial = None


QueueType = Union[queue.Queue, multiprocessing.Queue, asyncio.Queue]
ActiveType = Union[threading.Event, multiprocessing.Event, asyncio.Event]


class Behavior(model.Model):  # , Generic[T]):
    """
    Represents the behavior associated with states in a state machine.

    A behavior is an action or series of actions that may occur when a specific event is
    processed by the state machine. This class is designed to be subclassed to provide
    custom behavior logic as needed for different states.

    ClassVar Attributes:
        concurrency_kind (ClassVar[ConcurrencyKind]): Specifies the kind of concurrency used
                                                       by the behavior. Options include
                                                       threading, thread, multiprocessing,
                                                       and asynchronous.

    Attributes:
        activity (Callable[['Behavior', 'Event'], Union[Any, asyncio.Task]]):
            A callable representing the activity to be performed. When behavior is executed,
            this function is called with the behavior instance and the event as arguments.
        context (Union[T, 'Behavior']):
            The context in which the behavior is executed. This is typically the state or the
            state machine that the behavior belongs to.
        pool (Collection[Event]):
            A collection of events that are considered part of the behavior's event pool,
            which it may respond to.

    Note:
        The `activity` attribute can be either a synchronous or an asynchronous callable,
        depending on the concurrency kind specified.


    !!! info
        The actual concurrency behavior is determined by the model Interpreter, and the `concurrency_kind`
        simply provides an indication of how the behavior is meant to be executed in terms of concurrency.

    !!! example "Example"
        === "light_switch.py"
            ```python
            # ... existing code from the LightSwitch example

            # Defining a new Behavior by inheriting the Behavior element
            class PrintBehavior(sf.Behavior):
                # An activity function that prints the state and event information
                def activity(self, event: sf.Event = None):
                    print(
                        f"{self.qualified_name} -> {event.qualified_name if event else 'None'}"
                    )

            # Updating the LightSwitch state machine to use the PrintBehavior
            class LightSwitch(sf.AsyncStateMachine):
                class On(sf.State):
                    entry = sf.bind(PrintBehavior)  # Binding the PrintBehavior to the entry event
                    exit = sf.bind(PrintBehavior)   # Binding the PrintBehavior to the exit event

                class Off(sf.State):
                    entry = sf.bind(PrintBehavior)  # Similarly for the Off state
                    exit = sf.bind(PrintBehavior)

            # ... continuation of the LightSwitch example
            ```
        === "Output"
            The example output below illustrates the invocation of the `PrintBehavior` for each state's entry and exit procedures, with accompanying event details.

            ```bash
            LightSwitch.region.region_0.Off.entry<4313140624> -> None
            LightSwitch.region.region_0.Off.exit<4313140752> -> LightSwitch.region.region_0.transition_from_Off_to_On.events.OnEvent
            LightSwitch.region.region_0.On.entry<4313137296> -> LightSwitch.region.region_0.transition_from_Off_to_On.events.OnEvent
            LightSwitch.region.region_0.On.exit<4313139536> -> LightSwitch.region.region_0.transition_from_On_to_Off.events.OffEvent
            LightSwitch.region.region_0.Off.entry<4313140624> -> LightSwitch.region.region_0.transition_from_On_to_Off.events.OffEvent
            LightSwitch.region.region_0.Off.exit<4313140752> -> None
            ```

            This output demonstrates that the behavior is correctly associated with each state, with the `bind` function ensuring that each behavior is instantiated as a unique object. In contrast, without the `bind` method, multiple states could end up sharing a reference to the same `Behavior` instance, as behavior definitions are types. Using `bind`, we can also pass arguments to adjust the behavior's attributes, allowing for tailored functionality within each state.

    """

    concurrency_kind: ClassVar[ConcurrencyKind] = None
    activity: Callable[["Event"], Future] = None
    context: Union[T, "Behavior"] = None
    pool: model.Collection[Event] = None


class StateMachine(Behavior, CompositeState):
    """
    The `StateMachine` in StateForward is partially inspired by UML2.5 and is therefore designed with flexibility to deviate from the strict UML specifications when it provides practical benefits for development.

    Attributes:
        submachine_state (State): The current State of the submachine. This refers to the currently active State
            within the StateMachine.
        state: Retrieves a tuple of active `State` instances that are currently active in the state machine.


    A `StateMachine` is organized into one or more `Region` elements — see [CompositeState](#compositestate) for more details.

    The StateForward preprocessor automatically creates `Region` elements when substates are added to a `State` or `StateMachine`. This concurrent workflow within different regions of the state machine allows for sophisticated behavior patterns that can simulate complex systems' parallel operations.
    """

    submachine_state: State = None

    @property
    def state(self) -> tuple[State]:
        return tuple(
            cast(State, value)
            for value in self.interpreter.stack.keys()
            if model.element.is_subtype(value, State)
        )


class EntryKind(Enum):
    """
    EntryKind is an enumeration class that defines constants for representing the
    manner in which a state or pseudostate is entered within a state machine.

    Attributes:
        default (str): Indicates a default entry, where the state machine will enter
            the target vertex without any specific trigger or condition apart from the
            completion of previous transitions.
        explicit (str): Indicates an explicit entry, where the transition to the target
            vertex is triggered by a specific event or condition.
    """

    default = "default"
    explicit = "explicit"
