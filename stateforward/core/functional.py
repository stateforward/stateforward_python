"""

Module `functional` provides a set of functions to create various state machine components such as initial states, transitions, constraints, behaviors, events, and composite structures like forks, joins, and choices. 

The module uses a custom model building framework, which applies a functional approach to define the behavior of various elements in a state machine. This approach enables flexible construction and validation of state machine configurations.

Each function is designed to construct a specific type of element, such as a state, an event, a transition, etc., and returns an instance of the corresponding element type. These elements can be assembled to form complex state machine behaviors. Optional parameters allow for customization of these elements, such as specifying entry and exit behaviors for states, conditions for transitions, or timing for time-based events.

The use of Python's typing module ensures that the functions' arguments and return types are well-documented, enhancing code readability and maintenance.

Key functions in the module:

- `initial`: Create an initial pseudo-state with an optional effect.
- `transition`: Create a transition between source and target states, with optional events, guards, and effects.
- `constraint`: Define a constraint function to act as a guard for transitions.
- `behavior`: Define a behavior function to be invoked on state entry, exit, or during an activity.
- `event`: Create an event that can trigger transitions.
- `after`: Create a time event that triggers after a specified delay.
- `at`: Create a time event that triggers at a specific datetime.
- `when`: Create a change event based on a custom expression.
- `join`: Create a join pseudo-state to merge multiple incoming transitions.
- `fork`: Create a fork pseudo-state to split behavior into multiple concurrent paths.
- `choice`: Create a choice pseudo-state to conditionally trigger different transitions.
- `simple_state`: Define a simple state element with associated entry, exit, or ongoing activity behaviors.
- `entry_point`: Create a designated start point for a region within a state machine.
- `exit_point`: Create a designated exit point for a state machine region.
- `final_state`: Create a final state to represent the completion of the state machine or a region within it.

The module allows for significant customization of state machine elements, making it a powerful tool for modeling a variety of behaviors.
"""
from typing import Callable, Union, Sequence, Type, Optional
from datetime import datetime, timedelta
from stateforward import model, core


def initial(
    target: type[core.Vertex],
    effect: Optional[
        Union[type[core.Behavior], Callable[[core.Behavior, core.Event], None]]
    ] = None,
) -> type[core.Initial]:
    """
    Creates an initial state element with an optional effect that defines its transition behavior.
    This function creates an 'initial' element that represents the starting point for state transitions within a state machine model. The 'initial' element is an instance of 'core.Initial'. It may include an optional effect, which can either be a subclass of 'core.Behavior' or a callable that takes a 'core.Behavior' instance and a 'core.Event'. If the effect provided is not a subtype of 'core.Behavior', the function will create a new 'effect' element with the provided callable as its activity. The transition is then defined with the specified target state and effect, and this transition is set as an attribute of the 'initial' element.
    
    Args:
        target (type[core.Vertex]):
             The state to which the transition occurs from this initial element.
        effect (Optional[Union[type[core.Behavior], Callable[[core.Behavior, core.Event], None]]]):
             An optional behavior or callable that defines the effect of the transition.
    
    Returns:
        type[core.Initial]:
             A new 'initial' element instance representing the initial state of a state machine with the specified transition behavior.

    """
    element = model.element.new("initial", (core.Initial,))
    if not model.element.is_subtype(effect, core.Behavior):
        effect = model.element.new("effect", bases=(core.Behavior,), activity=effect)
    model.set_attribute(
        element,
        "transition",
        transition(target=target, effect=effect),
    )
    return element


