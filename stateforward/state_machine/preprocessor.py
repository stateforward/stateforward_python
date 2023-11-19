import asyncio
from inspect import iscoroutinefunction
from weakref import proxy
from asyncio import Queue as AsyncQueue
from typing import TYPE_CHECKING
from stateforward import model
from stateforward import elements


async def no_async_activity(self, event: "elements.Event"):
    pass


def no_activity(self, event: "elements.Event"):
    pass


def least_common_ancestor(
    node1: type["elements.Vertex"], node2: type["elements.Vertex"]
):
    if model.has_descendant(node1.container, node2):
        lca = node1.container
    elif model.has_descendant(node2.container, node1):
        lca = node2.container
    else:
        container = node1.container
        if container.state is None:
            return container
        lca = least_common_ancestor(container.state, node2)
    return lca


class StateMachinePreprocessor(model.Preprocessor):
    """
    A preprocessor for state machines that ensures that various elements of the model are correctly processed.

    This includes processing vertices, states, composite states, transitions, regions, and pseudostates to establish the correct relationships and properties necessary for the machine's operation. Additionally, it manages handling behavior activities, entry and exit points, and transition paths.

    Attributes:
        preprocessed (set): A set to keep track of already preprocessed elements to avoid re-processing.
    """

    def preprocess_vertex(self, element: type["elements.Vertex"]):
        container = model.find_ancestor(
            element,
            lambda owned_element: model.is_subtype(owned_element, elements.Region),
        )
        model.set_attribute(element, "container", container)

        outgoing = list(element.outgoing.elements()) if element.outgoing else []
        incoming = list(element.incoming.elements()) if element.incoming else []
        for transition in model.find_descendants(
            element.model,
            lambda owned_element: model.is_subtype(owned_element, elements.Transition),
        ):
            if (
                transition.source or transition.owner
            ) == element and transition not in outgoing:
                outgoing.append(transition)
            elif transition.target == element and transition not in incoming:
                incoming.append(transition)
        model.set_attribute(element, "outgoing", model.collection(*outgoing))
        model.set_attribute(element, "incoming", model.collection(*incoming))

    def preprocess_state(self, element: type["elements.State"]):
        if element.submachine is None:
            self.preprocess_composite_state(element)
        else:
            for region in element.region.elements():
                model.set_attribute(region, "state", element)
                model.set_attribute(region, "state_machine", None)
                # model.remove_owned_element(element, region)

        self.preprocess_vertex(element)

        for behavior in ("entry", "exit", "do_activity"):
            if getattr(element, behavior) is None:
                model.set_attribute(
                    element,
                    behavior,
                    model.new_element(behavior, bases=(elements.Behavior,)),
                )

    def preprocess_composite_state(self, element: type["elements.CompositeState"]):
        transitions = []
        subvertex = []
        regions = []
        for owned_element in element.owned_elements:
            if model.is_subtype(owned_element, elements.Transition):
                transitions.append(owned_element)
            elif model.is_type(owned_element, model.Collection) and all(
                model.is_subtype(_child, elements.Transition)
                and not model.is_association(_child)
                for _child in owned_element.owned_elements
            ):
                transitions.extend(owned_element.elements())
            elif model.is_subtype(owned_element, elements.Vertex):
                subvertex.append(owned_element)
            elif model.is_subtype(owned_element, elements.Region):
                regions.append(owned_element)
        if subvertex:
            new_region = model.new_element(
                f"region_{len(regions)}",
                bases=(elements.Region,),
            )
            for owned_element in subvertex + transitions:
                if owned_element.owner:
                    owned_element = model.remove_owned_element(
                        owned_element.owner, owned_element
                    )
                if owned_element.name in element.attributes:
                    model.set_attribute(new_region, owned_element.name, owned_element)
                else:
                    model.add_owned_element(new_region, owned_element)
            model.set_attribute(
                element,
                "region",
                model.collection(new_region, *regions),
            )
        elif regions:
            model.set_attribute(element, "region", model.collection(*regions))

        else:
            model.set_attribute(element, "region", model.collection())

    def create_transition_path(self, transition: type["elements.Transition"]):
        enter = []
        leave = []
        # TODO this can be reduced
        if transition.kind == elements.TransitionKind.external:
            leave.append(transition.source)
            for ancestor in model.ancestors(transition.source):
                if ancestor.qualified_name == transition.container.qualified_name:
                    break
                if model.is_subtype(ancestor, elements.State):
                    leave.append(ancestor)
            for ancestor in model.ancestors(transition.target):
                if ancestor.qualified_name == transition.container.qualified_name:
                    break
                if model.is_subtype(ancestor, elements.State):
                    enter.append(ancestor)
            enter.append(transition.target)
        elif transition.kind == elements.TransitionKind.local:
            for ancestor in model.ancestors(transition.target):
                if ancestor.qualified_name == transition.source.qualified_name:
                    break
                if model.is_subtype(ancestor, elements.State):
                    enter.append(ancestor)
            enter.append(transition.target)
        elif transition.kind == elements.TransitionKind.self:
            leave.append(transition.source)
            enter.append(transition.target)
        return model.new_element(
            "path",
            bases=(elements.TransitionPath,),
            enter=model.collection(*enter),
            leave=model.collection(*leave),
        )

    def preprocess_final_state(self, element: type["elements.FinalState"]):
        self.preprocess_vertex(element)

    def preprocess_transition(self, element: type["elements.Transition"]):
        if element.source is None:
            owner = element.owner
            if model.is_subtype(owner, model.Collection):
                owner = owner.owner
            if not model.is_subtype(owner, elements.Vertex):
                raise ValueError(
                    f"transition {element.qualified_name} has no source and is not owned by a state"
                )
            # transition source always defaults to the parent
            model.set_attribute(element, "source", owner)

        # yield from self.wait_for_completion_of(element.source)
        self.preprocess_element(element.source)
        if element.events is None:
            if model.is_subtype(element.source, elements.State):
                completion = element.source.completion
                if completion is None:
                    completion = model.new_element(
                        f"completion",
                        (elements.CompletionEvent,),
                    )
                    model.set_attribute(element.source, "completion", completion)

                model.set_attribute(
                    element,
                    "events",
                    model.collection(
                        completion,
                    ),
                )

        if element.effect is None:
            model.set_attribute(
                element,
                "effect",
                model.new_element(
                    "effect",
                    (elements.Behavior,),
                    activity=no_async_activity
                    if element.model.concurrency_kind
                    is elements.ConcurrencyKind.asynchronous
                    else no_activity,
                ),
            )
        container = element.source.container
        if element.source == element.target:
            element.kind = elements.TransitionKind.self
        elif element.target is None:
            element.kind = elements.TransitionKind.internal
        elif model.has_descendant(element.source, element.target):
            element.kind = elements.TransitionKind.local
        else:
            self.preprocess_element(element.target)
            element.kind = elements.TransitionKind.external
            container = least_common_ancestor(element.source, element.target)
        if container is None:
            raise ValueError(f"transition {element.qualified_name} has no container")
        model.set_attribute(element, "container", container)
        path = self.create_transition_path(element)
        model.set_attribute(element, "path", path)

    def preprocess_region(self, element: type["elements.Region"]):
        from stateforward.elements import StateMachine

        def initial_filter(vertex):
            return model.is_subtype(vertex, elements.Initial)

        model.set_attribute(
            element,
            "subvertex",
            model.collection(
                *model.find_owned_elements(
                    element,
                    lambda owned_element: model.is_subtype(
                        owned_element, elements.Vertex
                    ),
                )
            ),
        )
        initial = getattr(element, "initial", None)
        if initial is None:
            initial = model.find_owned_element(element, initial_filter)
            model.set_attribute(element, "initial", initial)

        parent = element.owner
        if not model.is_subtype(parent, (StateMachine, elements.State)):
            parent = parent.owner
        model.set_attribute(
            element,
            "state",
            parent if model.is_subtype(parent, elements.State) else None,
        )
        model.set_attribute(
            element,
            "state_machine",
            parent if model.is_subtype(parent, StateMachine) else None,
        )

    def preprocess_processor(self, element: type["model.Interpreter"]):
        concurrency_kind = element.model.concurrency_kind
        if concurrency_kind == elements.ConcurrencyKind.asynchronous:
            model.set_attribute(element, "queue", AsyncQueue)

    def preprocess_call_event(self, element: type["elements.CallEvent"]):
        if asyncio.iscoroutinefunction(element.operation):

            async def __call__(self, *args, **kwargs):
                value = await self.operation(*args, **kwargs)
                self.results.set_result(value)
                return value

        else:

            def __call__(self, *args, **kwargs):
                value = self.operation(*args, **kwargs)
                self.results.set_result(value)
                return value

        setattr(element, "__call__", __call__)

    def preprocess_change_event(self, element: type[elements.ChangeEvent]):
        element.condition = asyncio.Condition

    def preprocess_behavior(self, element: type["elements.Behavior"]):
        concurrency_kind = element.model.concurrency_kind
        activity = element.activity
        if activity is None:
            if concurrency_kind == elements.ConcurrencyKind.asynchronous:
                activity = no_async_activity
            else:
                activity = no_activity
        elif (
            concurrency_kind == elements.ConcurrencyKind.asynchronous
            and not iscoroutinefunction(element.activity)
        ):

            def activity(self, event: "elements.Event", _activity=element.activity):
                return _activity(self, event)

        activity.__module__ = element.model.__module__
        activity.__qualname__ = f"{element.qualified_name}.activity"
        model.set_attribute(element, "activity", activity)
        context = model.find_ancestor(
            element, lambda ancestor: model.is_subtype(ancestor, elements.Behavior)
        )
        self.preprocess_owned_elements(element)

        events = []
        for descendant in model.all_owned_elements(element):
            if model.is_subtype(descendant, elements.Event):
                events.append(descendant)
        model.set_attribute(element, "pool", model.collection(*events))

        model.set_attribute(
            element,
            "context",
            context,
        )

    def preprocess_state_machine(self, element: type["elements.Behavior"]):
        from stateforward.state_machine.interpreters.asynchronous import (
            AsyncStateMachineInterpreter,
        )

        self.preprocess_composite_state(element)
        if element.region.length == 0:
            raise ValueError(f"state machine {element.qualified_name} has no regions")
        self.preprocess_behavior(element)
        model.sort_collection(
            element.pool,
            lambda event: not model.is_subtype(event, elements.CompletionEvent),
        )
        if element.model.concurrency_kind is None:
            model.set_attribute(
                element,
                "interpreter",
                model.new_element("interpreter", bases=(AsyncStateMachineInterpreter,)),
            )
