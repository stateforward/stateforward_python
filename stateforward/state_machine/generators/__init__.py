"""

Provides the `PlantUMLGenerator` class for generating PlantUML diagrams from a given model.

This module contains the `PlantUMLGenerator` class defined to work with models conforming
 to UML-like structures. It is designed to traverse a model using the Visitor pattern, rendering
 elements of the model as PlantUML statements in a generated text file suitable for creating
 visual UML diagrams.

The `PlantUMLGenerator` class is initialized with optional parameters to specify the diagram
 direction (default is `'LR'` for left-to-right) and background color (default is black `'#000000'`).

Once instantiated, the generator can be used to process different elements of a state machine model,
 including states, transitions, composite states, pseudostates, and more. Each element visited
 will contribute to the overall structure of the PlantUML diagram.

The generator primarily functions through its `visit_*` methods tailored for different model
 elements. These methods build up the PlantUML syntax by appending to an internal `Cursor` object.
 The `generate` method finalizes the diagram by appending the `@enduml` tag and then returns the
 complete PlantUML syntax as a string.

To use it, simply import the `PlantUMLGenerator` class from this module and pass it a model
 to generate the corresponding PlantUML diagram.
"""
from .plantuml.plantuml_generator import PlantUMLGenerator