def transition(
    event: Optional[Union[type[core.Event], Sequence[type[core.Event]]]] = None,
    target: Optional[type[core.Vertex]] = None,
    source: Union[Sequence[type[core.Vertex]], type[core.Vertex]] = None,
    guard: Optional[
        Union[
            Callable[[core.Constraint, core.Event], bool],
            type[core.Constraint],
        ]
    ] = None,
    effect: Optional[
        Union[type[core.Behavior], Callable[[core.Behavior, core.Event], None]]
    ] = None,
    type: type[core.Transition] = core.Transition,
    name: str = None,
) -> Union[type[core.Transition], Sequence[type[core.Transition]]]:
    """
    Creates a new Transition element based on the provided parameters.
    This function generates a transition in a model, which can be defined with or without an event, and with optional guard and effect functions. It is capable of creating multiple transitions if presented with a list or sequence of source vertices.
    
    Args:
        event (Union[type[core.Event], Sequence[type[core.Event]]], optional):
             The event or events that trigger the transition.
        target (type[core.Vertex], optional):
             The vertex where the transition leads to.
        source (Union[Sequence[type[core.Vertex]], type[core.Vertex]], optional):
             The source vertex or vertices from where the transition originates.
        guard (Union[Callable[[core.Constraint, core.Event], bool], type[core.Constraint]], optional):
             A callable or Constraint that serves as the condition for the transition to occur.
        effect (Union[type[core.Behavior], Callable[[core.Behavior, core.Event], None]], optional):
             A callable or Behavior that represents the action taken when the transition occurs.
        type (type[core.Transition]):
             The type of the Transition element to create. Defaults to core.Transition.
        name (str, optional):
             The name of the transition. If not provided, a name is generated.
    
    Returns:
        Union[type[core.Transition], Sequence[type[core.Transition]]]:
             A new Transition element or a sequence of Transition elements.
    
    Raises:
        ValueError:
             If both 'source' and 'target' are None, this function raises a ValueError.

    """
    if isinstance(source, (list, tuple)):
        return model.collection(
            *(transition(event, target, _source, guard, effect) for _source in source)
        )
    elif source is not None and target is not None:
        # source = model.association(source)
        # target = model.association(target)
        if name is None:
            name = f"transition_from_{model.name_of(source)}_to_{model.name_of(target)}"
    elif target:
        # target = model.association(target)
        if name is None:
            name = f"transition_to_{model.name_of(target)}"
    elif source:
        # source = model.association(source)
        if name is None:
            name = f"transition_from_{model.name_of(source)}"
    else:
        raise ValueError("source and target cannot both be None")
    if event is None:
        events = None
    else:
        events = (
            model.collection(*event)
            if isinstance(event, (list, tuple))
            else model.collection(event)
        )
    if guard is not None and not model.element.is_subtype(guard, core.Constraint):
        guard = constraint(guard)
    if effect is not None and not model.element.is_subtype(effect, core.Behavior):
        effect = behavior(effect)
    new_transition = model.element.new(
        name,
        (type,),
        events=events,
        target=target,  # don't take ownership of the target
        source=source,  # don't take ownership of the source
        guard=guard,
        effect=effect,
    )
    return new_transition


def constraint(
    decorated: Callable[[core.Constraint, core.Event], bool],
    type: type[core.Constraint] = core.Constraint,
) -> type[core.Constraint]:
    """
    Creates a new constraint subclass with a specific condition.
    This function dynamically creates a new subclass of a constraint with a provided condition function. The new subclass
    is named based on the decorated function's name, and it includes the condition as its key behavior.
    
    Args:
        decorated (Callable[[core.Constraint, core.Event], bool]):
             A callable that represents the condition function.
            This function should accept a `core.Constraint` object and a `core.Event` object as parameters and return a
            boolean value indicating whether the constraint's condition is satisfied.
        type (type[core.Constraint], optional):
             The base class from which the new subclass will inherit.
            Defaults to 'core.Constraint', indicating that the new subclass will be a direct subclass of 'core.Constraint'.
    
    Returns:
        type[core.Constraint]:
             A new subclass of the specified 'type' with the 'decorated' function as a condition.

    """
    return model.element.new(
        f"constraint_{getattr(decorated, '__name__', repr(decorated))}",
        (type,),
        condition=decorated,
    )


def behavior(
    decorated: Callable[[core.Behavior, core.Event], bool],
    name: Optional[str] = None,
    type: type[core.Behavior] = core.Behavior,
) -> type[core.Constraint]:
    """
    Creates a new `core.Constraint` subclass that is associated with a specific behavior function.
    This function creates a new class based on a provided behavior function and optionally a specific name and type. The new class is a subclass of `core.Constraint` and is constructed using the `model.element.new` function with additional specifications such as the behavior function and a generated name if not explicitly provided.
    
    Args:
        decorated (Callable[[core.Behavior, core.Event], bool]):
             The behavior function that is to be associated with the new constraint subclass.
            It should accept a `core.Behavior` instance and a `core.Event` instance, returning a boolean based on the specified condition.
        name (Optional[str]):
             An optional name for the new constraint subclass. If not given, a name is generated based on the
            `decorated` function's name.
        type (type[core.Behavior]):
             The type of the behavior that will be the base for the new subclass. Defaults to
            `core.Behavior` if not provided.
    
    Returns:
        type[core.Constraint]:
             A new subclass of `core.Constraint` that has been associated with the specified behavior function.

    """
    return model.element.new(
        name or f"behavior_{getattr(decorated, '__name__', repr(decorated))}",
        (type,),
        activity=decorated,
    )


