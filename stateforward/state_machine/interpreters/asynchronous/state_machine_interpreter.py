import asyncio
from stateforward import elements, model
from stateforward.state_machine.log import log
from stateforward.state_machine.interpreters.asynchronous.behavior_interpreter import (
    AsyncBehaviorInterpreter,
)


class AsyncStateMachineInterpreter(AsyncBehaviorInterpreter):
    """
    An asynchronous state machine interpreter responsible for processing events
    and managing state transitions within an asynchronous environment.

    The interpreter leverages Python's asyncio library to handle the execution
    of state machine behaviors, ensuring non-blocking operations.

    Attributes:
        model (StateMachine): The state machine to be interpreted.
        idle (asyncio.Event): An event to indicate if the interpreter is idle.
        tasks (dict[Element, asyncio.Future]): A mapping of elements (e.g., states) to
            their respective awaitable task objects.

    """

    model: "elements.StateMachine"

    async def process_event(self, event: elements.elements.Event):
        """
        Asynchronously handles an incoming event and determines the resultant state machine processing action.

        This method looks through the active regions and states of the state machine and attempts to process
        the event. If any transitions match the event and its associated guard conditions, those transitions
        are taken, and the state machine moves to the next appropriate state(s).

        Args:
            event (Event): The event instance to be processed by the state machine.

        Returns:
            Processing: An enumeration value indicating the result of the event processing. This value can
                        be Processing.complete if the event led to a transition, Processing.incomplete if the
                        event did not lead to a transition, or Processing.deferred if the event processing is
                        ongoing or deferred.

        Raises:
            Exception: If no valid transitions are found for a choice pseudostate. This situation
                       indicates a model error where a choice cannot make a valid decision based on the
                       guards of its outgoing transitions.
        """
        # could possibly improve this with using state in reverse
        results = await asyncio.gather(
            *(self.process_region(region, event) for region in self.model.region)
        )
        self.log.debug(
            f"processed event {event.qualified_name} with results {tuple(result.value for result in results)}"
        )
        if model.Processing.complete in results:
            return model.Processing.complete
        return model.Processing.incomplete

    async def process_region(
        self, region: elements.elements.Region, event: elements.elements.Event
    ):
        if not self.is_active(region):
            return model.Processing.incomplete
        active_state = next(
            (state for state in region.subvertex if self.is_active(state)), None
        )
        if active_state is None:
            return model.Processing.incomplete
        return await self.process_state(active_state, event)

    async def process_state(
        self, state: elements.elements.State, event: elements.elements.Event
    ):
        if not self.is_active(state):
            return model.Processing.incomplete
        result = next(
            (
                result
                for result in (
                    await asyncio.gather(
                        *(self.process_region(region, event) for region in state.region)
                    )
                )
                if result is not model.Processing.incomplete
            ),
            model.Processing.incomplete,
        )
        if result is not model.Processing.incomplete:
            return result
        return await self.process_vertex(state, event)

    async def process_vertex(self, vertex: elements.Vertex, event: elements.Event):
        for transition in vertex.outgoing:
            if (
                await self.process_transition(transition, event)
                == model.Processing.complete
            ):
                return model.Processing.complete
        return model.Processing.incomplete

    async def process_transition(
        self, transition: elements.Transition, event: elements.Event
    ):
        if any(
            isinstance(_event, (type(event), elements.AnyEvent))
            for _event in transition.events
        ) and await self.evaluate_constraint(transition.guard, event):
            await self.execute_transition(transition, event)
            return model.Processing.complete
        return model.Processing.incomplete

        # could possibly improve this with using state in reverse

    async def evaluate_constraint(
        self, constraint: elements.Constraint, event: elements.Event
    ):
        if constraint is None:
            return True
        result = constraint.condition(event)
        if asyncio.iscoroutine(result):
            result = await result
        return result

    async def leave_vertex(self, vertex: elements.Vertex, event: elements.Event):
        if isinstance(vertex, elements.State):
            await asyncio.gather(
                *(self.leave_transition(transition) for transition in vertex.outgoing)
            )
            await self.leave_state(vertex, event)
        else:
            await self.leave_psuedostate(vertex, event)
        self.remove_active(vertex)

    async def execute_transition(
        self, transition: elements.Transition, event: elements.Event = None
    ):
        await asyncio.gather(
            *(self.leave_vertex(vertex, event) for vertex in transition.path.leave)
        )
        await self.execute_behavior(transition.effect, event)
        return await asyncio.gather(
            *(
                self.enter_vertex(
                    vertex,
                    event,
                    elements.EntryKind.default
                    if index == transition.path.enter.length - 1
                    else elements.EntryKind.explicit,
                )
                for index, vertex in enumerate(transition.path.enter)
            )
        )

    async def leave_transition(self, transition: elements.Transition):
        for element in (*transition.events, transition.events, transition):
            self.remove_active(element)

    async def enter_vertex(
        self, vertex: elements.Vertex, event: elements.Event, kind: elements.EntryKind
    ):
        self.add_active(vertex)

        if isinstance(vertex, elements.State):
            await self.enter_state(vertex, event, kind)
            return await asyncio.gather(
                *(self.enter_transition(transition) for transition in vertex.outgoing)
            )

        elif isinstance(vertex, elements.FinalState):
            return await self.enter_final_state(vertex, event)
        return await self.enter_psuedostate(vertex, event)

    async def enter_final_state(self, final_state: elements.FinalState):
        await self.terminate()

    async def leave_event(self, event: elements.Event):
        self.remove_active(event)

    def enter_change_event(self, event: elements.ChangeEvent):
        async def wait(_self=self, _event=event, _condition=event.condition()):
            while True:
                if _event.expr(_event):
                    _self.dispatch(_event)
                    break
                await asyncio.sleep(0)

        return asyncio.create_task(wait(), name=event.qualified_name)

    def enter_time_event(self, event: elements.TimeEvent):
        async def wait(_self=self, _event=event):
            await asyncio.sleep(_event.when.total_seconds())
            self.add_active(event)

        return asyncio.create_task(wait(), name=event.qualified_name)

    def enter_completion_event(self, event: elements.CompletionEvent):
        async def wait(_self=self, _event=event, _source=event.owner):
            await _self.get_active(
                _source.do_activity
            )  # wait for the activity of the state to complete
            await asyncio.gather(
                *(
                    _self.get_active(active.do_activity)
                    for active in _self.active
                    if model.is_subtype(active, elements.State)
                    and active.qualified_name.startswith(_source.qualified_name)
                )
            )
            self.add_active(_event)

        return asyncio.create_task(wait(), name=event.qualified_name)

    def enter_call_event(self, event: elements.CallEvent):
        event.results = asyncio.Future()

        async def wait(_self=self, _event=event):
            await _event.results
            _self.add_active(_event)

        return asyncio.create_task(wait(), name=event.qualified_name)

    def enter_event(self, event: elements.Event):
        if isinstance(event, elements.TimeEvent):
            return self.enter_time_event(event)

        elif isinstance(event, elements.CompletionEvent):
            return self.enter_completion_event(event)

        elif isinstance(event, elements.CallEvent):
            return self.enter_call_event(event)

        elif isinstance(event, elements.ChangeEvent):
            return self.enter_change_event(event)

    async def enter_transition(self, transition: elements.Transition):
        self.add_active(transition)
        tasks = []
        for event in transition.events:
            task = self.enter_event(event)
            if task is not None:
                tasks.append(self.enter_event(event))

        self.add_active(
            transition.events,
            asyncio.create_task(
                asyncio.wait_for(asyncio.gather(*tasks), None),
                name=transition.events.qualified_name,
            ),
        )

    async def enter_state(
        self, state: elements.State, event: elements.Event, kind: elements.EntryKind
    ):
        await self.execute_behavior(state.entry, event)
        self.execute_behavior(state.do_activity, event)
        if state.submachine is not None:
            await self.enter_state_machine(state.submachine, event, kind)
        else:
            await asyncio.gather(
                *(
                    self.enter_region(region, event, kind)
                    for region in state.region or []
                )
            )

    async def enter_state_machine(
        self,
        state_machine: "elements.StateMachine",
        event: elements.Event,
        kind: elements.EntryKind,
    ):
        self.log.debug(
            f'entering state machine "{state_machine.qualified_name}" with {state_machine.region.length} regions'
        )
        return await asyncio.gather(
            *(self.enter_region(region, event, kind) for region in state_machine.region)
        )

    async def enter_region(
        self, region: elements.Region, event: elements.Event, kind: elements.EntryKind
    ):
        self.log.debug(f"entering region {region.qualified_name}")
        states = ()
        if kind == elements.EntryKind.default:
            if region.initial is None:
                return states
            self.add_active(region)
            return await self.enter_psuedostate(region.initial, event)
        self.add_active(region)
        return states

    async def leave_region(self, region: elements.Region, event: elements.Event):
        active_vertex = next(
            (vertex for vertex in region.subvertex if vertex in self.active),
            None,
        )
        if active_vertex is not None:
            await self.leave_vertex(active_vertex, event)
        self.remove_active(region)

    async def leave_psuedostate(
        self, psuedostate: elements.Pseudostate, event: elements.Event
    ):
        pass

    async def leave_state(self, state: elements.State, event: elements.Event):
        if state.submachine is not None:
            await self.leave_state_machine(state.submachine, event)
        else:
            await asyncio.gather(
                *(self.leave_region(region, event) for region in state.region or [])
            )
        self.remove_active(state.do_activity)
        await self.execute_behavior(state.exit, event)

    async def leave_state_machine(
        self, state_machine: "elements.StateMachine", event: elements.Event
    ):
        await asyncio.gather(
            *(self.leave_region(region, event) for region in state_machine.region)
        )

    async def enter_psuedostate(
        self, psuedostate: elements.Pseudostate, event: elements.Event
    ):
        if psuedostate.kind == elements.PseudostateKind.initial:
            return await self.execute_transition(psuedostate.outgoing[0], event)
        elif psuedostate.kind == elements.PseudostateKind.choice:
            for transition in psuedostate.outgoing:
                if await self.evaluate_constraint(transition.guard, event):
                    return await self.execute_transition(transition, event)
            raise Exception("no valid transition this should never throw")
        elif psuedostate.kind == elements.PseudostateKind.join:
            if all(
                transition.source not in self.active
                for transition in psuedostate.incoming
            ):
                return await self.execute_transition(psuedostate.outgoing[0], event)
        elif psuedostate.kind == elements.PseudostateKind.fork:
            return await asyncio.gather(
                *(
                    self.execute_transition(transition, event)
                    for transition in psuedostate.outgoing
                )
            )

    async def run(self, machine):
        self.log.debug(f'running state machine "{machine.name}"')
        await self.enter_state_machine(machine, None, elements.EntryKind.default)
        return await super().run(machine)

    async def terminate(self):
        await self.leave_state_machine(self.model, None)
        await super().terminate()
