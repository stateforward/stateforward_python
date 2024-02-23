"""

The `plantuml_generator` module is part of the `stateforward` package and is responsible for generating PlantUML diagrams that visualize state machines defined using the `stateforward` framework. This module includes a `PlantUMLGenerator` class that traverses the elements of a state machine model and compiles them into a PlantUML representation. It relies heavily on the visitor design pattern to process various elements such as states, transitions, regions, and pseudostates.

## Classes and Methods:

- `PlantUMLStyle`: A placeholder class that presumably would hold styling configurations for UML diagrams but currently lacks implementation details.

- `PlantUMLGenerator`: A class inheriting from `model.Visitor` designed to generate UML diagrams.
  - `__init__(self, direction: str='LR', background_color: str='#000000')`: Initializes the generator with a specified direction for layout and a background color.
  - `visit_state_machine`: Processes the top-level state machine element.
  - `visit_composite_state`: Handles composite states within the state machine.
  - `visit_region`: Processes regions which can contain multiple sub-states or vertices. 
  - `visit_state`: Handles the generation of UML representation for states.
  - `visit_vertex`: Directs the processing of vertices to either a standard state or a pseudostate handler based on its type.
  - `visit_constraint`: Processes constraints associated with transitions.
  - `visit_transition`: Handles the transitions between states including events and guards.
  - `visit_pseudostate`: Manages pseudostates such as initial, fork, join, entry point, exit point, and choice, which are special state types in UML state diagrams.
  - `generate`: Orchestrates the entire rendering process of the state machine model to a PlantUML diagram format.

## Helper Objects and Variables:

- `Cursor`: A utility class used for keeping track of the current position while appending lines to the PlantUML diagram.
- `logger`: A preconfigured logger for the module, utilizing the `create_logger` function from `stateforward.state_machine.log`.
- `T = TypeVar('T')`: A generic type variable used in type annotations within the module.

## Usage:

The module is designed for internal use within the `stateforward` framework and should be invoked by other components of the framework needing to visualize state machine structures as PlantUML diagrams. Developers can instantiate the `PlantUMLGenerator` with appropriate parameters and call the `generate` method with a state machine model to create a PlantUML depiction. The current implementation omits direct user interaction details and example code snippets to focus on the structural and functional aspects of the module.

Overall, `plantuml_generator` is a specialized module intended to work with the `stateforward` package's state machines, providing a textual UML diagram output for visualization purposes.
"""
from stateforward import model
from stateforward import core
from stateforward.state_machine.log import create_logger
from typing import Type, TypeVar
import inspect
from stateforward.state_machine.generators.cursor import Cursor

T = TypeVar("T")

logger = create_logger("plantuml")


class PlantUMLStyle:
    """
    A class dedicated to defining the styles and aesthetics for PlantUML diagrams.
    This class encapsulates all the styling choices such as colors, line styles, font types, and any other
    visual settings that can be applied to generate uniform and aesthetically pleasing PlantUML diagrams.
    The class does not contain any methods, properties, or attributes by default and serves as a template
    for extending with specific styling configurations.
    
    Attributes:
    
    Methods:
    
    Note:

    """

    pass


