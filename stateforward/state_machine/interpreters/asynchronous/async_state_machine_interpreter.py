"""

The `async_state_machine_interpreter` module provides an asynchronous interpreter for state machines, capable of handling concurrent state transitions and events within the framework provided by `stateforward`. It is designed to work with the state machines structured according to the core classes and interfaces from the `stateforward` library.

The main class in this module is `AsyncStateMachineInterpreter`, which is an asynchronous interpreter that extends `AsyncBehaviorInterpreter`. It manages the asynchronous execution of states, transitions, regions, events, and the associated guard conditions and actions defined on a state machine.

Key Functionalities:
- **Event Processing**: Processes events concurrently across different regions of the state machine, handling transitions and state changes.

- **Activity Execution**: Manages execution of entry, do, and exit activities associated with states.

- **Transition Handling**: Performs transition checks and guards evaluation, executes the effects of transitions, as well as entry and exit actions.

- **State Management**: Handles the entry and exit of states, including composite states, and manages sub-states and regions.

- **Event Management**: Handles the scheduling and management of time events, change events, and completion events.

- **Termination**: Provides a mechanism to terminate the state machine execution.

Architecture Summary:
This module includes a collection of coroutine functions designed to asynchronously execute the different components of a state machine. It uses `asyncio` to manage asynchronous tasks and employs the `gather` function to handle concurrency. The interpreters maintain the current state of the machine and execute all states and transitions based on the events received. Error handling is implemented to ensure proper management of invalid transitions and other exceptions.
"""
import asyncio
from stateforward import core, model
from stateforward.protocols.interpreter import InterpreterStep
from stateforward.state_machine.interpreters.asynchronous.async_behavior_interpreter import (
    AsyncBehaviorInterpreter,
)
import typing

T = typing.TypeVar("T", bound=core.StateMachine)


