"""

The `preprocessor` module is responsible for transforming the abstract representation of a state machine into a form that is ready for execution. This involves enriching the state machine's constituents, such as vertices, transitions, and regions, with additional metadata and associations that are necessary for runtime processing. The preprocessing stage plays a crucial role in setting up the state machine by defining the relationships between its parts, refining its behaviors, and establishing the conditions for event handling and state transition.

The module provides a `StateMachinePreprocessor` class which houses methods corresponding to different elements of the state machine, including:

- `preprocess_vertex`: It enriches vertices of the state machine by finding their containers, and categorizing incoming and outgoing transitions.

- `preprocess_state`: This method refines states by handling instances that are composite states and manages behaviors such as entry, exit, and activity. It also addresses the incorporation of submachines within states.

- `preprocess_composite_state`: Composite states, which contain regions and substates, are processed to ensure proper nesting and transition management.

- `create_transition_path`: Based on the kind of transition (external, local, or self), this method constructs a transition path that defines the order in which states are to be entered and exited during the transition.

- `preprocess_final_state`: This method handles the preprocessing of final states within the state machine.

- `preprocess_transition`: Transitions between states are prepared by associating sources, targets, containers, and events, and by determining the transition kind.

- `preprocess_region`: Regions, which are collections of vertices, are preprocessed such that each region is aware of its associated initial state and parent state machine or composite state.

- `preprocess_processor`: This method is responsible for setting up the interpreter with the correct asynchronous behavior if required by the state machine's concurrency model.

- `preprocess_call_event`, `preprocess_change_event`, and `preprocess_behavior`: These methods are dedicated to processing different types of events and behaviors, ensuring that their invocation and state changes are correctly managed according to whether the operations are coroutine functions or regular functions.

- `preprocess_state_machine`: Finally, this method ties together all preprocessing steps for the overall state machine, ensuring it is ready for execution with all the necessary properties and behaviors set up.

This module does not depend on specific external imports as it's mainly focused on setting up the state machine internals based on provided abstract definitions. The class and method definitions within the module leverage functionalities from the `stateforward` package which defines the model and core functionalities required for state machine processing.
"""
import asyncio
from inspect import iscoroutinefunction
from asyncio import Queue as AsyncQueue
from stateforward import model
from stateforward import core
from stateforward.state_machine.log import create_logger
from stateforward.protocols.logger import Logger


async def no_async_activity(self, event: "core.Event"):
    """
    Coroutines defined with async def syntax are meant to be invoked in an asynchronous event loop. However, "no_async_activity" is designated as a stub with a pass statement, which means it currently does not perform any action when awaited on an event. The presence of an event parameter of hypothetical type 'core.Event' implies that it may potentially handle an event object from some core library or framework in the future.

    """
    pass


def no_activity(self, event: "core.Event"):
    """
    Handles a situation where there is no activity for a given event.
    This method is a placeholder intended to be overridden by subclasses to define
    specific behavior when an event has no activity. By default, it does nothing.

    Args:
        event (core.Event):
             The event object that has no activity.

    """
    pass


def least_common_ancestor(node1: type["core.Vertex"], node2: type["core.Vertex"]):
    """
    Finds the least common ancestor between two vertices in a state machine graph.
    This function computes the least common ancestor (LCA) between two given vertices (node1 and node2). It operates under the assumption that each vertex has a container that can also be considered a vertex, and that the structure forms a hierarchical state machine. The LCA is defined as the lowest vertex at which the two input vertices are both descendants.

    Args:
        node1 (type['core.Vertex']):
             The first vertex for which to find the LCA.
        node2 (type['core.Vertex']):
             The second vertex for which to find the LCA.

    Returns:
        type['core.Vertex']:
             The least common ancestor of the two given vertices. Returns the container itself if one vertex is a descendant of another, or if the container of the first node doesn't have a state, indicating the top of the hierarchy.

    Raises:

    """
    if model.is_descendant_of(node1.container, node2):
        lca = node1.container
    elif model.is_descendant_of(node2.container, node1):
        lca = node2.container
    else:
        container = node1.container
        if container.state is None:
            return container
        lca = least_common_ancestor(container.state, node2)
    return lca