class PlantUMLGenerator(model.Visitor):
    """
    A class for generating PlantUML diagrams from a model of a state machine.
    The PlantUMLGenerator class is used to produce PlantUML diagrams that represent state
    machines. It leverages the visitor design pattern to traverse the model and generate
    a textual representation that can be used to create UML diagrams.
    
    Attributes:
        direction (str):
             The direction of the diagram (e.g., 'LR' for left-to-right).
        background_color (str):
             The background color of the diagram in hex format.
    
    Methods:
        __init__:
             Constructor for initializing the PlantUMLGenerator with optional direction and background color.
        visit_state_machine:
             Processes the state machine model to generate the PlantUML representation.
        visit_composite_state:
             Visits a composite state and generates its representation.
        qualified_name:
             Helper method to provide a qualified name suitable for PlantUML.
        visit_region:
             Visits a region within the state machine diagram and generates its representation.
        visit_state:
             Visits a state and generates its representation in the diagram.
        visit_vertex:
             High-level method for visiting vertices which can either be states or pseudostates.
        visit_constraint:
             Visits a constraint to include its description or name in the diagram.
        visit_transition:
             Visits a transition between states and generates its representation in the diagram.
        visit_pseudostate:
             Visits pseudostates like initial, choice, fork, entry or exit point, and join, generating their representations.
        generate:
             Finalizes the generation process by outputting the PlantUML string representation of the model.
            This class assumes all necessary types and classes it uses from the model module are available within the scope it operates in.

    """

    def __init__(self, direction: str = "LR", background_color: str = "#000000"):
        """
        Initializes a new instance with specified diagram properties.
        This constructor initializes the diagram with custom direction and background color. It sets a default cursor with a predefined UML start notation, skin parameters, and styles suitable for generating diagrams.
        
        Args:
            direction (str, optional):
                 The direction that diagram elements should be laid out. Defaults to 'LR' (left to right).
            background_color (str, optional):
                 The hexadecimal color code for the diagram's background. Defaults to '#000000' (black).

        """
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
        self, state_machine: Type["core.StateMachine"], cursor: Cursor
    ):
        """
        Visits the state machine and generates a structured description of its states and transitions.
        The function processes the state machine by appending the state machine's name to the cursor's content
        as a state block. Within this block, it recursively visits any composite states to capture their nested
        structure. The function then goes through each owned element of the state machine. If the element is a
        transition and its source is not a pseudostate, it formats the transition's details and appends them to the
        cursor.
        
        Args:
            state_machine (Type['core.StateMachine']):
                 The state machine to visit.
            cursor (Cursor):
                 A mutable sequence of strings to which the formatted description is appended.
        
        Returns:
            bool:
                 Always returns True.

        """
        cursor.append(
            f'state "{model.name_of(state_machine)}" as {self.qualified_name(state_machine)} {{\n',
        )
        self.visit_composite_state(state_machine, cursor=cursor)
        for element in model.all_owned_elements_of(state_machine):
            if model.element.is_subtype(
                element, core.Transition
            ) and not model.element.is_subtype(element.source, core.Pseudostate):
                events = ""
                if element.events:
                    events = "|".join(event.name for event in element.events.elements())
                cursor.append(
                    f"{self.qualified_name(element.source)} --> {self.qualified_name(element.target)}: {events}\n"
                )
        return True

    def visit_composite_state(
        self,
        composite_state: Type["core.CompositeState"],
        cursor: Cursor = None,
    ):
        """
        Visits a composite state in the state machine, appending its representation to the provided cursor with proper indentation.
        Traverses the regions within the given composite state, leveraging the 'auto_indent' context manager for correct indentation. If the composite state has a description, it also appends a note with the description at the top of the composite state's representation.
        
        Args:
            composite_state (Type['core.CompositeState']):
                 The composite state to visit, it should be a type from the 'core' module.
            cursor (Cursor, optional):
                 The cursor instance where the composite state's representation will be appended. If None, a new Cursor instance will be used.
        
        Returns:
            bool:
                 Returns True to indicate the visit has been successfully completed.

        """
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
        """
        Generates a modified version of an element's qualified name by replacing all the periods with underscores.
        
        Args:
            element (Type[model.Element]):
                 The element whose qualified name will be modified.
        
        Returns:
            str:
                 A string representing the qualified name of the element with periods replaced by underscores.
        
        Raises:
            AttributeError:
                 If the element does not have a `qualified_name` attribute or if it is not of type `str`.

        """
        return element.qualified_name.replace(".", "_")

    def visit_region(self, region: Type["core.Region"], cursor: Cursor):
        """
        Visits and processes a region in a StateMachine, formatting the output to show the structure and transitions of the region.
        This function takes the `region` object, which is supposed to be an instance or subclass of `core.Region`, and a `Cursor` object used for managing indentation and organization in the output. It starts by checking the length of the `subvertex` attribute of the region; if there are subvertices present, it proceeds to handle region naming and formatting. In the case where the region's name does not start with 'region_', it formats the entry point, defines a state with the region’s qualified name, and an auto-indented block is started for the subvertices. Each subvertex is visited and processed recursively. If the region name starts with 'region_', it instead visits each vertex directly without additional structuring. The function returns `True` upon completion.
        
        Args:
            region (Type['core.Region']):
                 The region to visit and process.
            cursor (Cursor):
                 A `Cursor` instance for output formatting and indentation.
        
        Returns:
            bool:
                 True if the region is successfully visited and processed.

        """
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

    def visit_state(self, state: type["core.State"], cursor: Cursor):
        """
        Visits a state in the state machine and appends its representation to the cursor.
        
        Args:
            state (core.State):
                 The state to visit. Can be either a simple state or a composite state
                with a submachine.
            cursor (Cursor):
                 The cursor where the state representation will be appended.
        
        Returns:

        """
        name = (
            state.name
            if not state.submachine
            else f"{state.name}<{state.submachine.name}>"
        )
        cursor.append(
            f'state "{name}" as {self.qualified_name(state)} {{\n',
        )
        return self.visit_composite_state(state, cursor=cursor)

    def visit_vertex(self, vertex: Type["core.Vertex"], cursor: Cursor):
        """
        Visits a vertex within the state machine and determines the action based on its type.
        This method checks if the given vertex is a subtype of a pseudostate and delegates to the appropriate visit method based on this check. If the vertex is a pseudostate, `visit_pseudostate` is called. Otherwise, `visit_state` is called.
        
        Args:
            vertex (Type['core.Vertex']):
                 The vertex to be visited, which can be a state or a pseudostate within the state machine.
            cursor (Cursor):
                 The cursor representing the current position within the state machine's transition sequence.
        
        Returns:

        """
        if model.model.is_subtype(vertex, core.Pseudostate):
            return self.visit_pseudostate(vertex, cursor)
        return self.visit_state(vertex, cursor)

    def visit_constraint(self, constraint: Type["core.Constraint"], cursor: Cursor):
        """
        Visits a constraint within the context of a cursor operation.
        This method is used to append the documentation or name of a constraint's condition to the cursor. If the constraint's condition has a docstring, it will be used; otherwise, the name of the condition method will be used.
        
        Args:
            constraint (Type['core.Constraint']):
                 The constraint object to visit. It should have a condition attribute representing the constraint logic.
            cursor (Cursor):
                 The cursor object where the documentation or name of the constraint's condition is to be appended.
        
        Returns:
            bool:
                 Returns True to indicate the visit was successful.

        """
        doc = inspect.getdoc(constraint.condition)
        cursor.append(f": [{doc or constraint.condition.__name__}]")
        return True

    def visit_transition(self, transition: Type["core.Transition"], cursor: Cursor):
        """
        Visits a transition in a state machine to generate a formatted string representation of the transition.
        This method constructs a formatted string that represents a transition in the
        state machine. The string includes the qualified names of the source and target
        states, connected by an arrow. If the transition is triggered by events, their
        names are also included, separated by a pipe '|' character. Furthermore, if a
        guard condition is associated with the transition, the `visit_constraint` method
        is called to process it. The final representation of the transition is appended
        to the cursor.
        
        Args:
            transition (Type['core.Transition']):
                 The transition to visit.
            cursor (Cursor):
                 The cursor object used to accumulate the transition strings.
        
        Returns:
            bool:
                 Always returns True to indicate successful processing of the transition.

        """
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

    def visit_pseudostate(self, pseudostate: Type["core.Pseudostate"], cursor: Cursor):
        """
        Visits a pseudostate node within a state machine and appends relevant PlantUML description to the given cursor buffer based on the pseudostate kind.
        
        Args:
            self:
                 The instance of the class.
            pseudostate (Type['core.Pseudostate']):
                 The pseudostate node to visit.
            cursor (Cursor):
                 A mutable list-like object where the generated PlantUML is incrementally being stored.
        
        Returns:
            bool:
                 Always returns True, indicating the visit was completed.
            Each pseudostate kind results in a different handling and output string formatting:
                - If it's an initial pseudostate, it creates a transition from the initial node to its target state.
                - If it's a choice pseudostate, it defines the pseudostate as a choice node and processes its outgoing transitions.
                - If it's a fork pseudostate, it defines the pseudostate as a fork node and processes its outgoing transitions.
                - If it's an entry point pseudostate, it defines the pseudostate as an entry point node and processes its outgoing transitions.
                - If it's an exit point pseudostate, it defines the pseudostate as an exit point node.
                - If it's a join pseudostate, it defines the pseudostate as a join node and processes the first outgoing transition only.

        """
        if pseudostate.kind is core.PseudostateKind.initial:
            transition = tuple(pseudostate.outgoing.elements())[0]
            cursor.append(f"[*] --> {self.qualified_name(transition.target)}\n")
        elif pseudostate.kind is core.PseudostateKind.choice:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<choice>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is core.PseudostateKind.fork:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<fork>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is core.PseudostateKind.entry_point:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<entryPoint>>\n'
            )
            for transition in pseudostate.outgoing.elements():
                self.visit_transition(transition, cursor)
        elif pseudostate.kind is core.PseudostateKind.exit_point:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<exitPoint>>\n'
            )

        elif pseudostate.kind is core.PseudostateKind.join:
            cursor.append(
                f'state "{pseudostate.name}" as  {self.qualified_name(pseudostate)} <<join>>\n'
            )
            self.visit_transition(tuple(pseudostate.outgoing.elements())[0], cursor)
        return True

    def generate(self, model: type[model.Model]) -> str:
        """
        Generates a Unified Modeling Language (UML) representation of the specified model.
        This method processes the specified model element using `visit_element` to navigate
        and collect UML-related data. After the visitation process, it appends an '@enduml' tag at the
        end of the UML diagram data collected in the `cursor`. This data is then aggregated into a
        string which represents the UML diagram for the model and returned.
        
        Args:
            model (type[model.Model]):
                 The model to generate UML for. It has to be of a type that
                subclasses `model.Model`.
        
        Returns:
            str:
                 A string representation of the UML diagram generated for the provided model.

        """
        self.visit_element(model, self.cursor)
        self.cursor.append("@enduml\n")
        print(str(self.cursor))
        return str(self.cursor)
