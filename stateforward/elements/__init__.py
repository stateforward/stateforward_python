"""

In this document, we provide a comprehensive overview of the `stateforward.elements` module, part of the StateForward framework. The module defines the primary building blocks used to model state machines, which include vertices, states, transitions, and events. These constructs encapsulate the behavior, conditions, and structure of state-based systems.

## Elements

### Vertex
A base class for objects that represent the nodes within a state machine. It has `outgoing` and `incoming` collections for transitions, as well as a `container` which refers to the region it belongs to.

#### FinalState
A special kind of vertex indicating a state that, once entered, signifies the completion of a process within a particular region of the state machine.

### Transition
Defines a pathway or a link between two vertices (`source` and `target`). Transitions can be governed by `events`, have an assigned `effect` (behavior), and be protected by a `guard` condition. Transitions also have a `kind` signifying their type (internal, local, external, or self) and a `path` describing the entry and exit states involved during the transition.

### PseudostateKind (Enum)
Enumerates the different kinds of special purpose states within a state machine, such as initial, choice, join, fork, and more.

### Pseudostate
A specialized form of vertex representing various control nodes within a state machine, such as initial states or decision points. Its `kind` is determined by PseudostateKind.

### TransitionKind (Enum)
Enumerates different kinds of transitions, such as internal, local, external, and self-transitions.

### TransitionPath
Represents the sequence of vertices one must enter (`enter`) and leave (`leave`) when performing a transition.

### ConcurrencyKind (Enum)
Enumerates the different concurrency models that can be used, such as threaded, threaded, multiprocessing, and asynchronous.

### Event
A base class for different types of events that can trigger transitions.

#### AnyEvent
Represents a wildcard event that matches any occurring event.

#### CallEvent
Defines an event that represents the invocation of a callable, with potential `results` and an operation to execute (`operation`).

#### TimeEvent
An event triggered based on time, with a `when` attribute specifying the timing.

#### ChangeEvent
An event triggered by a change in the system's conditions.

#### CompletionEvent
An event that indicates the completion of the activities within a state.

### Constraint
Defines a conditional expression or constraint that can influence the behavior of a transition (`condition`).

### CompositeState
A base class for complex states that may contain other states (regions).

### State
A simple or composite state within the state machine that can perform `entry`, `exit`, and `do_activity` behaviors. It may also contain `completion`, `deferred` events, and a reference to a `submachine`.

### Region
Represents a 'container' for states inside composite states or state machines. Maintains a `subvertex` collection for the vertices it encloses and references its `initial` state.

### Behavior and StateMachine
Defines abstract bases for behaviors and state machines, enabling the modeling of more complex functional behaviors within the system.

---
By exploring these elements, developers can model the states and transitions of their systems, defining exactly how their state machines should behave in response to events and conditions. Each class provides the necessary attributes and mechanisms to accomplish this, forming a foundational toolkit for state management.

"""
from .elements import *
from .functional import *
