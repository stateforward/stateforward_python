from stateforward import model
from stateforward import elements
from stateforward.state_machine.log import create_logger
from typing import Type, TypeVar
import inspect
from stateforward.state_machine.generators.cursor import Cursor

T = TypeVar("T")

logger = create_logger("plantuml")


class PlantUMLStyle:
    pass


class PlantUMLGenerator(model.Visitor):
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

    def visit_state_machine(
        self, state_machine: Type["elements.StateMachine"], cursor: Cursor
    ):
        cursor.append(
            f'state "{model.name_of(state_machine)}" as {self.qualified_name(state_machine)} {{\n',
        )
        self.visit_composite_state(state_machine, cursor=cursor)
        for element in model.all_owned_elements_of(state_machine):
            if model.element.is_subtype(
                element, elements.Transition
            ) and not model.element.is_subtype(element.source, elements.Pseudostate):
                events = ""
                if element.events:
                    events = "|".join(event.name for event in element.events.elements())
                cursor.append(
                    f"{self.qualified_name(element.source)} --> {self.qualified_name(element.target)}: {events}\n"
                )
        return True

    def visit_composite_state(
        self,
        composite_state: Type["elements.CompositeState"],
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

    def qualified_name(self, element: Type[model.Element]):
        return element.qualified_name.replace(".", "_")

    def visit_region(self, region: Type["elements.Region"], cursor: Cursor):
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

    def visit_state(self, state: type["elements.State"], cursor: Cursor):
        name = (
            state.name
            if not state.submachine
            else f"{state.name}<{state.submachine.name}>"
        )
        cursor.append(
            f'state "{name}" as {self.qualified_name(state)} {{\n',
        )
        return self.visit_composite_state(state, cursor=cursor)

    def visit_vertex(self, vertex: Type["elements.Vertex"], cursor: Cursor):
        if model.model.is_subtype(vertex, elements.Pseudostate):
            return self.visit_pseudostate(vertex, cursor)
        return self.visit_state(vertex, cursor)

    def visit_constraint(self, constraint: Type["elements.Constraint"], cursor: Cursor):
        doc = inspect.getdoc(constraint.condition)
        cursor.append(f": [{doc or constraint.condition.__name__}]")
        return True

    def visit_transition(self, transition: Type["elements.Transition"], cursor: Cursor):
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

    def visit_pseudostate(
        self, pseudostate: Type["elements.Pseudostate"], cursor: Cursor
    ):
        if pseudostate.kind is elements.PseudostateKind.initial:
            transition = tuple(pseudostate.outgoing.elements())[0]
            cursor.append(f"[*] --> {self.qualified_name(transition.target)}\n")
        elif pseudostate.kind is elements.PseudostateKind.choice:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<choice>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is elements.PseudostateKind.fork:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<fork>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is elements.PseudostateKind.entry_point:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<entryPoint>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is elements.PseudostateKind.exit_point:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<exitPoint>>\n'
            )

        elif pseudostate.kind is elements.PseudostateKind.join:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<join>>\n'
            )
            self.visit_transition(tuple(pseudostate.outgoing.elements())[0], cursor)
        return True

    def generate(self, model: type[model.Model]) -> str:
        self.visit_element(model, self.cursor)
        self.cursor.append("@enduml\n")
        print(str(self.cursor))
        return str(self.cursor)
