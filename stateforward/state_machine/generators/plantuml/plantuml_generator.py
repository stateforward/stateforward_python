import stateforward as sf
from stateforward.state_machine.log import log
from typing import Type, TypeVar
import inspect
from stateforward.state_machine.generators.cursor import Cursor

T = TypeVar("T")

logger = log.getLogger("plantuml")


class PlantUMLStyle:
    pass


class PlantUMLGenerator(sf.model.Visitor):
    def __init__(self, direction: str = "LR", background_color: str = "#000000"):
        super().__init__()
        self.cursor = Cursor(
            """@startuml
skinparam linetype ortho
skinparam arrowColor white
skinparam backgroundColor #000000
skinparam ActivityBarColor white
<style>
circle {
    backgroundColor white
}
</style>
skinparam State {
    backgroundColor black
    FontColor white
    borderColor white
}
"""
        )
        self.direction = direction

    def visit_state_machine(self, state_machine: Type[sf.StateMachine], cursor: Cursor):
        cursor.append(
            f'state "{state_machine.name}" as {self.qualified_name(state_machine)} {{\n',
        )
        self.visit_composite_state(state_machine, cursor=cursor)
        for element in sf.all_owned_elements(state_machine):
            if sf.model.is_subtype(element, sf.Transition) and not sf.model.is_subtype(
                element.source, sf.Pseudostate
            ):
                events = ""
                if element.events:
                    events = "|".join(event.name for event in element.events.elements())
                cursor.append(
                    f"{self.qualified_name(element.source)} --> {self.qualified_name(element.target)}: {events}\n"
                )
        return True

    def visit_composite_state(
        self,
        composite_state: Type[sf.CompositeState],
        cursor: Cursor = None,
    ):
        region = composite_state.region
        with cursor.auto_indent(indent=2) as _cursor:
            regions = tuple(region.elements())
            if regions:
                for index, region in enumerate(region.elements()):
                    self.visit_region(region, _cursor)
        cursor.append("}\n")
        docs = composite_state.__doc__
        if docs is not None:
            cursor.append(
                f"note top of {self.qualified_name(composite_state)}: \"{docs.lstrip().encode('unicode_escape').decode()}\""
            )
        return True

    def qualified_name(self, element: Type[sf.Element]):
        return element.qualified_name.replace(".", "_")

    def visit_region(self, region: Type[sf.Region], cursor: Cursor):
        if region.subvertex.length:
            if not region.name.startswith("region_"):
                cursor.extend(
                    f"[*] --> {self.qualified_name(region)}\n",
                    f'state "{region.name}" as {self.qualified_name(region)} {{\n',
                )
                with cursor.auto_indent() as _cursor:
                    for index, vertex in enumerate(region.subvertex.elements()):
                        self.visit_vertex(vertex, _cursor)
                cursor.append("}\n")
            else:
                for index, vertex in enumerate(region.subvertex.elements()):
                    self.visit_vertex(vertex, cursor)

        return True

    def visit_state(self, state: type[sf.State], cursor: Cursor):
        name = (
            state.name
            if not state.submachine
            else f"{state.name}<{state.submachine.name}>"
        )
        cursor.append(
            f'state "{name}" as {self.qualified_name(state)} {{\n',
        )
        return self.visit_composite_state(state, cursor=cursor)

    def visit_vertex(self, vertex: Type[sf.Vertex], cursor: Cursor):
        if sf.model.is_subtype(vertex, sf.Pseudostate):
            return self.visit_pseudostate(vertex, cursor)
        return self.visit_state(vertex, cursor)

    def visit_constraint(self, constraint: Type[sf.Constraint], cursor: Cursor):
        doc = inspect.getdoc(constraint.condition)
        cursor.append(f": [{doc or constraint.condition.__name__}]")
        return True

    def visit_transition(self, transition: Type[sf.Transition], cursor: Cursor):
        cursor.append(
            f"{self.qualified_name(transition.source)} --> {self.qualified_name(transition.target)}"
        )
        if transition.events:
            cursor.extend(
                "|".join(event.name for event in transition.events.elements())
            )
        if transition.guard:
            self.visit_constraint(transition.guard, cursor)
        cursor.append("\n")
        return True

    def visit_pseudostate(self, pseudostate: Type[sf.Pseudostate], cursor: Cursor):
        if pseudostate.kind is sf.PseudostateKind.initial:
            transition = tuple(pseudostate.outgoing.elements())[0]
            cursor.append(f"[*] --> {self.qualified_name(transition.target)}\n")
        elif pseudostate.kind is sf.PseudostateKind.choice:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<choice>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is sf.PseudostateKind.fork:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<fork>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is sf.PseudostateKind.entry_point:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<entryPoint>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is sf.PseudostateKind.exit_point:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<exitPoint>>\n'
            )

        elif pseudostate.kind is sf.PseudostateKind.join:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<join>>\n'
            )
            self.visit_transition(tuple(pseudostate.outgoing.elements())[0], cursor)
        return True

    def generate(self, model: type[sf.Model]) -> str:
        self.visit_element(model, self.cursor)
        self.cursor.append("@enduml\n")
        print(str(self.cursor))
        return str(self.cursor)
