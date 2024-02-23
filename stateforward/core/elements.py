"""

The `elements` module provides a comprehensive set of classes that represent various components of a state machine. The classes in this module can be utilized to model the states, transitions, events, and behaviors within a state machine architecture. Below is an overview of the main classes and enumerations within the module, each designed to encapsulate specific aspects of state machine behavior and functionality.

### Classes

- `Vertex`: The base class for nodes within the state machine graph, which can have incoming and outgoing transitions.

- `Transition`: Represents a state change in the state machine, connecting two vertices and potentially associated with triggering events, guards, and effects.

- `TransitionPath`: Describes the sequence of vertices a transition passes through, including the vertices to enter and leave during the transition.

### Enumerations

- `ConcurrencyKind`: Defines the types of concurrency mechanisms used, like `threading`, `multiprocessing`, or `asynchronous` execution.

- `TransitionKind`: Categorizes transitions as `internal`, `local`, `external`, or `self` transitions.

- `PseudostateKind`: Specifies various types of control nodes within the state machine, such as `initial`, `choice`, `join`, `fork`, and others.

### Subclasses

- `FinalState`: Represents an end state for a region within a state machine.

- `Pseudostate`: A subclass of `Vertex`, representing different kinds of control points within the state machine, such as initial states or junction points.

- `State`: A vertex that may contain nested regions, representing a state which can also have entry and exit behaviors.

- `Region`: Organizes the structure of states and transitions, representing a distinct context for stateful behaviors.

- `Event`: The base class for events which can trigger transitions.

- `Constraint`: Represents a condition that guards transitions or influences state behavior.

- `StateMachine`: Encapsulates the entire state machine structure and behavior, acting as a container for states, regions, and transitions.

### Other Components

- `Behavior`: Encapsulates the action or activity associated with a state or event within the state machine.

- `CompletionEvent`: Represents an event that is fired upon the completion of a state's internal activity.

- `ChangeEvent`: Triggers a transition based on a conditional expression being satisfied.

- `TimeEvent`: Is fired when a specific time-related condition is met, like a timeout or an elapsed time period.

This module is intended to be used in conjunction with other modules and utilities that form a framework for state management and behavior modeling. The components defined here can be extended or used as is to create complex and robust state machines for various application domains.
"""
from stateforward import model
from typing import (
    Callable,
    Union,
    ClassVar,
    TypeVar,
    ParamSpec,
    Any,
    cast,
    Optional,
)
from enum import Enum
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
    An enumeration representing different concurrency models.
    This class is a specialized enumeration (derived from `str` and `Enum`) that
    outlines the various concurrency kinds or parallel execution models that can be
    used within a system or application. The ConcurrencyKind class provides
    a clear and standardized way to refer to these models with predefined
    constants.

    Attributes:
        threading (str):
             Represents a concurrency model that uses threads for
            concurrent execution. Threads run in the same memory space but execute
            independently.
        multiprocessing (str):
             Denotes a concurrency model that leverages multiple
            processes for parallel execution. Processes run in separate memory spaces
            and communicate via IPC (Inter-Process Communication).
        asynchronous (str):
             Indicates an event-driven concurrency model where
            the workflow is orchestrated around the availability of tasks to
            perform operations without necessarily blocking other tasks.

    """

    threading = "threaded"
    multiprocessing = "multiprocessing"
    asynchronous = "asynchronous"


class Vertex(model.Element):
    """
    A Vertex represents a node in a state machine diagram within a modeling framework.
    This class is a subclass of `model.Element` and represents the concept of a vertex in the context of state machines. A `Vertex` has potential incoming and outgoing transitions, which are references to other `Vertex` instances via `Transition` instances. It also maintains a reference to its containing `Region`, which represents the larger hierarchical structure of a state machine.

    Attributes:
        outgoing (model.Collection['Transition']):
             A collection of outgoing transitions from this vertex. The initial value is None, indicating that it may be set later.
        incoming (model.Collection['Transition']):
             A collection of incoming transitions to this vertex. Similar to outgoing, it is initialized as None.
        container ('Region'):
             The region that contains this vertex. This attribute is also initialized to None, reflecting that the assignment to a specific region will occur post-initialization.

    """

    outgoing: model.Collection["Transition"] = None  # initialize as None
    incoming: model.Collection["Transition"] = None  # initialize as None
    container: "Region" = None  # initialize as None


class FinalState(Vertex):
    """
    A class that represents the final state in a state machine or a similar diagrammatic structure.
    This class inherits from the Vertex class and signifies the completion of a process or the
    end state in a finite state machine or workflow.

    Attributes:

    Methods:
        Note:
            Additional details on how FinalState interacts with other components of the system
            or any special considerations could be included in this section.

    """


class TransitionKind(Enum):
    """
    An enumeration to represent the types of transitions in a state machine.

    Attributes:
        internal (Enum):
             A transition that occurs within the context of a single state, without causing a state exit or entry.
        local (Enum):
             A transition that is local to a composite state and does not exit the composite state itself.
        external (Enum):
             A transition that causes the state machine to exit the current state and enter a new state.
        self (Enum):
             A special transition that represents a self-transition, where the state exits and re-enters itself.

    """

    internal = "internal"
    local = "local"
    external = "external"
    self = "self"


class TransitionPath(model.Element):
    """
    A class that represents a transition path within a model, which consists of entering and leaving vertices.

    Attributes:
        enter (model.Collection[Vertex]):
             A collection of Vertex instances that represent the points where a
            transition can be entered. If not specified, it defaults to None, indicating that there are no
            specific enter points designated.
        leave (model.Collection[Vertex]):
             A collection of Vertex instances that represent the points where a
            transition can be exited. Similar to `enter`, it defaults to None, indicating that there are no
            specific leave points designated.
            The TransitionPath is a part of the model that tracks the entry and exit points in a transition, which can
            be particularly useful in state machines or workflow representations where the concept of transitions
            between states or tasks is essential.

    """

    enter: model.Collection[Vertex] = None
    leave: model.Collection[Vertex] = None


class Transition(model.Element):
    """
    A UML Transition element that represents a state change in the finite state machine.
    This class is inherited from the model.Element and acts as a container for the
    characteristics of a transition between states (or pseudostates) within a region.

    Attributes:
        source (Union[Vertex, 'State', 'Pseudostate']):
             The starting point of the transition,
            which can be either a Vertex, State, or Pseudostate.
        target (Union[Vertex, 'State', 'Pseudostate']):
             The endpoint of the transition,
            which can be either a Vertex, State, or Pseudostate.
        container ('Region'):
             The region that contains this transition. This region is part of
            the finite state machine structure that the transition belongs to.
        events (model.Collection['Event']):
             A collection of events that trigger this
            transition. The transition occurs when one of the events in this collection fires.
        effect ('Behavior'):
             The effect is a behavior to be performed when the transition
            occurs. This behavior is executed after the transition takes place.
        guard ('Constraint'):
             A condition that must evaluate to true for the transition to be
            taken. If the guard condition is false, the transition will not occur.
        kind (TransitionKind):
             The kind specifies the nature of the transition. Different
            transition kinds define different types of behavior such as internal, external, etc.
        path (TransitionPath):
             The path attribute provides information about the transition
            path, including its source and target and any intermediate steps.

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
    A class that enumerates the various kinds of pseudostates that can be used within a state machine.
    Pseudostates are special kinds of states that denote a transition phase rather than an actual state that an
    entity can reside in. The PseudostateKind class contains enumeration members that represent the different types
    of pseudostates including `initial`, `choice`, `join`, `deep_history`, `shallow_history`, `fork`, `entry_point`,
    `exit_point`, `junction`, and `terminate`. Each of these members correlates to a specific kind of pseudostate
    behavior.

    Attributes:
        initial (str):
             Represents the starting pseudostate of a state machine, indicating the default state on creation.
        choice (str):
             Indicates a decision point where multiple outgoing transitions are possible based on guard
            conditions.
        join (str):
             Represents the merging of parallel transition paths back into a single transition path.
        deep_history (str):
             Indicates that the state machine should enter the most recent active configuration of a
            composite state.
        shallow_history (str):
             Represents a history pseudostate that only remembers the immediate prior state rather than
            the complete history.
        fork (str):
             Symbolizes a splitting of one transition path into multiple parallel paths of execution.
        entry_point (str):
             Denotes a predefined point where a transition may cross the boundaries of a composite state.
        exit_point (str):
             Indicates a specific point out of a state or a region where transitions can be made from the inside.
        junction (str):
             Represents a complex branching point where multiple joins and forks can be chained together.
        terminate (str):
             Symbolizes the end of a state machine instance's life, after which no further processing occurs.
            This enumeration is typically used as part of a framework or library that implements state machine behavior,
            and serves to ensure that the pseudostate behavior is consistent and standardized across different applications.

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
    Represents a vertex in the state machine which is a Pseudostate.
    A Pseudostate is typically used to represent complex transition scenarios in state machines. This class extends from the Vertex class and includes an attribute to represent the specific kind of pseudostate it is.

    Attributes:
        kind (PseudostateKind):
             An enum value that signifies the specific kind of pseudostate, such as initial, choice, junction, etc. The default value is None, which should be set to a specific kind by the user.

    """

    kind: PseudostateKind = None


class Initial(Pseudostate, kind=PseudostateKind.initial):
    """
    Represents an initial pseudostate in a state machine.
    An initial pseudostate is a starting point for any state machine. When the state machine is initialized,
    it begins execution with the state that has an outgoing transition from this initial pseudostate.

    Attributes:
        transition (Transition):
             A transition object representing the outright transition from the initial
            pseudostate to another state in the state machine. This transition is triggered
            when the state machine starts. Initially, the transition is set to None and should
            be defined when the initial state is connected to another state.
        Inheritance:
            Inherits from `Pseudostate` with an implicit kind of `PseudostateKind.initial` to indicate
            that it is an initial pseudostate.
        Note:
            The class is expected to be used as part of a larger state machine framework, where transitions
            and states are interlinked to define the behavior of a complex system.

    """

    transition: "Transition" = None


class EntryPoint(Pseudostate, kind=PseudostateKind.entry_point):
    """
    Represents an entry point definition in a state machine.
    `EntryPoint` is a specialized `Pseudostate` that denotes the starting point of a
    region in a state machine. It is a pseudo state of kind entry point, meaning
    it is used to trigger the state machine to begin its execution from this point.


    Attributes:
        kind (PseudostateKind):
            An attribute inherited from `Pseudostate` that is
            statically set to `PseudostateKind.entry_point` to indicate that this
            pseudo state is an entry point.
    """


class ExitPoint(Pseudostate, kind=PseudostateKind.exit_point):
    """
    A specialization of Pseudostate that represents an exit point in a StateMachine or composite State in a UML model.
    ExitPoint is used to denote a point within a composite State or StateMachine from which.
    transition to a point outside the composite State or StateMachine occurs. An ExitPoint,
    as a kind of Pseudostate, is used to encapsulate the exit behavior for the State that owns it,
    providing a modular way of defining how different transitions lead out of a State.
    Inherits from:
    Pseudostate -- A generalization for various control points within a StateMachine.

    Attributes:
        kind (PseudostateKind):
             An enumerated value indicating the specific kind of
            Pseudostate that an instance represents, which in this case is
            set to PseudostateKind.exit_point by default.

    """


class DeepHistory(Pseudostate, kind=PseudostateKind.deep_history):
    """
    A DeepHistory class represents a deep history pseudostate within a state machine. It inherits from the
    Pseudostate class, with the kind attribute defaulted to PseudostateKind.deep_history.
    A deep history pseudostate is used to remember the most recent active configuration of states within
    a composite state. When a transition targets a deep history pseudostate, the state machine will
    re-enter the composite state with the same configuration that was last in place prior to its exit.

    Attributes:
        kind (PseudostateKind):
             A default attribute provided by the Pseudostate base class, overridden
            to use PseudostateKind.deep_history for deep history pseudostates.
        Inherits:
        Pseudostate:
             A base class for different types of pseudostates within a state machine.

    """


class ShallowHistory(Pseudostate, kind=PseudostateKind.shallow_history):
    """
    A class representing a shallow history pseudostate in a state machine.
    ShallowHistory is a specialized pseudostate that remembers the last active substate of its region, but not the history of nested substates.
    When a transition targets a shallow history pseudostate, the state machine will resume the state configuration just one level deep of the region.
    Inherits from:
    Pseudostate: A base class for pseudostates.

    Attributes:
        kind (PseudostateKind):
             Indicates the kind of pseudostate, which is set to `PseudostateKind.shallow_history` by default for this class.

    """


class Junction(Pseudostate, kind=PseudostateKind.junction):
    """
    A class representing a Junction, which is a specialized Pseudostate that is used to merge several transitions into one.
    Junction is a subclass of Pseudostate and is instantiated with a specific kind that identifies it as a junction kind of pseudostate. Junction pseudostates are used to model complex transitional logic in state machine diagrams, allowing for the convergence of multiple incoming transitions into a single outgoing transition.

    Attributes:
        kind (PseudostateKind):
             An enumeration value of PseudostateKind, specifically set to 'junction' to denote
            the type of Pseudostate this class represents.
        Inherits:
        Pseudostate:
             The base class for pseudostates, providing core functionality and properties.

    """


class Join(Pseudostate, kind=PseudostateKind.join):
    """
    A specialized Pseudostate that represents a join node in a state machine.
    This class is a specific type of Pseudostate that is used to synchronize multiple
    concurrent flows. It inherits from the Pseudostate class and is initialized with
    a kind attribute set to PseudostateKind.join by default. When multiple transitions
    converge to a join node, they are synchronized, and the state machine continues
    with a single, unified transition emanating from the join node.

    Attributes:
        kind (PseudostateKind):
             A default attribute representing the kind of pseudostate,
            which is set to PseudostateKind.join to indicate a join node behavior.
        Inherits:
        Pseudostate:
             The base class for all pseudostates in a state machine.
        Note:
            This class should be used in the context of a state machine where concurrent
            states need to be synchronized before proceeding further in the workflow.

    """


class Choice(Pseudostate, kind=PseudostateKind.choice):
    """
    A Pseudostate subclass that represents a choice pseudostate in a state machine.
    A choice pseudostate is a decision point where the transition path is chosen based on guards of the
    transitions. This Pseudostate subclass receives an additional argument `kind` which should be
    specifically set to `PseudostateKind.choice` to indicate that this pseudostate is a choice node.

    Attributes:
        kind (PseudostateKind):
             An enumeration value that determines the kind of pseudostate,
            with the expected value being `PseudostateKind.choice` for this subclass.
        Inherits:
        Pseudostate:
             The base class for all pseudostates, providing common functionality.

    """


class Fork(Pseudostate, kind=PseudostateKind.fork):
    """
    A class that represents a Fork Pseudostate in UML state machines.
    The Fork class is a specialized form of the Pseudostate and is used to model a point in a state machine where a single transition splits into multiple parallel transitions or where multiple parallel states can converge into a single state. It leverages the PseudostateKind enumeration to indicate that the pseudostate is of type 'fork'.
    Inheritance:
    Inherits from Pseudostate.

    Attributes:
        kind (PseudostateKind):
             An attribute provided by the Pseudostate class, which is set to PseudostateKind.fork, representing the kind of pseudostate this class models.

    """


class Event(model.Element):
    """
    An object that represents an event in a model. Inherits from the `model.Element` class.

    Attributes:

    """


class AnyEvent(Event):
    """
    An extension of the `Event` class that represents a generic event without specific properties or restrictions.
    This class serves as a base class for more specialized event types or can be used directly to create events that do not require additional information beyond what is offered by the `Event` base class. Subclasses of `AnyEvent` can add more context-specific attributes and methods as needed.

    Attributes:

    Methods:

    """


class CallEvent(Event):
    """
    A class that represents an event associated with a call operation, inheriting from the Event class.

    Attributes:
        results (Union[asyncio.Future, Future]):
             A placeholder for the future result of the call operation. This can either be an asyncio.Future or concurrent.futures.Future object.
        operation (Callable[P, R]):
             The callable object representing the operation that will be performed when the event is triggered. The callable should take parameters 'P' and return a result 'R'.
        __call__ (Callable[P, R]):
             An alias or a proxy to the 'operation' callable, allowing the instance to be directly invoked like a function with the same signature.

    """

    results: Union[asyncio.Future, Future] = None
    operation: Callable[P, R] = None
    __call__: Callable[P, R] = None


class TimeEvent(Event):
    """
    A class representing an event that is associated with a specific point in time or a duration of time.

    Attributes:
        when (Union[datetime, timedelta], optional):
             A datetime object indicating the specific time when the event occurs or a timedelta object indicating the duration or offset of the event from a certain point in time. The default is None, which means that the time or duration of the event is not set.
        Inherits from:
        Event:
             The base class for all event types.

    """

    when: Union[datetime, timedelta] = None


ConditionType = Union[threading.Condition, multiprocessing.Condition, asyncio.Condition]


class ChangeEvent(Event):
    """
    A class that represents an event signaling a change based on a specified condition.

    Attributes:
        condition (ConditionType):
             An optional attribute representing the condition under which the change event is triggered.
        expr (Callable[['Event'], bool]):
             An optional callable that takes an 'Event' object as input and returns a boolean value indicating whether the change event condition is met.

    """

    condition: ConditionType = None
    expr: Callable[["Event"], bool] = None


class CompletionEvent(Event):
    """
    A class representing a completion event in a system or application.
    This class inherits from a base 'Event' class and is specialized to represent an event that
    signifies the completion of an activity or process. It optionally carries additional data
    with the 'value' field to provide context or resulting value at the time of completion.

    Attributes:
        value (Any):
             The data or value associated with the completion event. This can be of any
            type and is meant to represent the result or final state upon completion. Default is 'None'.
        transition (Transition):
             Represents the state transition associated with the event completion.
            This is a placeholder for a 'Transition' type object which likely defines
            the movement from one state to another as the event completes. Default is 'None'.

    Args:
        value (Any, optional):
             Optional initialization argument for 'value'. The data or
            result to be associated with this completion event. If not provided,
            defaults to 'None'.

    """

    value: Any = None
    transition: Transition = None

    def __init__(self, value: Any = None):
        """
        Initializes a new instance of the class with an optional value.

        Args:
            value (Any, optional):
                 The initial value to be stored in the instance. Default is None.

        """
        self.value = value


class Constraint(model.Element):
    """
    A class that represents a constraint condition to be applied on an 'Event' within a modeling framework.
    This class inherits from 'model.Element' and encapsulates a condition that must be satisfied by an event. The condition is represented as a callable that takes an 'Event' as input and returns either a 'Future' object that resolves to a boolean or a boolean value directly. This allows for asynchronous or synchronous evaluation of the condition depending on the implementation.

    Attributes:
        condition (Callable[['Event'], Union[Future, bool]]):
             A callable object that defines the constraint condition to be checked against 'Event' objects. If the callable returns a 'Future', the result of the future must be a boolean value that represents whether the 'Event' satisfies the constraint condition. If the callable returns a boolean directly, it represents the immediate result of the constraint evaluation.

    """

    condition: Callable[["Event"], Union[Future, bool]] = None


class CompositeState(model.Element):
    """
    Represents a composite state in a state machine model.
    A composite state is a state that contains one or more regions, which in turn can contain other
    states, including composite states. This allows for the representation of a hierarchy of states
    and the possibility of concurrent states within a single composite state.

    Attributes:
        regions (model.Collection['Region']):
             A collection of regions that the composite state contains.
            Each region is an instance of 'Region', allowing the composite state to encapsulate
            various states and transitions.
        Inheritance:
            Inherits from model.Element, which provides base functionality
            for elements in the state machine model.
        Note:
             The regions attribute is initialized as None and should be set with instances of
            'Region' to define the structure of the composite state.

    """

    regions: model.Collection["Region"] = None


class State(Vertex, CompositeState):
    """
    A class that represents a State in a state machine, which is a specialized vertex that can also act as a composite state. It can have behaviors associated with it such as entry, exit, and activity, as well as a completion event. States can also defer events and reference a submachine for nested state configurations.

    Attributes:
        entry (Behavior):
             An optional behavior that is executed when entering the state. Defaults to None.
        exit (Behavior):
             An optional behavior that is executed when exiting the state. Defaults to None.
        activity (Behavior):
             An optional ongoing behavior that occurs while in the state. Defaults to None.
        completion (CompletionEvent):
             An optional completion event that can trigger a state transition. Defaults to None.
        deferred (model.Collection[Event]):
             An optional collection of events that are deferred until the state is exited. Defaults to None.
        submachine (StateMachine):
             An optional reference to a submachine if the state is a composite state that contains another state machine. Defaults to None.
        Inherits from:
        Vertex:
             A base class representing the vertices in a state machine graph.
        CompositeState:
             A base class for states that contain other states, indicating that this state can act as a composite state.

    """

    entry: "Behavior" = None
    exit: "Behavior" = None
    activity: "Behavior" = None
    completion: CompletionEvent = None
    deferred: model.Collection[Event] = None
    submachine: "StateMachine" = None


class Region(model.Element):
    """
    A class representing a Region in a state-based model. A Region can be considered as a part of a 'State', or it can be the top-level state containment for state machine. It may contain a collection of 'Vertex' instances representing states and transitions, and points to an 'Initial' pseudo-state that determines the default active state when entering this region.
    This class extends from 'model.Element', and includes optional references to a 'State' and a 'StateMachine' to which the region belongs. Additionally, it holds an optional collection of 'Vertex' instances that are contained within the region and an 'Initial' pseudo-state representing the default entry point.

    Attributes:
        state (Optional['State']):
             A reference to the 'State' instance that contains this region, if any.
        state_machine (Optional['StateMachine']):
             A reference to the 'StateMachine' instance that contains this region if it is a top-level region.
        subvertex (model.Collection[Vertex]):
             A collection of 'Vertex' instances that the region contains.
        initial (Initial):
             An 'Initial' pseudo-state specifying the initial active state within the region.

    """

    state: Optional["State"] = None
    state_machine: Optional["StateMachine"] = None
    subvertex: model.Collection[Vertex] = None
    initial: Initial = None


QueueType = Union[queue.Queue, multiprocessing.Queue, asyncio.Queue]
ActiveType = Union[threading.Event, multiprocessing.Event, asyncio.Event]


class Behavior(model.Model):  # , Generic[T]):
    """
    A class representing a Behavior which is part of a model with defined concurrency and associated actions.
    This class encapsulates the behavior in a system modeled by multiple classes. It defines the type
    of concurrency (synchronous, asynchronous, etc.), the activity to be carried out when
    triggered by an event, the context within which the behavior operates, and a pool of events
    it can handle.

    Attributes:
        concurrency_kind (ClassVar[ConcurrencyKind]):
             A variable indicating the type of concurrency employed by the
            behavior. This is a class-level variable shared among all instances.
        activity (Callable[['Event'], Future]):
             A callable that is invoked when the behavior is triggered by an event.
            It represents the action or activity undertaken by the behavior and returns a Future object, typically
            indicating an asynchronous operation.
        context (Union[T, 'Behavior']):
             A reference that provides the context in which the behavior operates.
            This can be an instance of a different Behavior or any other type (denoted by T) that provides
            the necessary context for the behavior.
        pool (model.Collection[Event]):
             A collection of events that are within the scope of what the behavior can handle.
            This is where events are pooled and managed by the behavior.
        Note:
            The actual types for the attributes `concurrency_kind`, `activity`, and `context` are defined
            externally and should be supplied during the usage of this class.

    """

    """
    A class that models a behavior and manages concurrent execution of activities in response to events.
    
    Attributes:
        concurrency_kind (ClassVar[ConcurrencyKind]):
            A class variable that specifies the concurrency mechanism used by the behavior. This might refer to an enumeration that defines whether the behavior is sequential, parallel or any other type of concurrency control.
            activity (Callable[['Event'], Future]): A callable attribute that represents the action or function to be triggered in response to an event. This callable takes an 'Event' object as an argument and returns a 'Future' object, facilitating asynchronous operation.
            context (Union[T, 'Behavior']):
            The context in which the behavior operates. It can either be a generic type 'T' or an instance of 'Behavior', depending on how the behavior is defined and used. This allows the behavior to be adaptable and possibly nested or composed of other behaviors.
            pool (model.Collection[Event]): A collection attribute that holds 'Event' objects to be processed by the behavior. This can be any collection-type object as defined by the 'model' module that is capable of managing and storing multiple events.
            Note that concrete subclasses should define the specifics of concurrency control, the actual function of the activity, the relevant context, and the appropriate collection for the pool of events.
            
    """
    """
    A base class for defining behaviors in a system.
        Behaviors encapsulate actions that are triggered by events. Each behavior can
        be associated with its own concurrency mechanism, can target a callable to
        execute, and can maintain a context for execution. The behavior also
        manages a collection pool of events it is responsible for.

        Attributes:
            concurrency_kind (ClassVar[ConcurrencyKind]): A class-level variable that specifies
                the concurrency behavior (e.g., single-threaded, multi-threaded) that the derived
                behavior class will adhere to.
            activity (Callable[['Event'], Future]): A callable activity that the behavior executes
                when it processes an event. This callable typically returns a Future object that
                represents a potentially long-running computation.
            context (Union[T, 'Behavior']): The context in which the behavior's activity is
                executed. This can be a specific context data type T or another Behavior
                instance.
            pool (model.Collection[Event]): A collection that holds the events which the behavior
                is responsible to handle.
        Note:
            This class is intended to be subclassed and is part of a larger framework or
            system. It is not meant to be instantiated directly.

    """
    concurrency_kind: ClassVar[ConcurrencyKind] = None
    activity: Callable[["Event"], Future] = None
    context: Union[T, "Behavior"] = None
    pool: model.Collection[Event] = None


class StateMachine(Behavior, CompositeState):
    """
    A state machine implementation that inherits from both Behavior and CompositeState.
    This class encapsulates the concept of a state machine, where a 'submachine_state' acts as the current state of the machine. It provides a property that retrieves the current state of the state machine as a tuple.

    Attributes:
        submachine_state (State):
             An instance of State that represents the current state of the state machine.
        Properties:
        state (tuple[State]):
             A tuple containing the states from the interpreter's stack that is also a subtype of State. This represents the current state configuration of the state machine.

    """

    submachine_state: State = None

    @property
    def state(self) -> tuple[State]:
        """
        Property that returns a tuple of State instances from the interpreter's stack.
        This property iterates over the keys of the stack in the interpreter object, casts
        each key to a State type, and then filters out only those keys which are subtypes
        of State as determined by the `is_subtype` method of a `model.element`. It then returns
        the resulting State instances as a tuple.

        Returns:
            tuple[State]:
                 A tuple containing State instances derived from the interpreter's stack.

        """
        return tuple(
            cast(State, value)
            for value in self.interpreter.stack.keys()
            if model.element.is_subtype(value, State)
        )


class EntryKind(Enum):
    """
    An enumeration to distinguish between different types of entry kinds.
    This class is a subclass of Enum and provides two types of Entry Kinds:
    - `default`: Represents a default entry kind.
    - `explicit`: Represents an explicit entry kind.

    Attributes:
        default (str):
             A class variable for the default entry kind.
        explicit (str):
             A class variable for the explicit entry kind.

    """

    default = "default"
    explicit = "explicit"