def after(
    hours: float = 0.0,
    minutes: float = 0.0,
    seconds: float = 0.0,
    milliseconds: float = 0.0,
    microseconds=0.0,
    days=0.0,
    when: Callable[[core.TimeEvent], bool] = None,
) -> type[core.TimeEvent]:
    """
    Creates a new `TimeEvent` type that triggers after a specified time duration or when a certain condition is met.
    This function facilitates the creation of time-based events. The event is triggered after the cumulative
    time specified by hours, minutes, seconds, milliseconds, and microseconds parameters, or on the condition
    defined by the `when` callable. If `when` is provided, it overrides the time-based parameters.
    
    Args:
        hours (float, optional):
             The number of hours to wait before the event triggers. Default is 0.0.
        minutes (float, optional):
             The number of minutes to wait before the event triggers. Default is 0.0.
        seconds (float, optional):
             The number of seconds to wait before the event triggers. Default is 0.0.
        milliseconds (float, optional):
             The number of milliseconds to wait before the event triggers. Default is 0.0.
        microseconds (float, optional):
             The number of microseconds to wait before the event triggers. Default is 0.0.
        days (float, optional):
             The number of days to wait before the event triggers. Default is 0.0.
        when (Callable[[core.TimeEvent], bool], optional):
             A callable that returns a boolean value. The event
            is triggered when this callable returns `True`. If provided, it takes precedence over the time
            parameters.
    
    Returns:
        type[core.TimeEvent]:
             A new subclass of `core.TimeEvent` that represents the event configured
            to trigger after the specified time or when the `when` condition is met.

    """
    if when is None:
        when = timedelta(
            hours=hours,
            minutes=minutes,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=microseconds,
            days=days,
        )
        name = f"after<{when}>"
    else:
        name = f"after<{getattr(when, '__name__', repr(when))}>"
    return model.element.new(
        name,
        (core.TimeEvent,),
        when=when,
    )


def event(name: str) -> type[core.Event]:
    """
    Creates a new event type with the given name.
    This function dynamically generates a new event type derived from the `core.Event` base class,
    using the provided name. The type is created using the `model.element.new` factory function.
    
    Args:
        name (str):
             The name of the event type to be created.
    
    Returns:
        type[core.Event]:
             A new event type subclassing `core.Event` with the given name.

    """
    return model.element.new(name, (core.Event,))


def at(
    iso_or_year,
    month,
    day,
    hour=0,
    minute=0,
    second=0,
    microsecond=0,
    tzinfo=None,
    when=None,
):
    """
    Creates a new TimeEvent model element with a specific timestamp.
    This function can take either an ISO-formatted date string or individual date and time components to create the timestamp. An additional 'when' parameter can be used to pass an existing datetime object directly.
    
    Args:
        iso_or_year (Union[str, int]):
             An ISO-formatted date string or the year component of the date.
        month (int):
             The month component of the date. Required if the first argument is a year.
        day (int):
             The day component of the date. Required if the first argument is a year.
        hour (int, optional):
             The hour component of the time. Defaults to 0.
        minute (int, optional):
             The minute component of the time. Defaults to 0.
        second (int, optional):
             The second component of the time. Defaults to 0.
        microsecond (int, optional):
             The microsecond component of the time. Defaults to 0.
        tzinfo (timezone, optional):
             The timezone information. Defaults to None.
        when (datetime, optional):
             An existing datetime object. If provided, other parameters are ignored. Defaults to None.
    
    Returns:
        element.Element:
             A TimeEvent model element initialized with the specified timestamp.

    """
    if when is None:
        if isinstance(iso_or_year, str):
            when = datetime.fromisoformat(iso_or_year)
        else:
            when = datetime(
                iso_or_year, month, day, hour, minute, second, microsecond, tzinfo
            )
    return model.element.new("at", (core.TimeEvent,), when=when)


