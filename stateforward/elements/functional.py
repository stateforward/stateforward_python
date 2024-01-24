"""
This module contains the basic elements of the stateforward library.
"""
from typing import Callable, Union, Sequence, Type, Optional
from datetime import datetime, timedelta
from stateforward import model, elements
from uuid import uuid1


def initial(
    target: type[elements.Vertex],
    effect: Optional[
        Union[
            type[elements.Behavior], Callable[[elements.Behavior, elements.Event], None]
        ]
    ] = None,
) -> type[elements.Initial]:
    element = model.element.new(f"initial", (elements.Initial,))
    if not model.element.is_subtype(effect, elements.Behavior):
        effect = model.element.new(
            f"effect", bases=(elements.Behavior,), activity=effect
        )
    model.set_attribute(
        element,
        "transition",
        transition(target=target, effect=effect),
    )
    return element


def transition(
    event: Optional[Union[type[elements.Event], Sequence[type[elements.Event]]]] = None,
    target: Optional[type[elements.Vertex]] = None,
    source: Union[Sequence[type[elements.Vertex]], type[elements.Vertex]] = None,
    guard: Optional[
        Union[
            Callable[[elements.Constraint, elements.Event], bool],
            type[elements.Constraint],
        ]
    ] = None,
    effect: Optional[
        Union[
            type[elements.Behavior], Callable[[elements.Behavior, elements.Event], None]
        ]
    ] = None,
    type: type[elements.Transition] = elements.Transition,
    name: str = None,
) -> Union[type[elements.Transition], Sequence[type[elements.Transition]]]:
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
    if guard is not None and not model.element.is_subtype(guard, elements.Constraint):
        guard = constraint(guard)
    if effect is not None and not model.element.is_subtype(effect, elements.Behavior):
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
    decorated: Callable[[elements.Constraint, elements.Event], bool],
    type: type[elements.Constraint] = elements.Constraint,
) -> type[elements.Constraint]:
    return model.element.new(
        f"constraint_{getattr(decorated, '__name__', repr(decorated))}",
        (type,),
        condition=decorated,
    )


def behavior(
    decorated: Callable[[elements.Behavior, elements.Event], bool],
    name: Optional[str] = None,
    type: type[elements.Behavior] = elements.Behavior,
) -> type[elements.Constraint]:
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
    when: Callable[[elements.TimeEvent], bool] = None,
) -> type[elements.TimeEvent]:
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
        (elements.TimeEvent,),
        when=when,
    )


def event(name: str) -> type[elements.Event]:
    return model.element.new(name, (elements.Event,))


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
    if when is None:
        if isinstance(iso_or_year, str):
            when = datetime.fromisoformat(iso_or_year)
        else:
            when = datetime(
                iso_or_year, month, day, hour, minute, second, microsecond, tzinfo
            )
    return model.element.new("at", (elements.TimeEvent,), when=when)


def when(expr: Callable[[model.element.Element], bool]) -> type[elements.ChangeEvent]:
    name = f"when<{getattr(expr, '__name__', repr(expr))}>"
    return model.element.new(name, (elements.ChangeEvent,), expr=expr)


def join(
    target: type[elements.Vertex],
    effect=None,
    guard=None,
) -> Type[elements.Join]:
    join_element = model.element.new("join", (elements.Join,))
    model.add_owned_element_to(
        join_element,
        transition(target=target, source=join_element, effect=effect, guard=guard),
    )
    return join_element


def fork(
    *outgoing: Sequence[type[elements.Transition]], name: str = None
) -> Type[elements.Fork]:
    return model.element.new(
        name or "fork", (elements.Fork,), outgoing=model.collection(*outgoing)
    )


def choice(
    *transitions: Sequence[type[elements.Transition]],
    name=None,
) -> type["elements.Choice"]:
    # for enumerate, transition in transitions:
    #     transiiton.name = f"choice_{enumerate}"
    return model.element.new(
        name or "choice", (elements.Choice,), outgoing=model.collection(*transitions)
    )


def simple_state(
    name: str,
    entry: Union[
        type[elements.Behavior], Callable[[elements.Behavior, elements.Event], None]
    ] = None,
    exit: Union[
        type[elements.Behavior], Callable[[elements.Behavior, elements.Event], None]
    ] = None,
    activity: Union[
        type[elements.Behavior], Callable[[elements.Behavior, elements.Event], None]
    ] = None,
):
    if not model.element.is_subtype(entry, elements.Behavior):
        entry = behavior(entry)
    if not model.element.is_subtype(exit, elements.Behavior):
        exit = behavior(exit)
    if not model.element.is_subtype(activity, elements.Behavior):
        activity = behavior(activity)
    return model.element.new(
        name,
        (elements.State,),
        entry=entry,
        exit=exit,
        activity=activity,
    )


def entry_point(
    *transitions: Sequence[type[elements.Transition]],
    name: str = None,
) -> type[elements.State]:
    return model.element.new(
        name or "entry_point",
        (elements.EntryPoint,),
        outgoing=model.collection(*transitions),
    )


def exit_point(
    name: str = None,
) -> type[elements.State]:
    return model.element.new(
        name or "exit_point",
        (elements.ExitPoint,),
    )
