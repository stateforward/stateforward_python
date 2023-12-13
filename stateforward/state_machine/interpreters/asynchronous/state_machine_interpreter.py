import asyncio
from stateforward import elements, model
from stateforward.state_machine.interpreters.asynchronous.behavior_interpreter import (
    AsyncBehaviorInterpreter,
)
from functools import partial
import typing

T = typing.TypeVar("T", bound=elements.StateMachine)


class AsyncStateMachineInterpreter(AsyncBehaviorInterpreter[T]):
    async def exec_event_processing(self, event: elements.elements.Event):
        # could possibly improve this with using state in reverse
        # self.log.debug(f"processing event {model.qualified_name_of(event)}")
        results = await asyncio.gather(
            *(
                self.exec_region_processing(region, event)
                for region in self.model.regions
            )
        )
        if model.InterpreterStep.complete in results:
            return model.InterpreterStep.complete
        return (
            model.InterpreterStep.deferred
            if model.InterpreterStep.deferred in results
            else model.InterpreterStep.incomplete
        )

    async def exec_region_processing(
        self, region: elements.elements.Region, event: elements.elements.Event
    ):
        # self.log.debug(f"processing region {model.qualified_name_of(region)}")
        if not self.is_active(region):
            return model.InterpreterStep.incomplete
        active_state = next(
            (state for state in region.subvertex if self.is_active(state)), None
        )
        if active_state is None:
            return model.InterpreterStep.incomplete
        return await self.exec_state_processing(active_state, event)

    async def exec_state_processing(
        self, state: elements.elements.State, event: elements.elements.Event
    ):
        # self.log.debug(f"processing state {model.qualified_name_of(state)}")
        if not self.is_active(state):
            return model.InterpreterStep.incomplete
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
                    if result is not model.InterpreterStep.incomplete
                ),
                model.InterpreterStep.incomplete,
            )
        else:
            result = model.InterpreterStep.incomplete
        if result is model.InterpreterStep.incomplete:
            result = await self.exec_vertex_processing(state, event)
        return result

    async def exec_vertex_processing(
        self, vertex: elements.Vertex, event: elements.Event
    ):
        for transition in vertex.outgoing:
            if (
                await self.exec_transition_processing(transition, event)
                == model.InterpreterStep.complete
            ):
                return model.InterpreterStep.complete
        return model.InterpreterStep.incomplete

    async def exec_transition_processing(
        self, transition: elements.Transition, event: elements.Event
    ):
        if any(
            isinstance(_event, (type(event), elements.AnyEvent))
            for _event in transition.events
        ) and (
            transition.guard is None
            or await self.exec_constraint_evaluate(transition.guard, event)
        ):
            await self.exec_transition(transition, event)
            return model.InterpreterStep.complete
        return model.InterpreterStep.incomplete

        # could possibly improve this with using state in reverse

    async def exec_constraint_evaluate_condition(
        self, constraint: elements.Constraint, event: elements.Event
    ) -> bool:
        result = constraint.condition(event)
        if asyncio.isfuture(result) or asyncio.iscoroutine(result):
            result = await result
        self.log.debug(
            f"done evaluating constraint {model.qualified_name_of(constraint)} results are {result}"
        )
        return result

    async def exec_constraint_evaluate(
        self, constraint: elements.Constraint, event: elements.Event
    ) -> bool:
        self.log.debug(
            f"evaluating constraint {model.qualified_name_of(constraint)} for event {model.qualified_name_of(event)}"
        )
        return await self.exec_constraint_evaluate_condition(constraint, event)

    async def exec_transition(
        self, transition: elements.Transition, event: elements.Event = None
    ):
        self.log.debug(f"executing transition {model.qualified_name_of(transition)}")
        await asyncio.gather(
            *(self.exec_vertex_exit(vertex, event) for vertex in transition.path.leave)
        )
        if transition.effect is not None:
            self.exec_behavior(transition.effect, event)
            await self.pop(transition.effect)
        return await asyncio.gather(
            *(
                self.exec_vertex_entry(
                    vertex,
                    event,
                    elements.EntryKind.default
                    if index == transition.path.enter.length - 1
                    else elements.EntryKind.explicit,
                )
                for index, vertex in enumerate(transition.path.enter)
            )
        )

    async def exec_vertex_exit(self, vertex: elements.Vertex, event: elements.Event):
        if isinstance(vertex, elements.State):
            await asyncio.gather(
                *(
                    self.exec_transition_exit(transition)
                    for transition in vertex.outgoing
                )
            )
            await self.exec_state_exit(vertex, event)
        else:
            await self.exec_pseudostate_exit(
                typing.cast(elements.Pseudostate, vertex), event
            )
        self.pop(vertex)

    async def exec_transition_exit(self, transition: elements.Transition):
        for element in (*transition.events, transition.events, transition):
            if element in self.stack:
                self.pop(element)

    async def exec_vertex_entry(
        self, vertex: elements.Vertex, event: elements.Event, kind: elements.EntryKind
    ):
        self.log.debug(f"entering vertex {model.qualified_name_of(vertex)}")
        self.push(vertex)
        if isinstance(vertex, elements.State):
            await self.exec_state_entry(vertex, event, kind)
            results = await asyncio.gather(
                *(
                    self.exec_transition_entry(transition)
                    for transition in vertex.outgoing
                )
            )

        elif isinstance(vertex, elements.FinalState):
            results = await self.exec_final_state_entry(vertex, event)
        else:
            results = await self.exec_pseudostate_entry(
                typing.cast(elements.Pseudostate, vertex), event
            )
        return results

    async def exec_final_state_entry(
        self, final_state: elements.FinalState, event: elements.Event
    ):
        await self.terminate()

    async def exec_event_exit(self, event: elements.Event):
        self.pop(event)

    async def exec_change_event_wait(self, event: elements.ChangeEvent):
        while True:
            if event.expr(event):
                await self.send(event.__class__())
                break
            await asyncio.sleep(0)

    def exec_change_event_entry(self, event: elements.ChangeEvent):
        return asyncio.create_task(
            self.exec_change_event_wait(event), name=model.qualified_name_of(event)
        )

    async def exec_time_event_wait(self, event: elements.TimeEvent):
        await asyncio.sleep(event.when.total_seconds())
        await self.send(event.__class__())

    def exec_time_event_entry(self, event: elements.TimeEvent):
        return asyncio.create_task(
            self.exec_time_event_wait(event), name=model.qualified_name_of(event)
        )

    async def exec_completion_event_wait(self, event: elements.CompletionEvent):
        source: elements.State = model.owner_of(event)
        await self.stack.get(source)
        activities = tuple(
            self.stack.get(typing.cast(elements.State, state).do_activity)
            for state in self.stack
            if model.element.is_subtype(state, elements.State)
            and model.element.is_descendant_of(source, state)
        )
        await asyncio.gather(*activities)
        self.push(event, asyncio.Future())

    def exec_completion_event_entry(self, event: elements.CompletionEvent):
        qualified_name = model.qualified_name_of(event)
        self.log.debug(f"entering completion event {qualified_name}")
        task = asyncio.create_task(
            self.exec_completion_event_wait(event), name=qualified_name
        )
        return task

    async def exec_call_event_wait(self, event: elements.CallEvent):
        await event.results
        self.push(event)

    def exec_call_event_entry(self, event: elements.CallEvent):
        qualified_name = model.qualified_name_of(event)
        return asyncio.create_task(
            self.exec_call_event_wait(event), name=qualified_name
        )

    def exec_event_entry(self, event: elements.Event):
        qualified_name = model.qualified_name_of(event)
        self.log.debug(f"entering event {qualified_name}")
        if isinstance(event, elements.TimeEvent):
            return self.exec_time_event_entry(event)

        elif isinstance(event, elements.CompletionEvent):
            return self.exec_completion_event_entry(event)

        # elif isinstance(event, elements.CallEvent):
        #     return self.exec_call_event_entry(event)

        elif isinstance(event, elements.ChangeEvent):
            return self.exec_change_event_entry(event)

    async def exec_transition_entry(self, transition: elements.Transition):
        qualified_name = model.qualified_name_of(transition)
        self.log.debug(f"entering transition {qualified_name}")
        self.push(transition)
        tasks = []
        for event in transition.events:
            task = self.exec_event_entry(event)
            if task is not None:
                tasks.append(task)

        self.push(
            transition.events,
            asyncio.create_task(
                asyncio.wait_for(asyncio.gather(*tasks), None),
                name=model.qualified_name_of(transition.events),
            ),
        )

    async def exec_state_entry(
        self, state: elements.State, event: elements.Event, kind: elements.EntryKind
    ):
        qualified_name = model.qualified_name_of(state)
        self.log.debug(f"entering state {qualified_name}")
        if state.entry is not None:
            self.exec_behavior(state.entry, event)
            await self.pop(state.entry)
        if state.do_activity is not None:
            self.exec_behavior(state.do_activity, event)
        if state.submachine is not None:
            return
            # await self.enter_state_machine(state.submachine, event, kind)
        # else:
        await asyncio.gather(
            *(
                self.exec_region_entry(region, event, kind)
                for region in state.regions or []
            )
        )

    async def exec_state_machine_entry(
        self,
        state_machine: "elements.StateMachine",
        event: typing.Optional[elements.Event],
        kind: elements.EntryKind,
    ):
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
        self, region: elements.Region, event: elements.Event, kind: elements.EntryKind
    ):
        qualified_name = model.qualified_name_of(region)
        self.log.debug(f"entering region {qualified_name}")
        states = ()
        if kind == elements.EntryKind.default:
            if region.initial is None:
                return states
            self.push(region)
            return await self.exec_pseudostate_entry(region.initial, event)
        self.push(region)
        return states

    async def exec_region_exit(self, region: elements.Region, event: elements.Event):
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
        self, psuedostate: elements.Pseudostate, event: elements.Event
    ):
        pass

    async def exec_state_exit(self, state: elements.State, event: elements.Event):
        qualified_name = model.qualified_name_of(state)
        self.log.debug(f'leaving state "{qualified_name}"')
        if state.submachine is not None:
            await self.exec_state_machine_exit(state.submachine, event)
        else:
            await asyncio.gather(
                *(
                    self.exec_region_exit(region, event)
                    for region in state.regions or []
                )
            )
        if state.do_activity is not None:
            do_activity = self.pop(state.do_activity)
            if not do_activity.done():
                do_activity.cancel()
        if state.exit is not None:
            await self.exec_behavior(state.exit, event)

    async def exec_state_machine_exit(
        self,
        state_machine: "elements.StateMachine",
        event: typing.Optional[elements.Event],
    ):
        self.log.debug(
            f'leaving state machine "{model.qualified_name_of(state_machine)}"'
        )
        await asyncio.gather(
            *(self.exec_region_exit(region, event) for region in state_machine.regions)
        )

    async def exec_pseudostate_entry(
        self, pseudostate: elements.Pseudostate, event: elements.Event
    ):
        self.log.debug(
            f"entering {pseudostate.kind.value} psuedostate {model.qualified_name_of(pseudostate)}"
        )
        self.push(pseudostate)
        if pseudostate.kind == elements.PseudostateKind.initial:
            return await self.exec_transition(pseudostate.outgoing[0], event)
        elif pseudostate.kind == elements.PseudostateKind.choice:
            for transition in pseudostate.outgoing:
                if await self.exec_constraint_evaluate(transition.guard, event):
                    return await self.exec_transition(transition, event)
            raise Exception("no valid transition this should never throw")
        elif pseudostate.kind == elements.PseudostateKind.join:
            if all(
                transition.source not in self.stack
                for transition in pseudostate.incoming
            ):
                return await self.exec_transition(pseudostate.outgoing[0], event)
        elif pseudostate.kind == elements.PseudostateKind.fork:
            return await asyncio.gather(
                *(
                    self.exec_transition(transition, event)
                    for transition in pseudostate.outgoing
                )
            )

    async def run(self):
        self.log.debug(f'running state machine "{model.qualified_name_of(self.model)}"')
        await self.exec_state_machine_entry(
            self.model, None, elements.EntryKind.default
        )
        return await super().run()

    async def terminate(self):
        await self.exec_state_machine_exit(self.model, None)
        await super().terminate()