def when(expr: Callable[[model.element.Element], bool]) -> type[core.ChangeEvent]:
    """
    Creates a new ``ChangeEvent`` subclass which is triggered based on a specified expression.
    This function dynamically creates a subclass of ``ChangeEvent`` with a unique name derived from the
    expression's name or its string representation if the expression lacks a ``__name__`` attribute. The
    created class is designed to be triggered when the given expression evaluates to true.
    
    Args:
        expr (Callable[[model.element.Element], bool]):
             A callable that takes an instance of
            ``model.element.Element`` as its only argument and returns a boolean value. The expression is used to
            evaluate whether the ``ChangeEvent`` should be triggered.
    
    Returns:
        type[core.ChangeEvent]:
             A new subclass of ``core.ChangeEvent`` that incorporates the provided
            expression for its triggering condition.

    """
    name = f"when<{getattr(expr, '__name__', repr(expr))}>"
    return model.element.new(name, (core.ChangeEvent,), expr=expr)


def join(
    target: type[core.Vertex],
    effect=None,
    guard=None,
) -> Type[core.Join]:
    """
    Generates a new Join element and creates a transition to the specified target Vertex.
    This function instantiates a new Join element within the model and associates it with a transition. The transition is
    directed towards the given target Vertex, and can optionally include an effect and a guard. The newly
    created Join element is then returned.
    
    Args:
        target (type[core.Vertex]):
             The target Vertex for the transition originating from the join.
        effect (optional):
             The effect to be triggered by the transition. Defaults to None.
        guard (optional):
             The guard condition that must be true for the transition to trigger. Defaults to None.
    
    Returns:
        Type[core.Join]:
             The newly created Join element associated with the modeled transition.

    """
    join_element = model.element.new("join", (core.Join,))
    model.add_owned_element_to(
        join_element,
        transition(target=target, source=join_element, effect=effect, guard=guard),
    )
    return join_element


def fork(
    *outgoing: Sequence[type[core.Transition]], name: str = None
) -> Type[core.Fork]:
    """
    Creates a new `core.Fork` element with the specified outgoing transitions and name.
    This factory function constructs a new `core.Fork` instance that inherits from a
    collection of outgoing `core.Transition` types. If a name is provided, it sets the
    name of the new `core.Fork` element; otherwise, it assigns a default name 'fork'.
    
    Args:
        *outgoing (Sequence[type[core.Transition]]):
             A variable number of `core.Transition` types
            that will be the outgoing transitions for the fork.
        name (str, optional):
             The name to assign to the new `core.Fork` element. If unspecified,
            the name defaults to 'fork'.
    
    Returns:
        Type[core.Fork]:
             A new `core.Fork` instance with the specified outgoing transitions and name.

    """
    return model.element.new(
        name or "fork", (core.Fork,), outgoing=model.collection(*outgoing)
    )