class StateMachinePreprocessor(model.Preprocessor):
    """
    A preprocessor class for state machine models that extends the functionality of a base model preprocessor.
    This class contains methods for preprocessing various elements within a state machine such as vertices, states, composite states, final states, transitions, regions, processors, call events, change events, behaviors, and the state machine itself. Each preprocessing method makes modifications to the elements, ensuring they are correctly configured within the state machine’s model, and establishing connections and relationships as needed.
    The class initializes with a logger attribute for logging messages and warnings during the preprocessing stage.

    Attributes:
        log (Logger):
             A logger instance used for outputting debug and error information during preprocessing.

    Methods:
        preprocess_vertex:
             Parses a vertex element, setting up its container, as well as outgoing and incoming transitions.
        preprocess_state:
             Processes a state element, handling submachine preprocessing and setting up entry, exit, and activity behaviors before delegating to vertex preprocessing.
        preprocess_composite_state:
             Handles preprocessing for composite states, creating regions, and categorizing internal transitions and subvertices.
        create_transition_path:
             Creates a transition path for transitions, factoring in the kind of transition and the hierarchy of source and target states.
        preprocess_final_state:
             Preprocessor for final state elements, mainly delegates to vertex preprocessing.
        preprocess_transition:
             Handles the preparation of transition elements, setting source, target, events effect, container, and transition path.
        preprocess_region:
             Processes region elements, setting up subvertices, initial states, state machines, and linkages to states or state machines.
        preprocess_processor:
             Prepares a model interpreter with the appropriate queue depending on the concurrency kind.
        preprocess_call_event:
             Processes call event elements, particularly attaching coroutine-friendly call methods when operations are asynchronous.
        preprocess_change_event:
             Preprocesses change event elements and sets up associated conditions.
        preprocess_behavior:
             Preprocessor for behavior elements, ensuring correct activities are set dependent on concurrency and establishing event pools and contexts.
        preprocess_state_machine:
             Comprehensive preprocessing for the state machine which involves state, behavior, and transition preprocessing along with additional configurations.

    """

    log: Logger = create_logger("StateMachinePreprocessor")

    def preprocess_vertex(self, element: type["core.Vertex"]):
        """
        Processes the given vertex by assigning it a container and categorizing its incoming and outgoing transitions.

        Args:
            element (type['core.Vertex']):
                 The vertex element to preprocess. This vertex should be part of a state machine model.
                The function logs the process of finding the container for the given vertex. If no container is found, an error is logged.
                Furthermore, the function identifies and categorizes all outgoing and incoming transitions of the vertex. It checks for transitions that are either originating from or targeting the element. It updates the 'outgoing' and 'incoming' attributes of the element with the newly found transitions.

        """
        logger = create_logger(f"preprocess_vertex({model.qualified_name_of(element)})")
        logger.debug(f"finding container for {model.qualified_name_of(element)}")
        container = model.find_ancestor_of(
            element,
            lambda owned_element: model.element.is_subtype(owned_element, core.Region),
        )

        if container is None:
            logger.error(f"vertex {model.qualified_name_of(element)} has no container")
        logger.debug(f"found container {model.qualified_name_of(container)}")
        model.set_attribute(element, "container", container)

        outgoing = list(element.outgoing) if element.outgoing else []
        incoming = list(element.incoming) if element.incoming else []
        for transition in model.find_descendants_of(
            model.of(element),
            lambda owned_element: model.element.is_subtype(
                owned_element, core.Transition
            ),
        ):
            if (
                transition.source or model.owner_of(transition)
            ) == element and transition not in outgoing:
                outgoing.append(transition)
            elif transition.target == element and transition not in incoming:
                incoming.append(transition)
        model.set_attribute(element, "outgoing", model.collection(*outgoing))
        model.set_attribute(element, "incoming", model.collection(*incoming))

    def preprocess_state(self, element: type["core.State"]):
        """
        Preprocesses a state in the state machine for further operations.
        This method takes a state as an argument and performs preprocessing step depending on whether it is a composite state or contains a submachine. If the state has a submachine, it gets logged. Additionally, it handles the preprocessing for the vertices of the state and ensures that 'entry', 'exit', and 'activity' behaviors are set on the state if they are not already defined.

        Args:
            element (core.State):
                 The state to preprocess. This type should be derived from a class that has an attribute 'submachine', which indicates whether the state is a simple state or a composite state with its own submachine.

        Returns:

        """
        if element.submachine is None:
            self.preprocess_composite_state(element)
        else:
            self.log.warning(
                f"preprocessing submachine {element} {getattr(element, 'entry', None)}"
            )
            # for region in element.submachine.regions.core():
            #     model.set_attribute(region, "state", element)
            #     model.set_attribute(region, "state_machine", None)

        self.preprocess_vertex(element)

        for behavior in ("entry", "exit", "activity"):
            if getattr(element, behavior) is None:
                model.set_attribute(
                    element,
                    behavior,
                    model.element.new(behavior, bases=(core.Behavior,)),
                )

    def preprocess_composite_state(self, element: type["core.CompositeState"]):
        """
        Processes a composite state to organize its sub-elements such as transitions, vertices, and regions.
        This method takes an element that is assumed to be a composite state, and iterates over its owned elements
        to categorize them into transitions, subvertices, and regions. If there are subvertices without an enclosing region,
        a new region is created to contain them along with any associated transitions. Existing regions within the composite state
        are preserved. The method then ensures that all transitions and subvertices are assigned to a region, either the new region
        or one of the existing ones, by updating their 'container' attributes. If an owned element corresponds to an attribute of
        the composite state, that association is maintained within the newly formed or existing region.

        Args:
            element (type['core.CompositeState']):
                 The composite state to be preprocessed, expected to be an instance of 'core.CompositeState'.

        Returns:
            None:
                 This method modifies the composite state element in-place and has no return value.

        """
        transitions = []
        subvertex = []
        regions = []
        for owned_element in [
            _owned_element
            for _owned_element in model.owned_elements_of(element)
            if not any(
                model.is_descendant_of(region, _owned_element) for region in regions
            )
        ]:
            if model.element.is_subtype(owned_element, core.Transition):
                transitions.append(owned_element)
            elif model.element.is_type(owned_element, model.Collection) and all(
                model.element.is_subtype(_child, core.Transition)
                for _child in owned_element
            ):
                transitions.extend(owned_element)
            elif model.element.is_subtype(owned_element, core.Vertex):
                subvertex.append(owned_element)
            elif model.element.is_subtype(owned_element, core.Region):
                regions.append(owned_element)
        if subvertex:
            new_region = model.element.new(
                f"region_{len(regions)}",
                bases=(core.Region,),
            )
            model.set_attribute(
                element,
                "regions",
                model.collection(new_region, *regions),
            )
            for owned_element in subvertex + transitions:
                if (
                    owner_of_owned_element := model.owner_of(owned_element)
                ) is not None:
                    owned_element = model.remove_owned_element_from(
                        owner_of_owned_element, owned_element
                    )
                    model.set_attribute(owned_element, "container", new_region)
                if (
                    owned_element_name := model.name_of(owned_element)
                ) in model.attributes_of(element):
                    model.set_attribute(new_region, owned_element_name, owned_element)
                else:
                    model.add_owned_element_to(new_region, owned_element)
        elif regions:
            model.set_attribute(element, "regions", model.collection(*regions))

        # else:
        #     model.set_attribute(element, "region", model.collection())

    def create_transition_path(self, transition: type["core.Transition"]):
        """
        Generates and returns a transition path object based on the provided transition.
        This method analyzes the provided transition object to determine the path of
        state entries and exits required for a state machine transition. This is done
        by examining the `source`, `target`, and `kind` attributes of the `transition`
        object. Depending on the kind of transition (external, local, or self), it
        assembles two lists representing the states to be entered ('enter') and the
        states to be left ('leave'). The method then uses these lists to create a new
        transition path object with 'enter' and 'leave' as its attributes.

        Args:
            transition (core.Transition):
                 The transition object whose path needs
                to be created.

        Returns:

        """
        enter = []
        leave = []
        # TODO this can be reduced
        if transition.kind == core.TransitionKind.external:
            leave.append(transition.source)
            for ancestor in model.ancestors_of(transition.source):
                if model.id_of(ancestor) == model.id_of(transition.container):
                    break
                if model.element.is_subtype(ancestor, core.State):
                    leave.append(ancestor)
            for ancestor in model.ancestors_of(transition.target):
                if model.id_of(ancestor) == model.id_of(transition.container):
                    break
                if model.element.is_subtype(ancestor, core.State):
                    enter.insert(0, ancestor)
            enter.append(transition.target)
        elif transition.kind == core.TransitionKind.local:
            for ancestor in model.ancestors_of(transition.target):
                if model.id_of(ancestor) == model.id_of(transition.source):
                    break
                if model.element.is_subtype(ancestor, core.State):
                    enter.append(ancestor)
            enter.append(transition.target)
        elif transition.kind == core.TransitionKind.self:
            leave.append(transition.source)
            enter.append(transition.target)
        return model.element.new(
            "path",
            bases=(core.TransitionPath,),
            enter=model.collection(*enter),
            leave=model.collection(*leave),
        )

    def preprocess_final_state(self, element: type["core.FinalState"]):
        """
        Processes a final state element within the state machine before compilation.
        This method is responsible for applying preprocessing steps to the given final state element
        within the context of the state machine. It is designed to be overridden in subclasses for
        specific behaviors. The default implementation delegates the preprocessing to the
        `preprocess_vertex` method.

        Args:
            element (type['core.FinalState']):
                 The final state element of the state machine to preprocess.

        Returns:

        """
        self.preprocess_vertex(element)

    def preprocess_transition(self, element: type["core.Transition"]):
        """
        Preprocesses the transition element to ensure it has all the necessary attributes set up correctly.
        This method processes a given transition element by setting up default values and verifying its
        correctness within a state machine. It checks if the transition source is defined, and if not,
        it attempts to derive the source based on hierarchy and ownership rules. It handles the completion
        events for states, initializes an empty effect if none is provided, and determines the transition
        kind based on the relationship between the source and target.

        Args:
            element (type['core.Transition']):
                 The transition element to preprocess.

        Raises:
            ValueError:
                 If the transition source is not found or if the transition has no container.
                This function does not return any value but modifies the transition element in place.

        """
        if element.source is None:
            owner = model.owner_of(element)
            if model.element.is_subtype(owner, model.Collection):
                owner = model.owner_of(owner)
            if not model.element.is_subtype(owner, core.Vertex):
                raise ValueError(
                    f"transition {model.qualified_name_of(element)} has no source and is not owned by a state"
                )
            # transition source always defaults to the parent
            model.set_attribute(element, "source", owner)

        # yield from self.wait_for_completion_of(element.source)
        self.preprocess_element(element.source)
        if element.events is None:
            if model.element.is_subtype(element.source, core.State):
                completion = element.source.completion
                if completion is None:
                    completion = model.element.new(
                        "completion",
                        (core.CompletionEvent,),
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
                model.element.new(
                    "effect",
                    (core.Behavior,),
                    activity=no_async_activity
                    if model.of(element).concurrency_kind
                    is core.ConcurrencyKind.asynchronous
                    else no_activity,
                ),
            )
        container = element.source.container
        if element.source == element.target:
            element.kind = core.TransitionKind.self
        elif element.target is None:
            element.kind = core.TransitionKind.internal
        elif model.is_descendant_of(element.source, element.target):
            element.kind = core.TransitionKind.local
        else:
            self.preprocess_element(element.target)
            element.kind = core.TransitionKind.external
            container = least_common_ancestor(element.source, element.target)
        if container is None:
            raise ValueError(
                f"transition {model.qualified_name_of(element)} has no container"
            )
        model.set_attribute(element, "container", container)
        path = self.create_transition_path(element)
        model.set_attribute(element, "path", path)

    def preprocess_region(self, element: type["core.Region"]):
        """
        Processes the given UML region by setting attributes and filtering sub-elements.
        This method takes an element of type 'core.Region' and performs preprocessing to set attributes
        related to its subvertices, initial state, parent state, and parent state machine. It identifies
        all the subvertices of the region that are of type 'core.Vertex' and sets the 'subvertex' attribute.
        If the region does not have an explicit initial state, this method will attempt to find one based on
        the provided filtering criteria. Once an initial state is identified or confirmed, the method sets
        the 'initial' attribute of the element.
        The method also discerns and sets attributes for the region's parent state and state machine,
        ensuring that each is appropriately classified as either a 'core.State' or 'StateMachine'.

        Args:
            element (type['core.Region']):
                 The region of a state machine to preprocess.

        Raises:
            AttributeError:
                 If the attributes related to 'subvertex', 'initial', 'state', or
                'state_machine' cannot be set due to incorrect typing or hierarchy of the provided element.

        Returns:

        """
        from stateforward.core import StateMachine

        def initial_filter(vertex):
            """
            Determines whether a given vertex is a subtype of core.Initial.

            Args:
                vertex (Any):
                     The vertex to be checked for being a subtype.

            Returns:
                bool:
                     True if the vertex is a subtype of core.Initial, otherwise False.

            """
            return model.element.is_subtype(vertex, core.Initial)

        model.set_attribute(
            element,
            "subvertex",
            model.collection(
                *model.find_owned_elements_of(
                    element,
                    lambda owned_element: model.element.is_subtype(
                        owned_element, core.Vertex
                    ),
                )
            ),
        )
        initial = getattr(element, "initial", None)

        if initial is None:
            initial = model.find_owned_element_of(element, initial_filter)
            model.set_attribute(element, "initial", initial)
        else:
            self.log.debug(
                f"region {model.qualified_name_of(element)} has initial {model.qualified_name_of(initial)}"
            )
        parent = model.owner_of(element)
        if not model.element.is_subtype(parent, (StateMachine, core.State)):
            parent = model.owner_of(parent)
        model.set_attribute(
            element,
            "state",
            parent if model.element.is_subtype(parent, core.State) else None,
        )
        model.set_attribute(
            element,
            "state_machine",
            parent if model.element.is_subtype(parent, StateMachine) else None,
        )

    def preprocess_processor(self, element: type["model.Interpreter"]):
        """
        Preprocesses an interpreter element to set up queue characteristics based on concurrency type.
        This method examines the concurrency_kind attribute of the provided interpreter element and sets an attribute to use an asynchronous queue if the concurrency kind matches asynchronous operation.

        Args:
            element (type['model.Interpreter']):
                 The interpreter element to preprocess, it must be an instance or subclass of model.Interpreter. The element is expected to have a model property with a concurrency_kind attribute.

        Raises:
            AttributeError:
                 If the 'model' property or 'concurrency_kind' attribute is missing from the element.

        """
        concurrency_kind = element.model.concurrency_kind
        if concurrency_kind == core.ConcurrencyKind.asynchronous:
            model.set_attribute(element, "queue", AsyncQueue)

    def preprocess_call_event(self, element: type["core.CallEvent"]):
        """
        Processes the provided CallEvent by setting the appropriate __call__ attribute,
        depending on whether the operation is a coroutine function or not.
        This method decorates the given CallEvent's operation with a new __call__ method.
        If the operation is an asynchronous coroutine function, it wraps the call in an
        'async def' to handle the coroutine execution, sends an event to the model's interpreter,
        and then returns the result upon completion. If the operation is a regular function,
        it wraps the call in a 'def' and sets the result before returning.
        After processing, the CallEvent can be invoked as a callable which automatically
        handles the operation execution and result management.

        Args:
            element (type['core.CallEvent']):
                 The CallEvent instance to be preprocessed.

        Raises:
            AttributeError:
                 If the 'operation' attribute is not found in the CallEvent.

        """
        if asyncio.iscoroutinefunction(element.operation):

            async def __call__(self, *args, **kwargs):
                """
                Performs an asynchronous operation and then sends its class instance to the model's interpreter.
                This asynchronous method is a coroutine that must be awaited. It wraps an internal operation coroutine, invokes it with the supplied arguments, and then sends the current class instance to the associated interpreter, which is an attribute of the model object.

                Args:
                    *args:
                         Variable length argument list to be passed to the internal operation coroutine.
                    **kwargs:
                         Arbitrary keyword arguments to be passed to the internal operation coroutine.

                Returns:

                Raises:
                    Exception:
                         Propagates any exceptions raised by the internal operation coroutine or the model's interpreter.

                """
                value = await self.operation(*args, **kwargs)
                await self.model.interpreter.send(self.__class__())
                return value

        else:

            def __call__(self, *args, **kwargs):
                """
                Performs the operation bound to the callable object and stores the result.
                This method allows the instance to be called as a function, executing the operation method
                with the provided arguments and keyword arguments. After execution, the result is saved
                using the results attribute's set_result method.

                Args:
                    *args:
                         Variable length argument list that will be passed to the operation method.
                    **kwargs:
                         Arbitrary keyword arguments that will be passed to the operation method.

                Returns:

                """
                value = self.operation(*args, **kwargs)
                self.results.set_result(value)
                return value

        setattr(element, "__call__", __call__)

    def preprocess_change_event(self, element: type[core.ChangeEvent]):
        """
        Preprocesses a ChangeEvent object by assigning an asyncio.Condition to its 'condition' attribute.

        Args:
            element (type[core.ChangeEvent]):
                 The ChangeEvent instance that is to be preprocessed.

        Raises:
            AttributeError:
                 If 'condition' is not an attribute of the provided ChangeEvent instance.

        Note:

        """
        element.condition = asyncio.Condition

    def preprocess_behavior(self, element: type["core.Behavior"]):
        """
        Preprocesses the behavior element to set up appropriate activities and contexts.
        This method takes a behavior element and does the following:
        - Determines the type of concurrency (asynchronous or synchronous) and assigns the correct no-activity function if the activity is not provided.
        - If concurrency is asynchronous and the activity is not a coroutine function, it wraps the provided activity inside a function that can handle coroutine calling conventions.
        - Sets the 'activity' attribute of the behavior element to the processed activity function, ensuring that it has appropriate module and qualname attributes.
        - Identifies the context of the behavior by finding the ancestor element that is a subtype of core.Behavior.
        - Processes all owned elements of the behavior element.
        - Collects all events that are descendants of the behavior element and assigns them to the 'pool' attribute.
        - Sets the 'context' attribute of the behavior element to the identified context.

        Args:
            element (type['core.Behavior']):
                 The behavior element to preprocess.

        """
        concurrency_kind = model.of(element).concurrency_kind
        activity = element.activity
        if activity is None:
            if concurrency_kind == core.ConcurrencyKind.asynchronous:
                activity = no_async_activity
            else:
                activity = no_activity
        elif (
            concurrency_kind == core.ConcurrencyKind.asynchronous
            and not iscoroutinefunction(element.activity)
        ):

            def activity(self, event: "core.Event", _activity=element.activity):
                """
                Performs an activity associated with a given event.
                This function is designed to execute a specific activity that is tied to an event passed to the function. The activity to be executed is provided by the _activity argument, which defaults to `element.activity`. It calls this provided activity function, passing in the instance (`self`) and the event object.

                Args:
                    event (core.Event):
                         The event object that is associated with the activity to be performed.
                    _activity (callable, optional):
                         A callable that represents the activity to be performed when the function is called. Defaults to `element.activity` if not provided.

                Returns:

                """
                return _activity(self, event)

        activity.__module__ = model.of(element).__module__
        activity.__qualname__ = f"{model.qualified_name_of(element)}.activity"
        model.set_attribute(element, "activity", activity)
        context = model.find_ancestor_of(
            element,
            lambda ancestor: model.element.is_subtype(ancestor, core.Behavior),
        )
        self.preprocess_owned_elements(element)

        events = []
        for descendant in model.descendants_of(element):
            if model.element.is_subtype(descendant, core.Event):
                events.append(descendant)
        model.set_attribute(element, "pool", model.collection(*events))
        model.set_attribute(
            element,
            "context",
            context,
        )

    def preprocess_state_machine(self, element: type["core.Behavior"]):
        """
        Preprocesses a state machine behavior object prior to compilation.
        This method takes an element which is an instance of a specific state machine behavior and performs preprocessing steps on it. These steps involve preprocessing any composite states within the element and the behavior itself. This is essential to prepare the element for subsequent compilation or transformation processes. It involves logging the preprocessing step, ensuring internal consistency, setting up necessary ordering, and potentially more based on the implementation details.
        The function concludes by sorting a collection within the state machine. The sorting criteria is based on the type of event; it prioritizes non-completion events over completion events. This ordering may affect how events are processed or triggered within the state machine behavior at runtime.

        Args:
            element (core.Behavior):
                 The state machine behavior to preprocess. This is expected to be a subtype of 'core.Behavior'.

        Returns:
            None:
                 This method performs operations on the 'element' object but does not return any value.

        """
        self.log.debug(
            f"preprocessing state machine {model.qualified_name_of(element)}"
        )
        if element.submachine_state is not None:
            return self.preprocess_state(element.submachine_state)
        self.preprocess_composite_state(element)
        self.preprocess_behavior(element)
        model.sort_collection(
            element.pool,
            lambda event: not model.element.is_subtype(event, core.CompletionEvent),
        )