class AsyncStateMachineInterpreter(AsyncBehaviorInterpreter[T]):
    """
    An asynchronous interpreter for state machine behavior execution.
    This interpreter asynchronously processes events and manages state transitions within a state machine based on a provided model. It handles concurrent entry and exit actions for regions, states, sub-states, and pseudostates, as well as the evaluation and execution of various event kinds such as time events and change events.

    Attributes:
        model (StateMachine):
             The state machine model to interpret.
        log (Logger):
             Logger for debug messages.
        stack (dict):
             A tracking structure for the active states and ongoing tasks in the state machine.

    Methods:
        exec_event_processing:
             Processes an individual event for all regions in the state machine.
        exec_region_processing:
             Processes an event for a specific region within the state machine.
        exec_state_processing:
             Processes an event for a specific state within the state machine.
        exec_vertex_processing:
             Processes an event for a specific vertex within the state machine.
        exec_transition_processing:
             Evaluates and, if conditions are met, executes a transition for an event.
        exec_constraint_evaluate:
             Evaluates a guard constraint with respect to an event.
        exec_transition:
             Executes the actions associated with taking a transition, including exit and entry actions where appropriate.
        exec_vertex_exit:
             Manages the exit actions and clean-up upon leaving a vertex in the state machine.
        exec_vertex_entry:
             Manages the entry actions and setup when entering a vertex in the state machine.
        exec_region_entry/exit:
             Handles the entry/exit logic for a region within the state machine.
        exec_state_entry/exit:
             Manages the entry and exit logic of a state, including executing any associated entry, exit, or activity actions.
        exec_state_machine_entry/exit:
             Handles the logic for entering and leaving the entire state machine or a sub-state machine.
        exec_pseudostate_entry/exit:
             Manages the logic for entering and exiting a pseudostate, based on the pseudostate kind.
        exec_event_entry:
             Wraps the starting of the async event processing in a Task and logs entry.
        run:
             Initiates the state machine execution by entering the state machine and processing steps.
        terminate:
             Handles the orderly shutdown of the state machine, exiting all active regions and states.
            This interpreter extends AsyncBehaviorInterpreter, making it capable of dealing with the asynchronous nature of the systems modelled by the state machine.

    """

    async def exec_event_processing(self, event: core.elements.Event):
        """
        Asynchronously processes an event across all regions within a model.
        This method takes a single event and concurrently processes it through all regions defined in the model. It uses asyncio.gather to asynchronously execute region processing for each region. After all regions have processed the event, the method determines the overall processing result based on the outcomes of the regional processing. The method returns an instance of InterpreterStep to indicate whether event processing is complete, deferred, or incomplete.

        Args:
            event (core.elements.Event):
                 The event to be processed by the state machine.

        Returns:
            (InterpreterStep):
                 An enum value indicating the completion state of the event processing. It can either be InterpreterStep.complete if the processing is finished across all regions, InterpreterStep.deferred if at least one region deferred the event, or InterpreterStep.incomplete if all regions are incomplete in processing the event.

        """
        results = await asyncio.gather(
            *(
                self.exec_region_processing(region, event)
                for region in self.model.regions
            )
        )
        if InterpreterStep.complete in results:
            return InterpreterStep.complete
        return (
            InterpreterStep.deferred
            if InterpreterStep.deferred in results
            else InterpreterStep.incomplete
        )

    async def exec_region_processing(
        self, region: core.elements.Region, event: core.elements.Event
    ):
        """
        Performs the execution processing of a given region within a state machine, handling an incoming event.
        This asynchronous method checks if the region is currently active and proceeds to process the
        specified event by executing its corresponding active state. It is part of the state machine's
        execution logic which would typically be involved in the workflow of state transitions and event handling.

        Args:
            region (core.elements.Region):
                 The region of the state machine to be processed.
            event (core.elements.Event):
                 The event to be handled within the region's active state.

        Returns:
            (InterpreterStep):
                 An enumeration value representing the completion status of the region processing.
                This could either be `InterpreterStep.incomplete` indicating that the processing is not yet complete,
                due to either the region not being active or the absence of an active state within the region.

        Raises:
            TypeError:
                 If the region or event parameters are not instances of their respective expected types.

        """
        if not self.is_active(region):
            return InterpreterStep.incomplete
        active_state = next(
            (state for state in region.subvertex if self.is_active(state)), None
        )
        if active_state is None:
            return InterpreterStep.incomplete
        return await self.exec_state_processing(active_state, event)

    async def exec_state_processing(
        self, state: core.elements.State, event: core.elements.Event
    ):
        """
        Performs processing on a state within the state machine given an event.
        This function executes the processing logic associated with a given state. If the state is not active, it immediately returns an incomplete step indicator. Otherwise, it proceeds to check if the state has regions and processes them asynchronously, waiting for all to complete before continuing.
        If all regions return an incomplete processing result, or there are no regions, it attempts to process the state itself as a vertex. Finally, it returns the result of the processing, whether that be the processing of the regions or the state as a vertex.

        Args:
            state (core.elements.State):
                 The state that needs to be processed.
            event (core.elements.Event):
                 The event that may trigger state transitions or actions.

        Returns:
            (InterpreterStep):
                 The result of the state processing, which can indicate whether the processing is complete, incomplete, or has resulted in a transition.

        """
        if not self.is_active(state):
            return InterpreterStep.incomplete
        elif state.regions is not None:
            result = next(
                (
                    result
                    for result in (
                        await asyncio.gather(
                            *(
                                self.exec_region_processing(region, event)
                                for region in state.regions
                            )
                        )
                    )
                    if result is not InterpreterStep.incomplete
                ),
                InterpreterStep.incomplete,
            )
        else:
            result = InterpreterStep.incomplete
        if result is InterpreterStep.incomplete:
            result = await self.exec_vertex_processing(state, event)
        return result

    async def exec_vertex_processing(self, vertex: core.Vertex, event: core.Event):
        """
        Asynchronously processes a given vertex in the state machine with respect to an incoming event.
        This method iteratively examines all outgoing transitions from the provided vertex. It attempts to process each transition with the given event by invoking the exec_transition_processing method. The processing of transitions continues until either the processing of a transition results in a 'complete' state or all transitions have been processed without reaching a 'complete' state.

        Args:
            vertex (core.Vertex):
                 The vertex to process which contains the outgoing transitions.
            event (core.Event):
                 The event that triggered the processing of the vertex.

        Returns:
            (InterpreterStep):
                 An enum value indicating whether the processing of the vertex resulted in a 'complete' or 'incomplete' state. 'complete' is returned if any of the transitions reached completion, otherwise 'incomplete' is returned if all transitions were processed and none was completed.

        """
        for transition in vertex.outgoing:
            if (
                await self.exec_transition_processing(transition, event)
                == InterpreterStep.complete
            ):
                return InterpreterStep.complete
        return InterpreterStep.incomplete

    async def exec_transition_processing(
        self, transition: core.Transition, event: core.Event
    ):
        """
        Performs the processing of a given state transition based on an event.
        This asynchronous method checks if the specified event matches one of the expected events for the transition, and whether the transition's guard condition (if any) is satisfied. If the conditions are met, the method executes the transition and indicates that the process is complete. If the conditions are not met, the processing is incomplete.

        Args:
            transition (core.Transition):
                 The transition to be processed.
            event (core.Event):
                 The event that is triggering the transition.

        Returns:
            (InterpreterStep):
                 An enum indicating whether the transition processing is 'complete' or 'incomplete'.

        """
        if any(
            isinstance(_event, (type(event), core.AnyEvent))
            for _event in transition.events
        ) and (
            transition.guard is None
            or await self.exec_constraint_evaluate(transition.guard, event)
        ):
            await self.exec_transition(transition, event)
            return InterpreterStep.complete
        return InterpreterStep.incomplete

        # could possibly improve this with using state in reverse

    async def exec_constraint_evaluate_condition(
        self, constraint: core.Constraint, event: core.Event
    ) -> bool:
        """
        Async method to evaluate a condition of a given constraint in the context of an event.
        This function takes a constraint object and an event object. It executes the condition
        associated with the constraint by passing the event to it. If the condition function
        returns a Future or is a coroutine, the function awaits the result. Logging is performed
        after the evaluation to indicate that the evaluation is completed, including the result of the evaluation.

        Args:
            constraint (core.Constraint):
                 The constraint whose condition must be evaluated.
            event (core.Event):
                 The event which is passed to the constraint's condition for evaluation.

        Returns:
            (bool):
                 The result of the constraint's condition evaluation.

        """
        result = constraint.condition(event)
        if asyncio.isfuture(result) or asyncio.iscoroutine(result):
            result = await result
        self.log.debug(
            f"done evaluating constraint {model.qualified_name_of(constraint)} results are {result}"
        )
        return result

    async def exec_constraint_evaluate(
        self, constraint: core.Constraint, event: core.Event
    ) -> bool:
        """
        Evaluates a given constraint in the context of a specific event asynchronously.
        This function logs the evaluation process, indicates that it is evaluating a particular constraint for a specified event, and then proceeds to evaluate the condition associated with the constraint.

        Args:
            constraint (core.Constraint):
                 The constraint object that needs to be evaluated.
            event (core.Event):
                 The event object that will be used in the context of the constraint evaluation.

        Returns:
            (bool):
                 A boolean value indicating the result of the constraint evaluation.

        """
        self.log.debug(
            f"evaluating constraint {model.qualified_name_of(constraint)} for event {model.qualified_name_of(event)}"
        )
        return await self.exec_constraint_evaluate_condition(constraint, event)

    async def exec_transition(
        self, transition: core.Transition, event: core.Event = None
    ):
        """
        Performs the execution of a given transition within a state machine.
        This coroutine executes the actions associated with leaving the current state vertices, executing transition's effect if any, and entering the target state vertices. It logs the process of executing each transition for debugging purposes.

        Args:
            transition (core.Transition):
                 The transition to be executed.
            event (core.Event, optional):
                 The event that may have triggered the transition. Defaults to None.

        """
        self.log.debug(f"executing transition {model.qualified_name_of(transition)}")
        for vertex in transition.path.leave:
            await self.exec_vertex_exit(vertex, event)
        if transition.effect is not None:
            await self.exec_behavior(transition.effect, event)
        for index, vertex in enumerate(transition.path.enter):
            await self.exec_vertex_entry(
                vertex,
                event,
                core.EntryKind.default
                if index == transition.path.enter.length - 1
                else core.EntryKind.explicit,
            )

    async def exec_vertex_exit(self, vertex: core.Vertex, event: core.Event):
        """
        Asynchronously executes the exit behavior for a given vertex in a state machine.
        This coroutine checks if the provided vertex is an instance of `core.State` or any other type. If the vertex is a `core.State`, it performs two main tasks, executed concurrently for efficiency: it calls `exec_transition_exit` for all outgoing transitions, followed by `exec_state_exit` for the state itself. For other types of vertices, identified here as `core.Pseudostate`, it calls `exec_pseudostate_exit`. After executing the appropriate exit behavior, it then removes the vertex from consideration within the current flow by calling the `pop` method.

        Args:
            vertex (core.Vertex):
                 The vertex that is exiting and requires the execution of its exit behavior.
            event (core.Event):
                 The event that triggered the vertex's exit.

        """
        if isinstance(vertex, core.State):
            await asyncio.gather(
                *(
                    self.exec_transition_exit(transition)
                    for transition in vertex.outgoing
                )
            )
            await self.exec_state_exit(vertex, event)
        else:
            await self.exec_pseudostate_exit(
                typing.cast(core.Pseudostate, vertex), event
            )
        self.pop(vertex)

    async def exec_transition_exit(self, transition: core.Transition):
        """
        Asynchronously executes the exit logic for a given state machine transition.
        This method is responsible for handling the exit process when a state machine transition occurs. It iterates over both events associated with the transition and the transition itself, and for each element, it checks whether the element exists in the state machine's stack. If any element is found within the stack, the method will asynchronously pop the element from the stack.

        Args:
            transition (core.Transition):
                 The transition object that is undergoing the exit process.

        Raises:
            Any exceptions that could occur while popping elements from the stack are implicitly raised and not caught within this function.

        """
        for element in (*transition.events, transition.events, transition):
            if element in self.stack:
                self.pop(element)

    async def exec_vertex_entry(
        self, vertex: core.Vertex, event: core.Event, kind: core.EntryKind
    ):
        """
        Executes entry logic for a given vertex within a state machine.
        This asynchronous method handles the entry logic for different vertex types present in a state machine. Depending on the type of the vertex (core.State, core.FinalState, or core.Pseudostate), it will perform the appropriate entry actions and execute any outgoing transitions related to that vertex. It also manages the vertex stack by pushing the current vertex into it before proceeding with the entry actions.

        Args:
            vertex (core.Vertex):
                 The vertex at which to start executing the entry logic.
            event (core.Event):
                 The event instance that triggered the state transition.
            kind (core.EntryKind):
                 The kind of entry action to be performed. This helps determine how deep the entry logic should go; for instance, it could specify entering only the top state or recursive entry to all substates.

        Returns:
            (List[object]):
                 A list of results from execution of entry logic and transitions originating from the vertex. The content of this list can vary depending on the type of vertex and number of transitions.

        Raises:
            TypeError:
                 If the provided vertex is not castable to one of the expected vertex types (core.State, core.FinalState, or core.Pseudostate).

        """
        self.push(vertex)
        if isinstance(vertex, core.State):
            await self.exec_state_entry(vertex, event, kind)
            results = await asyncio.gather(
                *(
                    self.exec_transition_entry(transition)
                    for transition in vertex.outgoing
                )
            )

        elif isinstance(vertex, core.FinalState):
            results = await self.exec_final_state_entry(vertex, event)
        else:
            results = await self.exec_pseudostate_entry(
                typing.cast(core.Pseudostate, vertex), event
            )
        return results

    async def exec_final_state_entry(
        self, final_state: core.FinalState, event: core.Event
    ):
        """
        Asynchronously executes the entry actions for a final state of a state machine.
        This method handles the actions that should be taken when entering the final state of
        a state machine or a specific region within the state machine. It ensures that all exit
        actions are completed for the regions that are being left behind. Additionally, if
        the state machine associated with the final state's container has no active regions
        left on the stack, it also terminates the super state (inferred to be a higher level state machine).

        Args:
            final_state (core.FinalState):
                 The final state object representing the state machine's
                final state or a specific region's final state to which the state machine is
                transitioning.
            event (core.Event):
                 The event that triggered the transition to the final state.

        """
        await self.exec_region_exit(final_state.container, event)

        if final_state.container.state_machine is not None and all(
            region not in self.stack
            for region in final_state.container.state_machine.regions
        ):
            super().terminate()

    async def exec_event_exit(self, event: core.Event):
        """
        A coroutine that handles the exit event for the current state in the state machine.
        This coroutine pops an event from the state context, effectively facilitating a transition
        from the current state by handling the exit logic associated with that state.

        Args:
            event (core.Event):
                 The event that triggers the exit operation from the current state.

        """
        self.pop(event)

    async def exec_change_event_wait(self, event: core.ChangeEvent):
        """
        Performs an asynchronous wait for a change event to meet a certain condition before sending the event class associated with the event.
        This function enters an infinite loop that continuously checks if the condition specified by the `expr` attribute of the `event` argument is met. If the condition evaluates to `True`, the function sends an instance of the event's class using the `send` coroutine and then breaks out of the loop. Otherwise, it awaits asynchronously for a very brief time (`0` seconds) before checking the condition again, allowing other asynchronous operations to proceed in the meantime.

        Args:
            event (core.ChangeEvent):
                 The change event instance containing the condition expression to be evaluated and the event class to be sent once the condition is met.

        Raises:
            This function does not explicitly raise any exceptions, but exceptions may be raised by the `expr` evaluation or the `send` coroutine.

        Returns:
            (None):
                 This function does not return a value.

        """
        while True:
            if event.expr(event):
                await self.send(event.__class__())
                break
            await asyncio.sleep(0)

    def exec_change_event_entry(self, event: core.ChangeEvent) -> asyncio.Task:
        """
        Schedules the execution of an `exec_change_event_wait` coroutine for a given change event.
        This function creates an asyncio Task to asynchronously wait for a change event to be processed. It assigns a unique name to the task based on the qualified name of the event.

        Args:
            event (core.ChangeEvent):
                 The change event to be processed asynchronously.

        Returns:
            (asyncio.Task):
                 The asyncio Task object created for the change event.

        """
        return asyncio.create_task(
            self.exec_change_event_wait(event), name=model.qualified_name_of(event)
        )

    async def exec_time_event_wait(self, event: core.TimeEvent) -> None:
        """
        Async function to wait for a specific time event and then send the event.
        This asynchronous method takes a time event object and performs a sleep operation for the duration specified by the `when` attribute of the time event. After the wait period is over, it sends the event.

        Args:
            event (core.TimeEvent):
                 The time event object containing the `when` attribute, which specifies the duration to wait before sending the event.

        Returns:
            None

        """
        await asyncio.sleep(event.when.total_seconds())
        await self.send(event.__class__())

    def exec_time_event_entry(self, event: core.TimeEvent):
        """
        Schedules the execution of a time-based event.
        This function initiates an asynchronous task to handle a time-event in the context of the current model's state machine.
        It uses the asyncio library to create a new task which will await the execution of the 'exec_time_event_wait' coroutine.
        The task is assigned a name that corresponds to the fully qualified name of the event, which is retrieved using the 'model.qualified_name_of' method.

        Args:
            event (core.TimeEvent):
                 An instance of a time-based event that is to be handled by the state machine.

        Returns:
            (asyncio.Task):
                 The newly created asyncio task object that is responsible for executing the time-event.

        """
        return asyncio.create_task(
            self.exec_time_event_wait(event), name=model.qualified_name_of(event)
        )

    async def exec_completion_event_wait(self, event: core.CompletionEvent):
        """
        Awaits the completion of an event within a state machine, gathering futures related to activities in descendant states.
        This asynchronous method is designed to handle the completion of a given event within the context of a state machine.
        It first retrieves the state that owns the provided event and then awaits the future associated with the activity of that state. Once the awaited future completes, its value is stored within the event's value attribute. Subsequently, the method identifies all activities associated with descendant states of the source state and collects their associated futures. It awaits the completion of all these futures concurrently using `asyncio.gather`. Finally, the event is pushed to an internal stack for further processing.

        Args:
            event (core.CompletionEvent):
                 The event for which the completion is being awaited. It is assumed to have originated from a state within the state machine.

        """
        source: core.State = model.owner_of(event)
        future = self.stack.get(source.activity)
        event.value = await future
        activities = tuple(
            self.stack.get(typing.cast(core.State, state).activity)
            for state in self.stack
            if model.element.is_subtype(state, core.State)
            and model.element.is_descendant_of(source, state)
        )
        await asyncio.gather(*activities)
        self.push(event)

    def exec_completion_event_entry(self, event: core.CompletionEvent) -> asyncio.Task:
        """
        Executes the entry logic for a completion event by creating an asyncio task to wait for the event completion.
        This method is responsible for logging the entry of the completion event, resetting the event's value to None,
        and spawning an asyncio task to await the event's completion. It returns the created task object.

        Args:
            event (core.CompletionEvent):
                 The completion event for which to execute the entry logic.

        Returns:
            (asyncio.Task):
                 The asyncio task created to wait for the event to complete.

        """
        qualified_name = model.qualified_name_of(event)
        self.log.debug(f"entering completion event {qualified_name}")
        event.value = None
        task = asyncio.create_task(
            self.exec_completion_event_wait(event), name=qualified_name
        )
        return task

    def exec_event_entry(self, event: core.Event) -> typing.Optional[asyncio.Task]:
        """
        Executes the entry logic for a given event in the state machine.
        This method dispatches the execution based on the type of event received. Depending on the type of the event,
        different execution paths are taken:
        - `core.TimeEvent`: Executes the logic specific for time-triggered events.
        - `core.CompletionEvent`: Executes the logic specific for completion-triggered events.
        - `core.ChangeEvent`: Executes the logic specific for change-triggered events.

        Args:
            event (core.Event):
                 The event that is currently being processed by the state machine.

        Returns:
            (typing.Optional[asyncio.Task]):
                 An optional asyncio Task object if the event processing
                results in an asynchronous task that needs to be awaited by the caller. None if the processing
                of the event doesn't create an asynchronous task.

        """
        qualified_name = model.qualified_name_of(event)
        self.log.debug(f"entering event {qualified_name}")
        if isinstance(event, core.TimeEvent):
            return self.exec_time_event_entry(event)

        elif isinstance(event, core.CompletionEvent):
            return self.exec_completion_event_entry(event)

        elif isinstance(event, core.ChangeEvent):
            return self.exec_change_event_entry(event)

    async def exec_transition_entry(self, transition: core.Transition) -> None:
        """
        Performs entry operations for a given state transition in an asynchronous state machine.
        This method logs the entering of a transition, then pushes the transition onto the state stack. It
        proceeds to gather tasks associated with the entry events of the transition, executes them asynchronously,
        and waits for their completion before advancing.

        Args:
            transition (core.Transition):
                 The transition object representing the state transition
                that is being entered.

        Returns:
            (None):
                 This method does not return a value and is intended to be used for its side effects.

        Raises:
            This method does not explicitly raise any exceptions, but exceptions could be raised by
            the tasks executed during transition entry, which should be handled by the calling context.

        """
        qualified_name = model.qualified_name_of(transition)
        self.log.debug(f"entering transition {qualified_name}")
        self.push(transition)
        tasks = []
        for event in transition.events:
            task = self.exec_event_entry(event)
            if task is not None:
                tasks.append(task)
        if tasks:
            self.push(
                transition.events,
                self.wait(*tasks),
            )

    async def exec_state_entry(
        self, state: core.State, event: core.Event, kind: core.EntryKind
    ):
        """
        Asynchronously executes the entry logic for the given state in a State Machine.
        This coroutine manages the transition into a state by performing several actions:
        - It logs the entry into the state.
        - Executes the 'entry' behavior for the state, if it exists.
        - Initiates and manages the state's 'activity', if it exists, by scheduling it to run asynchronously.
        - Skips further actions if the state contains a submachine (a nested State Machine).
        - Recursively invokes entry logic for each contained region within the state.

        Args:
            state (core.State):
                 The state object that is being entered.
            event (core.Event):
                 The event object that triggered the state transition.
            kind (core.EntryKind):
                 The enumeration value representing the kind of entry action to be executed.

        Returns:
            None

        """
        qualified_name = model.qualified_name_of(state)
        self.log.debug(f"entering state {qualified_name}")
        if state.entry is not None:
            await self.exec_behavior(state.entry, event)
        if state.activity is not None:
            self.push(
                state.activity,
                self.loop.create_task(self.exec_behavior(state.activity, event)),
            )
        if state.submachine is not None:
            return
        await asyncio.gather(
            *(
                self.exec_region_entry(region, event, kind)
                for region in state.regions or []
            )
        )

    async def exec_state_machine_entry(
        self,
        state_machine: "core.StateMachine",
        event: typing.Optional[core.Event],
        kind: core.EntryKind,
    ):
        """
        Asynchronously executes the entry behavior for a given state machine.
        This method is responsible for logging the entry into the state machine and
        then concurrently executing the entry behavior of all regions within the
        state machine. It uses asynchronous gathering to ensure that all regions
        start their entry behavior concurrently.

        Args:
            state_machine (core.StateMachine):
                 The state machine instance for which entry behavior needs to be executed.
            event (typing.Optional[core.Event]):
                 The event that triggered the entry into the state machine, if any.
            kind (core.EntryKind):
                 The kind of entry to be performed for the state machine.

        Returns:
            A coroutine that, when awaited, results in the concurrent execution of entry
            behavior for all regions within the state machine.

        """
        self.log.debug(
            f'entering state machine "{model.qualified_name_of(state_machine)}" with {state_machine.regions.length} regions'
        )
        return await asyncio.gather(
            *(
                self.exec_region_entry(region, event, kind)
                for region in state_machine.regions
            )
        )

    async def exec_region_entry(
        self, region: core.Region, event: core.Event, kind: core.EntryKind
    ):
        """
        Executes the entry logic for a given state machine region.
        This asynchronous method is responsible for entering a region of the state machine. Based on the
        entry kind specified, it either proceeds with the default entry logic by initiating the region's
        initial pseudostate or simply prepares for entry into the region without further action.

        Args:
            region (core.Region):
                 The region of the state machine that is being entered.
            event (core.Event):
                 The event that triggered the entry into the region.
            kind (core.EntryKind):
                 The kind of entry into the region, which determines the behavior
                on region entry. A 'default' kind leads to executing the initial pseudostate, while other kinds may
                alter this behavior.

        Returns:
            (tuple):
                 A tuple representing the states that have been entered as a result of the entry
                process. For 'default' kind with an initial pseudostate, it's the result of the pseudostate entry;
                otherwise, it's an empty tuple.

        Raises:
            Any exceptions raised by the `exec_pseudostate_entry` if 'default' kind entry is being processed
            and the region has an initial pseudostate.

        """
        qualified_name = model.qualified_name_of(region)
        self.log.debug(f"entering region {qualified_name}")
        states = ()
        if kind == core.EntryKind.default:
            if region.initial is None:
                return states
            self.push(region)
            return await self.exec_pseudostate_entry(region.initial, event)
        self.push(region)
        return states

    async def exec_region_exit(self, region: core.Region, event: core.Event):
        """
        Asynchronously exits a region within a state machine.
        This method handles the process of exiting a region by first determining the region's qualified name and logging the exit action. It then identifies the active vertex (state) of the region currently on the stack, if any. If an active vertex exists, the method ensures its proper exit sequence is executed. Finally, the region is popped from the internal state stack.
        This method is an asynchronous coroutine and should be awaited.

        Args:
            region (core.Region):
                 The region to exit from within the state machine.
            event (core.Event):
                 The event instance that triggered the exit.

        """
        qualified_name = model.qualified_name_of(region)
        self.log.debug(f'leaving region "{qualified_name}"')
        active_vertex = next(
            (vertex for vertex in region.subvertex if vertex in self.stack),
            None,
        )
        if active_vertex is not None:
            await self.exec_vertex_exit(active_vertex, event)
        self.pop(region)

    async def exec_pseudostate_exit(
        self, psuedostate: core.Pseudostate, event: core.Event
    ):
        """
        Async function to execute the exit process of a given pseudostate in response to an event.
        This function is designed to handle the exiting of a pseudostate, which is typically
        a state in a state machine that does not correspond to a condition or action in the
        traditional sense, but instead is used to represent an abstract state or a state that
        serves as a transition to other states. The function takes as input the pseudostate
        to be exited and the event that triggered the exit process.

        Args:
            psuedostate (core.Pseudostate):
                 The pseudostate object to be exited.
            event (core.Event):
                 The event object that has triggered the exit of the pseudostate.


        """
        pass

    async def exec_state_exit(self, state: core.State, event: core.Event):
        """
        Performs the exit sequence for a given state in the context of a state machine.
        This asynchronous method handles the exit behavior of a state before a transition to another state. It will go through any nested state machines or regions associated with the given state, triggering their own exit sequences. If the state has an associated activity, and it's still running, it will be canceled. Lastly, if the state has defined an exit behavior, it is executed.

        Args:
            state (core.State):
                 The state from which to exit.
            event (core.Event):
                 The event that triggered the state exit, if any.

        """
        qualified_name = model.qualified_name_of(state)
        if state.submachine is not None:
            await self.exec_state_machine_exit(state.submachine, event)
        else:
            await asyncio.gather(
                *(
                    self.exec_region_exit(region, event)
                    for region in state.regions or []
                )
            )
        if state.activity is not None:
            activity = self.pop(state.activity)
            if not activity.done():
                activity.cancel()
        if state.exit is not None:
            await self.exec_behavior(state.exit, event)
        self.log.debug(f'leaving state "{qualified_name}"')

    async def exec_state_machine_exit(
        self,
        state_machine: "core.StateMachine",
        event: typing.Optional[core.Event],
    ):
        """
        Asynchronously leaves the state machine and executes the cleanup for each region within it.
        This method is responsible for triggering the exit process from a given state machine and ensuring
        that each of the regions within the state machine has its exit process executed. It logs the
        activity and utilizes asynchronous gathering to handle the exiting of multiple regions concurrently.

        Args:
            state_machine (core.StateMachine):
                 The state machine instance that is being exited.
            event (typing.Optional[core.Event]):
                 An optional event that might have triggered the state machine exit.
                This parameter may be None, indicating that no specific event is associated with the exit action.

        """
        self.log.debug(
            f'leaving state machine "{model.qualified_name_of(state_machine)}"'
        )
        await asyncio.gather(
            *(self.exec_region_exit(region, event) for region in state_machine.regions)
        )

    async def exec_pseudostate_entry(
        self, pseudostate: core.Pseudostate, event: core.Event
    ):
        """
        Executes the entry behavior of a pseudostate based on its kind.
        This asynchronous method processes the entry of a pseudostate and performs
        actions based on its type (e.g., initial, choice, join, fork). It logs the entry,
        determines the proper transition(s) based on the pseudostate kind and the given
        event, and asynchronously executes the appropriate transition(s).

        Args:
            pseudostate (core.Pseudostate):
                 The pseudostate that is being entered.
            event (core.Event):
                 The event that triggered the entry into the pseudostate.

        Raises:
            Exception:
                 If the pseudostate is of kind 'choice' and no valid transition can be
                determined (i.e., no transition guard is satisfied), an Exception is
                raised indicating a model error.

        Returns:
            An awaitable object that, when awaited, yields the result of the executed
            transition(s). Depending on the pseudostate kind, this could be the result from
            a single transition or a collection of results from multiple transitions (in
            the case of a 'fork' pseudostate).

        """
        self.log.debug(
            f"entering {pseudostate.kind.value} psuedostate {model.qualified_name_of(pseudostate)}"
        )
        if pseudostate.kind == core.PseudostateKind.initial:
            return await self.exec_transition(pseudostate.outgoing[0], event)
        elif pseudostate.kind == core.PseudostateKind.choice:
            for transition in pseudostate.outgoing:
                if transition.guard is None or await self.exec_constraint_evaluate(
                    transition.guard, event
                ):
                    return await self.exec_transition(transition, event)
            raise Exception("no valid transition this should never throw")
        elif pseudostate.kind == core.PseudostateKind.join:
            if all(
                transition.source not in self.stack
                for transition in pseudostate.incoming
            ):
                return await self.exec_transition(pseudostate.outgoing[0], event)
        elif pseudostate.kind == core.PseudostateKind.fork:
            return await asyncio.gather(
                *(
                    self.exec_transition(transition, event)
                    for transition in pseudostate.outgoing
                )
            )

    async def run(self):
        """
        Async function to start and manage the execution of the state machine.
        This method initiates the run process of the state machine by logging its execution and handling
        its entry operations. It proceeds to call the `step` method to perform the state machine's
        transitions. If an `asyncio.CancelledError` occurs, it logs that the state machine is stopping.
        In the absence of exceptions, it delegates to the superclass's `run` method to continue the
        running process.

        Raises:
            asyncio.CancelledError:
                 If the asynchronous task that called `run` is cancelled.

        """
        self.log.debug(f'running state machine "{model.qualified_name_of(self.model)}"')
        await self.exec_state_machine_entry(self.model, None, core.EntryKind.default)
        try:
            await self.step()
        except asyncio.CancelledError:
            self.log.debug(
                f'stopping state machine "{model.qualified_name_of(self.model)}"'
            )
            return
        return await super().run()

    async def terminate(self):
        """
        Asynchronously terminates the current object's operations by executing the state machine exit process and then calling the terminate method of the superclass.
        This method performs two main actions in sequence. First, it calls 'exec_state_machine_exit' with the current model instance and 'None' as arguments to properly exit any state the object might be in. After that, it awaits the termination method of the superclass to ensure any additional superclass-specific termination procedures are carried out.

        Args:
            None

        Returns:
            (None):
                 This method does not return any value. Its purpose is to perform an asynchronous cleanup.

        Raises:
            Any exception raised by 'exec_state_machine_exit' or the superclass termination method will propagate upwards, potentially to the invoker of this method.

        """
        await self.exec_state_machine_exit(self.model, None)
        await super().terminate()