def choice(
    *transitions: Sequence[type[core.Transition]],
    name=None,
) -> type["core.Choice"]:
    # for enumerate, transition in transitions:
    #     transiiton.name = f"choice_{enumerate}"
    """
    Creates a new Choice model element with optional transitions.
    This function creates a new Choice model element, which represents a point in the workflow where
    one among multiple transitions can be taken. It allows for the dynamic specification of transitions
    as part of the construct, with the option to provide a name for the choice element.
    
    Args:
        *transitions (Sequence[type[core.Transition]]):
             A variable number of transition sequences that
            represents outgoing transitions from the choice element.
        name (Optional[str]):
             An optional name for the choice element. If not provided, a default name
            'choice' is used.
    
    Returns:
        type['core.Choice']:
             A new Choice model element with specified outgoing transitions.

    """
    """
    Creates a new 'Choice' element with the given transitions and name.

    Args:

        *transitions (Sequence[type[core.Transition]]):
             A variable number of transition sequences to be included as outgoing transitions for the choice element.

        name (Optional[str]):
             An optional name for the choice element. If not provided, 'choice' is used as the default name.

    Returns:

        type['core.Choice']:
             A new Choice element with the specified outgoing transitions and name.

    """
    """
    Creates a new instance of the 'core.Choice' class with outgoing transitions.

    Args:
        *transitions (Sequence[type[core.Transition]]):
            A variable number of sequences where each sequence contains
            'core.Transition' type elements to be used as outgoing transitions for the choice element.
            name (Optional[str], None):
            An optional name for the new choice element. If not provided, 'choice' will be used as the default name.
            Returns:
            type['core.Choice']:
            A new instance of the 'core.Choice' class with the specified outgoing transitions.

    """
    """
    Creates a new Choice element with a given name and a sequence of transitions.
    This function constructs a new Choice element, which is typically used in state machine models to
    represent a decision point where the outcome is determined by conditions on the transitions.
    It allows for the dynamic arrangement of the transitions that can be taken from this choice point.

    Args:
        *transitions (Sequence[type[core.Transition]]):
            A sequence of Transition class references that
            are potential outgoing transitions from the new Choice element.
            name (Optional[str]):
            An optional name for the new Choice element. If no name is provided, the
            default name 'choice' will be used.

    Returns:
        type['core.Choice']:
            A new Choice element with the specified outgoing transitions and name.


    """
    """
    Creates a new choice element with given transitions.
    
    The function dynamically creates a new choice element, which is a type of core.Choice. It allows one to specify multiple transition elements that act as outgoing connections from this choice. An optional name can be provided; if not specified, the choice element will have the default name 'choice'.
    
    Args:
    *transitions (Sequence[type[core.Transition]]): A variable number of transition elements that will be associated with the choice element as outgoing connections.
    name (Optional[str]): An optional name for the choice element. If not specified, defaults to 'choice'.
    
    Returns:
    type['core.Choice']: A new choice element configured with the given transitions and name.

    """
    """
Creates a new Choice element with the given transitions.
        
This function generates a new Choice element, optionally with a specified name, and
    sets up the outgoing transitions provided. If no name is given, it defaults to 'choice'.
        
Args:
*transitions (Sequence[type[core.Transition]]): A variable number of transition sequences.
Each transition is of the type specified by core.Transition or a subclass of it.
        name (Optional[str]): An optional name for the Choice element. If not provided, defaults to 'choice'.
            
Returns:
type['core.Choice']: The newly created Choice element with the specified transitions.

    """
    """
    Creates a new Choice element with specified transitions and an optional name.
    
    This function constructs a Choice element, which is a part of a state machine model. The Choice element
    represents a decision point where one of several transition options can be taken based on
    some condition. The function allows for a variable number of transitions to be passed as
    arguments, and an optional name to be associated with the Choice element.
    
    Args:
    *transitions (Sequence[type[core.Transition]]): A variable number of transition elements
    indicating the possible paths that can be taken from this choice point.
    name (Optional[str]): An optional name given to the Choice element for identification. If no
    name is provided, a default name 'choice' will be used.
    
    Returns:
    type['core.Choice']: A new Choice element initialized with the provided transitions and
    the given or default name.

    """
    """
        Creates a new choice element in a model with given transitions.
        The function creates a new choice element, which is typically used in
        modeling decision points with multiple possible outcomes. It can be given
        a name and a sequence of transitions that serve as outgoing paths from
        the choice element.
        Args:
            *transitions (Sequence[type[core.Transition]]): A sequence of
                `core.Transition` type elements that will be used as outgoing
                transitions for the choice element.
            name (Optional[str]): An optional name for the choice element. If no
                name is provided, 'choice' will be used as the default name.
        Returns:
            type['core.Choice']: A new choice element with the specified outgoing
                transitions and name.
    """
    """
    Creates a new core.Choice element with a name and a sequence of transitions.
        The function constructs a new core.Choice element, which is a model element used to
        represent a point in a process where one among several transitions can be taken.
        Args:
            *transitions (Sequence[type[core.Transition]]): A variable number of Transition objects
                that can potentially be taken from this choice point.
            name (Optional[str]): An optional name for the core.Choice element. If no name is provided,
                a default name 'choice' is used.
        Returns:
            type['core.Choice']: A new instance of core.Choice, which is a subclass of
                the provided transitions, with the specified name and outgoing transitions.
        Raises:
            TypeError: If any of the provided transitions are not of type core.Transition.
    """
    """
    Creates a new Choice model element with specified transitions and an optional name.
    Args:
        *transitions (Sequence[type[elements.Transition]]): A variable number of Transition sequences to be associated with the Choice.
        name (Optional[str], optional): An optional name for the Choice element. If not provided, 'choice' is used as a default name.
    Returns:
        type['core.Choice']: A new instance of the core.Choice class with the provided transitions.
    """
    return model.element.new(
        name or "choice", (core.Choice,), outgoing=model.collection(*transitions)
    )


