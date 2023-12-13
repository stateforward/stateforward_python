"""
# Element Overview

The [Element](/modeling/element) is the foundational class for all StateForward elements. It provides essential functionality for creating a tree structure and managing relationships.

In contrast to the `ast` module, the Element and its associated elements are classes rather than objects. This design choice is based on several reasons:

1. The tree is constructed only once at the initiation of the Python process and remains static thereafter. This results in a one-time overhead, which becomes significant when we examine the `Model` element.
2. Elements can be customized through standard inheritance and polymorphism. This feature enables the development of unique elements that can enhance the capabilities of the `Element` class.
3. Elements are instantiated in the same manner as any other Python object.


## Definition
!!! example "Element Definition"
    === "Code"
        ```python
        import stateforward as sf
        from typing import Union


        class FamilyTreeElement(sf.Element):
            def __new__(cls, *args, **kwargs):
                print(f"{cls.qualified_name}.__new__")
                return super().__new__(cls, *args, **kwargs)

            def __init__(self, *args, **kwargs):
                print(f"{self.qualified_name}.__init__")
                super().__init__(*args, **kwargs)


        class Person(FamilyTreeElement):
            first_name: str
            age: int
            kids: Union[FamilyTreeElement, sf.Collection[FamilyTreeElement]] = None


        class FamilyTree(FamilyTreeElement):
            pass


        class Family(FamilyTree):
            class Dad(Person, first_name="John", age=40):
                pass

            class Mom(Person, first_name="Jane", age=38):
                class Son(Person, first_name="Jack", age=15):
                    pass

                class Daughter(Person, first_name="Jill", age=26):
                    class Grandson(Person, first_name="Jimmy", age=1):
                        pass

                class SonInLaw(Person, first_name="John", age=26):
                    pass


        sf.dump(Family)
        ```
    === "Output"
        ```bash
        0 -> Family type[FamilyTree] @ 0x105882730
         1 -> Family.Dad type[Person] @ 0x10587feb0
         1 -> Family.Mom type[Person] @ 0x105882070
          2 -> Family.Mom.Son type[Person] @ 0x105880570
          2 -> Family.Mom.Daughter type[Person] @ 0x1058812f0
           3 -> Family.Mom.Daughter.Grandson type[Person] @ 0x105880c30
          2 -> Family.Mom.SonInLaw type[Person] @ 0x1058819b0
        ```

        The leading numbers in the output denote the hierarchical level of each element within the tree structure, which aids in deciphering the connections among elements.
        Even upon instantiation, this hierarchical format is preserved.


## Instantiating
!!! example "Element Instantiation"
    === "Code"
        ```python
        my_family = Family()
        sf.dump(my_family)
        print(my_family.Dad)
        ```
    === "Output"
        ```bash
        Family.__new__
        Family.Dad.__new__
        Family.Mom.__new__
        Family.Mom.Son.__new__
        Family.Mom.Daughter.__new__
        Family.Mom.Daughter.Grandson.__new__
        Family.Mom.SonInLaw.__new__
        Family.Mom.__init__
        Family.Mom.SonInLaw.__init__
        Family.Mom.Daughter.__init__
        Family.Mom.Daughter.Grandson.__init__
        Family.Mom.Son.__init__
        Family.Dad.__init__
        Family.__init__
        0 -> Family object[FamilyTree] @ 0x1011ea59
         1 -> Family.Dad object[Person] @ 0x101a7cb9
         1 -> Family.Mom object[Person] @ 0x101a7cc9
          2 -> Family.Mom.Son object[Person] @ 0x101a7cdd
          2 -> Family.Mom.Daughter object[Person] @ 0x101a7ced
           3 -> Family.Mom.Daughter.Grandson object[Person] @ 0x101a7d05
          2 -> Family.Mom.SonInLaw object[Person] @ 0x101a7d11
        <__main__.Family.Dad object at 0x101a7cb9>
        ```
Print statements were added to `__new__` and `__init__` to demonstrate the order of instantiation and initialization of a tree of Elements.
This is done intentionally to ensure that all elements are instantiated before any of them are initialized making them safe to access or references inside the `__init__` method.
Additionally the owned elements that are declared in `Family` become object attributes of the `Family` instance. As you can see in the printed `my_family.Dad` statement output.

---
# Association Overview

An `Association` represents a relationship to an element that is already under ownership elsewhere in the object hierarchy. It acts as a reference that enables access to these elements without directly owning them, maintaining a clear structure of ownership and dependencies.

In Python, an `Association` is a specialized wrapper around `weakref.proxy`, which allows the referred objects to be accessible as long as they exist, without affecting their lifetime by creating strong reference counts that would prevent garbage collection.

For example, in the `Family` tree structure mentioned earlier, if the `Grandson` needs to be associated with both `Daughter` and `SonInLaw`, rather than duplicating the `Grandson` object or directly sharing ownership, an `Association` can be created from `SonInLaw` to the pre-existing `Grandson` element. This setup symbolizes the relationship without taking full ownership, thus keeping the `Grandson` within the sole ownership tree of `Daughter` but still accessible from `SonInLaw` through this lightweight relationship.

By utilizing an `Association`, you ensure the system's relational integrity without being entangled in complex webs of ownership that might lead to memory leaks or logical inconsistencies.

## Definition

!!! example "Association Usage"
    === "Code"
        ```python
        # ... same as above
                class SonInLaw(Person, first_name="John", age=26, kids=Daughter.Grandson):
                    pass


        sf.dump(Family)
        ```
    === "Output"
        ```bash
        0 -> Family type[FamilyTree] @ 0x106f0ab10
         1 -> Family.Dad type[Person] @ 0x106f08290
         1 -> Family.Mom type[Person] @ 0x106f0a450
          2 -> Family.Mom.Son type[Person] @ 0x106f08950
          2 -> Family.Mom.Daughter type[Person] @ 0x106f096d0
           3 -> Family.Mom.Daughter.Grandson type[Person] @ 0x106f09010
          2 -> Family.Mom.SonInLaw type[Person] @ 0x106f09d90
           3 -> Family.Mom.SonInLaw.kids type[Association<Family.Mom.Daughter.Grandson>] @ 0x106f09010
        ```

Inspecting the output reveals that `SonInLaw.kids` has been established as an `Association` pointing to `Daughter.Grandson`. It is noteworthy that this association references the grandson using the very same memory location, underscoring that it does not constitute a separate instance but a different access path to the same object.

## Instantiating

Now, let's proceed to create another instance of the family tree to observe the effects of these relationships in practice.
!!! example "Element With Associations"
    === "Code"
        ```python
        my_family = Family()
        sf.dump(my_family)
        ```
    === "Output"
        ```bash
        Family.__new__
        Family.Dad.__new__
        Family.Mom.__new__
        Family.Mom.Son.__new__
        Family.Mom.Daughter.__new__
        Family.Mom.Daughter.Grandson.__new__
        Family.Mom.SonInLaw.__new__
        Family.Mom.__init__
        Family.Mom.SonInLaw.__init__
        Family.Mom.Daughter.__init__
        Family.Mom.Daughter.Grandson.__init__
        Family.Mom.Son.__init__
        Family.Dad.__init__
        Family.__init__
        0 -> Family object[FamilyTree] @ 0x1010d245
         1 -> Family.Dad object[Person] @ 0x1010d899
         1 -> Family.Mom object[Person] @ 0x1010d8b9
          2 -> Family.Mom.Son object[Person] @ 0x1010d8d1
          2 -> Family.Mom.Daughter object[Person] @ 0x1010d8e1
           3 -> Family.Mom.Daughter.Grandson object[Person] @ 0x1010d8f9
          2 -> Family.Mom.SonInLaw object[Person] @ 0x1010d905
           3 -> Family.Mom.SonInLaw.kids object[Association<Family.Mom.Daughter.Grandson>] @ 0x1010d8f9
        ```
Upon observation, we can discern that the `Association` has maintained its link to the same `Grandson` instance, as indicated by the identical memory address.

Additionally, the output highlights that the `Grandson` element is initialized only once, even though it's included in the family tree twice—once directly within `Daughter` and once as an associated reference in `SonInLaw`. It demonstrates the efficiency of `Associations` in managing relationships without redundant initializations, thus providing a single source of truth for shared objects within complex structures.

---
# Collection Overview

A `Collection` is a fixed container designed to hold elements, which can be either directly owned entities or associations to other elements. Elements within a `Collection` are automatically mapped or instantiated at the time the `Collection` itself is instantiated, making the container's content predictable and consistent.


## Definition

The following modification to the family tree example introduces a `GrandDaughter` under the `Mom.Daughter` class. Additionally, the `SonInLaw` class now includes a `Collection` named `kids` to hold both the `Grandson` and the `Granddaughter`.

!!! example "Collection Example"
    === "Code"
        ```python
        # ... same as the original
                class Daughter(Person, first_name="Jill", age=26):
                    class Grandson(Person, first_name="Jimmy", age=1):
                        pass

                    class Granddaughter(Person, first_name="Jenny", age=3):
                        pass

                class SonInLaw(
                    Person,
                    first_name="John",
                    age=26,
                    kids=sf.collection(Daughter.Grandson, Daughter.Granddaughter),
                ):
                    pass


        sf.dump(Family)
        ```
    === "Output"
        In this scenario, the `SonInLaw` class reflects that `John` has two children: `Grandson` and `Granddaughter`. These children are grouped together using the `sf.collection()` method, signifying that `John`'s `kids` attribute is an immutable set of his children. When the `Family` instance is created, this `Collection` ensures that the `Grandson` and `Granddaughter` are both tied into the family structure within the context of the `SonInLaw` class.
        ```bash
        0 -> Family type[FamilyTree] @ 0x120eb8a40
         1 -> Family.Dad type[Person] @ 0x120eb5440
         1 -> Family.Mom type[Person] @ 0x120eb8380
          2 -> Family.Mom.Son type[Person] @ 0x120eb5b00
          2 -> Family.Mom.Daughter type[Person] @ 0x120eb6f40
           3 -> Family.Mom.Daughter.Grandson type[Person] @ 0x120eb61c0
           3 -> Family.Mom.Daughter.Granddaughter type[Person] @ 0x120eb6880
          2 -> Family.Mom.SonInLaw type[Person] @ 0x120eb7cc0
           3 -> Family.Mom.SonInLaw.kids type[Collection] @ 0x120eb7600
            4 -> Family.Mom.SonInLaw.kids.0 type[Association<Family.Mom.Daughter.Grandson>] @ 0x120eb61c0
            4 -> Family.Mom.SonInLaw.kids.1 type[Association<Family.Mom.Daughter.Granddaughter>] @ 0x120eb6880
        ```
You can discern from this output that the `kids` attribute of the `SonInLaw` instance is now a `Collection`. Within this `Collection`, there are `Associations` to the `Grandson` and `Granddaughter`. Crucially, these associations preserve the original memory addresses of the grandchildren, as they should, confirming the `Collection` utilizes direct associations to existing instances rather than creating duplicate objects.

The output enumerates and maintains the hierarchical integrity and precise order of elements, as exhibited by the four-level deep printout where `SonInLaw.kids` consists of indexes (`.0` and `.1`) signifying individual positions within the `Collection`. This ensures each child's relational context within the family is clear and traceable.

## Instantiating
instantiating the family again.
!!! example "Collection Instantiation"
    === "Code"
        ```python
        my_family = Family()
        sf.dump(my_family)
        print(my_family.Mom.SonInLaw.kids[0])
        ```
    === "Output"
        ```bash
        Family.__new__
        Family.Dad.__new__
        Family.Mom.__new__
        Family.Mom.Son.__new__
        Family.Mom.Daughter.__new__
        Family.Mom.Daughter.Grandson.__new__
        Family.Mom.Daughter.Granddaughter.__new__
        Family.Mom.SonInLaw.__new__
        Family.Mom.__init__
        Family.Mom.SonInLaw.__init__
        Family.Mom.Daughter.__init__
        Family.Mom.Daughter.Granddaughter.__init__
        Family.Mom.Daughter.Grandson.__init__
        Family.Mom.Son.__init__
        Family.Dad.__init__
        Family.__init__
        0 -> Family object[FamilyTree] @ 0x102eaf7d
         1 -> Family.Dad object[Person] @ 0x103f14e9
         1 -> Family.Mom object[Person] @ 0x103f14f9
          2 -> Family.Mom.Son object[Person] @ 0x103f1511
          2 -> Family.Mom.Daughter object[Person] @ 0x103f1521
           3 -> Family.Mom.Daughter.Grandson object[Person] @ 0x103f153d
           3 -> Family.Mom.Daughter.Granddaughter object[Person] @ 0x103f154d
          2 -> Family.Mom.SonInLaw object[Person] @ 0x103f1559
           3 -> Family.Mom.SonInLaw.kids object[Collection] @ 0x103f155d
            4 -> Family.Mom.SonInLaw.kids.0 object[Association<Family.Mom.Daughter.Grandson>] @ 0x103f153d
            4 -> Family.Mom.SonInLaw.kids.1 object[Association<Family.Mom.Daughter.Granddaughter>] @ 0x103f154d
        <__main__.Family.Mom.Daughter.Grandson object at 0x103f153d>
        ```

Just as anticipated from our previous discussion, the `Collection` within `SonInLaw.kids` endures as a reference to the `Grandson` and `Granddaughter`. It's worth observing that these associations are now presented as `objects` instead of `types`, reflecting the instantiated state of the elements. In this context, "instantiated state" suggests that instead of merely referring to the class blueprints (types), we're now handling actual, constructed instances of these elements, as represented by their memory addresses.

Moreover, the `Grandson` and `Granddaughter` are both initialized just once, despite being referenced mutiple times within the family tree, affirming the intelligent management of object creation and relationships through `Associations` and `Collections` in this family tree representation.

# Model Overview

The `Model` class is an enhancement of the `Element` that includes additional features for preprocessing, validation, and interpretation, providing a structured way to represent complex entities within a system. Each `Element` nested within a `Model` is provided with a `model` attribute, granting a reference to the root `Model` instance, which allows elements to be aware of their context within the larger entity.

## Definition
!!! example "Model Definition"
    === "Code"
        ```python
        import stateforward as sf

        class Automobile(sf.Model):
            manufacturer: str = None
            wheels: sf.Collection["Wheel"]
            engine: "Engine"

        class Wheel(sf.Element):
            size: int

        class Engine(sf.Element):
            power: int

        class Car(
            Automobile,
            manufacturer="Saturn",
        ):
            class V8(Engine, power=300):
                pass

            class FrontLeft(Wheel, size=16):
                pass

            class FrontRight(Wheel, size=16):
                pass

            class RearLeft(Wheel, size=16):
                pass

            class RearRight(Wheel, size=16):
                pass

        sf.dump(Car)
        print(Car.V8.model)
        ```
    === "Output"
        ```bash
        0 -> Car type[Automobile] @ 0x11861f820
         1 -> Car.V8 type[Engine] @ 0x11861d660
         1 -> Car.FrontLeft type[Wheel] @ 0x11861dd20
         1 -> Car.FrontRight type[Wheel] @ 0x11861e3e0
         1 -> Car.RearLeft type[Wheel] @ 0x11861eaa0
         1 -> Car.RearRight type[Wheel] @ 0x11861f160
        <class '__main__.Car'>
        ```
The output shows the structure of the `Car` as a `Model`, which is a concrete representation of an `Automobile`. The nested classes like `V8` and the individual wheels are displayed as `Element` types that are part of the `Car` model. It also exhibits that the `V8` class within `Car` understands it is part of the `Car` model via the `model` attribute.

The `Automobile` model specifies that `manufacturer`, `wheels`, and an `engine` are essential components. In the context of the example, it means that a valid `Car` must have these attributes defined. However, it's important to note that the presence and correctness of these parts are not automatically checked by the `Model` or `Element` classes — a dedicated `Validator` would be required to ensure that the `Car` model adheres to the defined rules and structure of an `Automobile`.

---
## Validation

The `Model` class facilitates the use of a validator which is executed once the `Model` is fully constructed. The validation occurs only once at runtime, after the entire model is built, ensuring that the instance complies with the predefined rules and requirements.

### Definition

Below is an excerpt showing the incorporation of an `AutomobileValidator` for an `Automobile` `Model`. The validator checks for the presence of essential components like `engine` and `wheels`.

!!! example "Model Validation"
    === "Code"
        ```python
        # ... the rest of the example above

        class AutomobileValidator(sf.Validator):
            def validate_automobile(self, automobile: type["Automobile"]):
                if automobile.engine is None:
                    raise ValueError(f"Automobile {automobile.name} must have an engine")
                elif automobile.wheels is None:
                    raise ValueError(f"Automobile {automobile.name} must have wheels")

        class Automobile(sf.Model, validator=AutomobileValidator()):
        # ... the rest of the example
        ```
    === "Output"
        ```bash
        Traceback (most recent call last):
          File "car_model_example.py", line 26, in <module>
            class Car(
          File "model.py", line 33, in __init_subclass__
            cls.validator.validate(cls)
          File "validator.py", line 35, in validate
            self.validate_element(element)
          File "validator.py", line 26, in validate_element
            method(element.type)
          File "car_model_example.py", line 7, in validate_automobile
            raise ValueError(f"Automobile {automobile.name} must have an engine")
        ValueError: Automobile Car must have an engine
        ```

In this case, the validator indicates that the `Car` class or its derivatives must include both an `engine` and `wheels` to be considered valid. However, explicitly specifying these components for every car class can be cumbersome.

To address this, we can introduce preprocessors to the `Model`. Preprocessors can simplify the code by automatically inferring or setting default values for properties like `engine` and `wheels`, reducing verbosity and making the model definitions more efficient and less error-prone.

---
## Preprocessing

Preprocessors are executed as part of the `Model` construction process, taking place after the entire `Model` has been built but ahead of the validation phase. They are useful for setting up or modifying `Model` attributes based on a specific logic before the model is validated for correctness.

### Definition

This extension of the earlier example incorporates a `Preprocessor` for the `Automobile` `Model`, which dynamically assigns the `wheels` and `engine` attributes by inspecting the elements present in the model.

!!! example "Model Preprocessing"
    === "Code"
        ```python
        # ... continuation from the Automobile validation example

        # Define a Preprocessor class specific to the Automobile model
        class AutomobilePreprocessor(sf.Preprocessor):
            def preprocess_automobile(self, element: type["Automobile"]):
                sf.set_attribute(
                    element,
                    "wheels",
                    sf.collection(
                        *sf.find_owned_elements(
                            element, lambda _element: sf.is_subtype(_element, Wheel)
                        )
                    ),
                )
                sf.set_attribute(
                    element,
                    "engine",
                    sf.find_owned_element(
                        element, lambda _element: sf.is_subtype(_element, Engine)
                    ),
                )

        # Update the Automobile Model to leverage the Preprocessor and Validator
        class Automobile(
            sf.Model, validator=AutomobileValidator(), preprocessor=AutomobilePreprocessor()
        ):
        # ... the remaining code for the Automobile model etc.
        ```
    === "Output"
        ```bash
        0 -> Car type[Automobile] @ 0x11d616af0
         1 -> Car.V8 type[Engine] @ 0x11d614930
         1 -> Car.FrontLeft type[Wheel] @ 0x11d614ff0
         1 -> Car.FrontRight type[Wheel] @ 0x11d6156b0
         1 -> Car.RearLeft type[Wheel] @ 0x11d615d70
         1 -> Car.RearRight type[Wheel] @ 0x11d616430
         1 -> Car.wheels type[Collection] @ 0x11d6171b0
          2 -> Car.wheels.0 type[Association<Car.FrontLeft>] @ 0x11d614ff0
          2 -> Car.wheels.1 type[Association<Car.FrontRight>] @ 0x11d6156b0
          2 -> Car.wheels.2 type[Association<Car.RearLeft>] @ 0x11d615d70
          2 -> Car.wheels.3 type[Association<Car.RearRight>] @ 0x11d616430
         1 -> Car.engine type[Association<Car.V8>] @ 0x11d614930
        ```
With the preprocessor's functionality, we've streamlined the `Model` definition process, making it less verbose and more maintainable without the need to explicitly declare `wheels` and `engine` for every `Automobile` subclass. This approach allows for easier extension and customization of the model by simply including the relevant subclass elements.

---

# Validator Overview

The `Validator` in the context of the `Model` functions analogously to the `NodeVisitor` found in Python’s abstract syntax tree (`ast`) module. It follows a set path to discover the appropriate validation method for a given element within the structure.

Here’s an outline of the search logic:

1. Element names are normalized to lowercase and converted to snake_case.
2. The search attempts to find a method called `validate_{element.name}`.
3. If not found, it looks for `validate_{element.type.name}`, continuing the search up the inheritance chain until `validate_element` is found or a matching method is identified.
4. This search stops as soon as a validation method is discovered, and that method is executed.

Further, if the `Element` derives from another `Element`, the base class validation methods must be explicitly called within the identified validation method; they are not called automatically.

## Definition

In the example provided, different color elements are created along with a corresponding `Validator` class that contains specific validation methods.
!!! example "Validator Definition"
    === "Code"
        ```python
        import stateforward as sf

        # Define a Validator to handle ColorWheel and its elements
        class ColorWheelValidator(sf.Validator):
            # Validates a ColorWheel instance
            def validate_color_wheel(self, element: type["ColorWheel"]):
                print(f"validate_color_wheel({element.name})")
                # Invokes validation for each owned element within ColorWheel
                self.validate_owned_elements(element)

            # Validates an instance of Red, inheriting from Theme.Red
            def validate_red(self, element: type["Theme.Red"]):
                print("validate_red(Red)")
                # Calls validation for the Color base class with an indent
                self.validate_color(element, 2)

            # Validates an instance of Green
            def validate_green(self, element: type["Theme.Green"]):
                print("validate_green(Green)")

            # Validates any Color instance with an optional indent
            def validate_color(self, element: type["Color"], indent=0):
                print(f"{' ' * indent}validate_color({element.name})")

        # Define a generic Color Element
        class Color(sf.Element):
            pass

        # Define a ColorWheel Model, which incorporates the Validator
        class ColorWheel(sf.Model, validator=ColorWheelValidator()):
            pass

        # Define a Theme Model that inherits from ColorWheel and includes color elements
        class Theme(ColorWheel):
            class Red(Color):
                pass

            class Green(Color):
                pass

            class Blue(Color):
                pass

        # The output will demonstrate the Validator searching for and executing
        # validation rules for the Theme Model's color elements
        ```

    === "Output"
        The console output should indicate that the Validator successfully navigates through the elements, invoking the corresponding validation methods:
        ```bash
        validate_color_wheel(Theme)
        validate_red(Red)
          validate_color(Red)
        validate_green(Green)
        validate_color(Blue)
        ```

In the bullet points, it is explained how each color's validation method is resolved, showcasing the Validator's logic:

1. The `Blue` color is validated using `validate_color` directly, as there is no explicit `validate_blue` method available.
2. `validate_color` is not called for the `Green` color because `validate_green` is already present and does not call `validate_color`.
3. `validate_color` is invoked for the `Red` color due to an explicit call within `validate_red`.
4. `validate_owned_elements` is used in the `ColorWheel` validator, ensuring that all owned elements (`Red`, `Green`, and `Blue`) get validated. This step is vital because element validation would not occur without it.

By defining and structuring the Validator and validation methods correctly, developers can enforce specific validation rules tailored to their `Model` structure and ensure that all elements comply with the defined criteria.

---

# Preprocessor Overview

The preprocessor in the `stateforward` library operates identically to the `Validator`, with the key difference being the timing of its invocation. It is called before the validation phase, which allows it to modify or augment the `Model` structure prior to any checks for correctness. The primary role of the `Preprocessor` is to streamline the model construction process, adding convenience and reducing code verbosity, thus enhancing the clarity and maintainability of the model definitions.

The `Preprocessor` follows a search pattern similar to the `Validator` to determine the appropriate processing method for a given element:

1. Element names are converted to lowercase and snake_case for standardization.
2. It seeks a method with the signature `preprocess_{element.name}`.
3. Failing that, it looks for `preprocess_{element.type.name}`, proceeding recursively up the inheritance hierarchy until either `preprocess_element` is found or a suitable method is located.
4. Once a preprocessing method is identified, the search concludes and that method is executed.

Should an `Element` inherit from another `Element`, base preprocessing functions are not automatically invoked. They must be explicitly called within the identified preprocessing method.

While the preprocessor can perform a wide range of tasks, common uses include auto-filling attributes with default values, organizing collections of elements, and setting up links or associations between parts of the model. This enables developers to define elegant and concise models that automatically adjust to include necessary attributes or sub-elements, thus freeing them from repetitive boilerplate code.

The `Preprocessor` is a powerful tool within the `stateforward` library that aids in simplifying complex model preparation while ensuring a solid foundation for subsequent validation steps.
# Interpreter Overview

The `Interpreter` is an abstract class responsible for executing a `Model`.

"""
from . import element
from .element import (
    Element,
    redefine,
    find_owned_elements_of,
    find_descendants_of,
    owned_elements_of,
    remove_owned_elements_from,
    remove_owned_element_from,
    attributes_of,
    associations_of,
    add_owned_element_to,
    descendants_of,
    ancestors_of,
    find_ancestor_of,
    find_owned_element_of,
    name_of,
    id_of,
    owner_of,
    qualified_name_of,
    type_of,
    find_owned_element_of,
    is_descendant_of,
    ElementType,
    set_attribute,
    new,
)
from .collection import Collection, collection, sort_collection, extend_collection
from .model import Model, dump, of
from .preprocessor import Preprocessor
from .interpreter import Interpreter, InterpreterStep
from .validator import Validator
from .association import is_association, Association, association
from .visitor import Visitor


__all__ = (
    "Element",
    "redefine",
    "find_owned_elements_of",
    "owned_elements_of",
    "find_descendants_of",
    "remove_owned_elements_from",
    "remove_owned_element_from",
    "add_owned_element_to",
    "ancestors_of",
    "find_ancestor_of",
    "find_owned_element_of",
    "set_attribute",
    "name_of",
    "id_of",
    "owner_of",
    "descendants_of",
    "qualified_name_of",
    "type_of",
    "find_owned_element_of",
    "associations_of",
    "is_descendant_of",
    "ElementType",
    "Collection",
    "collection",
    "sort_collection",
    "extend_collection",
    "Model",
    "dump",
    "of",
    "Preprocessor",
    "Interpreter",
    "InterpreterStep",
    "Validator",
    "is_association",
    "Association",
    "association",
    "Visitor",
    "element",
)