def simple_state(
    name: str,
    entry: Union[
        type[core.Behavior], Callable[[core.Behavior, core.Event], None]
    ] = None,
    exit: Union[
        type[core.Behavior], Callable[[core.Behavior, core.Event], None]
    ] = None,
    activity: Union[
        type[core.Behavior], Callable[[core.Behavior, core.Event], None]
    ] = None,
):
    """
    Creates a simple state with optional entry, exit, and activity behaviors.
    A convenience function that simplifies the creation of a state object with optional behaviors for entry, exit, and activity. If the provided entry, exit, and activity are not already subtypes of `core.Behavior`, they are converted using the `behavior` function.
    
    Args:
        name (str):
             The name of the state.
        entry (Union[type[core.Behavior], Callable[[core.Behavior, core.Event], None]], optional):
             The entry behavior for the state. Can be a subclass of `core.Behavior` or a callable.
            Defaults to None, indicating no entry behavior.
        exit (Union[type[core.Behavior], Callable[[core.Behavior, core.Event], None]], optional):
             The exit behavior for the state. Can be a subclass of `core.Behavior` or a callable.
            Defaults to None, indicating no exit behavior.
        activity (Union[type[core.Behavior], Callable[[core.Behavior, core.Event], None]], optional):
             The activity behavior for the state. Can be a subclass of `core.Behavior` or a callable.
            Defaults to None, indicating no activity behavior.
    
    Returns:
        type[core.State]:
             A new state object of type `core.State` with the specified entry, exit, and activity behaviors.

    """
    if not model.element.is_subtype(entry, core.Behavior):
        entry = behavior(entry)
    if not model.element.is_subtype(exit, core.Behavior):
        exit = behavior(exit)
    if not model.element.is_subtype(activity, core.Behavior):
        activity = behavior(activity)
    return model.element.new(
        name,
        (core.State,),
        entry=entry,
        exit=exit,
        activity=activity,
    )


def entry_point(
    *transitions: Sequence[type[core.Transition]],
    name: str = None,
) -> type[core.State]:
    """
    Creates a new entry point state in a state machine model.
    This function constructs a new state object that acts as an entry point in the state machine. It aggregates outgoing transitions from the entry point and optionally allows naming the entry point state for identification.
    
    Args:
        *transitions (Sequence[type[core.Transition]]):
             A sequence of transition types that will originate from the new entry point. These transitions define the possible next states from the entry point.
        name (str, optional):
             An optional name for the entry point state. If no name is provided, it defaults to the string 'entry_point'.
    
    Returns:
        type[core.State]:
             A new state object that represents the entry point in the state machine. It is a subclass of core.State, possibly with additional characteristics inherent to core.EntryPoint class.

    """
    return model.element.new(
        name or "entry_point",
        (core.EntryPoint,),
        outgoing=model.collection(*transitions),
    )


def exit_point(
    name: str = None,
) -> type[core.State]:
    """
    Creates a new instance of ExitPoint within the model.
    The function is intended to create a new element of type ExitPoint in the model, with an optional name provided.
    If no name is given, it uses 'exit_point' as the default name. The new instance is created as a subtype of core.State.
    
    Args:
        name (str, optional):
             The name to be assigned to the new ExitPoint. Defaults to None, and if not provided, 'exit_point' is used.
    
    Returns:
        type[core.State]:
             A new instance of ExitPoint which is a subtype of core.State.

    """
    return model.element.new(
        name or "exit_point",
        (core.ExitPoint,),
    )


def final_state():
    """
    Creates a new 'final' element that is an instance of core.FinalState.
    
    Returns:

    """
    return model.element.new("final", (core.FinalState,))
