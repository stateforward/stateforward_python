"""

The `model` module defines the structure and behavior of a `Model` class which is an extension of the `Element` class. This module also provides utility functions to interact with model instances and to perform various operations such as model creation and instance retrieval.

## Model class
The `Model` class is an abstract base class that represents a generic model in the system. It is designed to be subclassed to create specific types of models. It includes special methods for model initialization (`__init_subclass__`) and instance creation (`__create__`). The `Model` class keeps track of all instances of itself and derived classes using a class attribute `__all_instances__`, which is a dictionary of model instances indexed by their unique identifiers.

### Class Variables
- `__all_instances__`: A dictionary that keeps track of all created model instances.
- `preprocessor`: A variable that should be assigned a `Preprocessor` class. This preprocessor is applied to the model class during subclass initialization.
- `validator`: A variable that should be assigned a `Validator` class. This validator is applied during subclass initialization for the purpose of validating the model class.
- `interpreter`: An instance of the `Interpreter` protocol that is intended to be used with the model.

### Special Methods
- `__init_subclass__`: This method is automatically called when a subclass of `Model` is created. It is responsible for running the associated preprocessor and validator, if they are provided.
- `__create__`: This protected class method creates an instance of the model and registers it in `__all_instances__`.

## Utility Functions
- `of`: A function that takes an `ElementType` and returns either the `Model` class or an instance of Model associated with that element, if one exists.
- `all_instances`: A function that returns a dictionary of all model instances tracked by `Model.__all_instances__`.
- `dump`: A function used for debugging, which prints out a representation of the model elements hierarchy. It takes an `Element` object, an optional level of indentation, and an optional associated name. The output shows the model elements' types or object instances, qualified names, and associations.

## Typing Imports
The module includes relevant imports from the `typing` module and other components from within the stateforward package that are used for type annotations. These imports also make use of conditional import statements to prevent circular dependencies when types are used for annotations only (`typing.TYPE_CHECKING`).
"""
import typing
from stateforward.model.element import (
    Element,
    ElementType,
    id_of,
    type_of,
    qualified_name_of,
    owned_elements_of,
    associations_of,
    is_redefined,
)

if typing.TYPE_CHECKING:
    from stateforward.model.preprocessor import Preprocessor
    from stateforward.protocols.interpreter import Interpreter
    from stateforward.model.validator import Validator

__all__ = (
    "Model",
    "of",
    "dump",
    "all_instances",
)


class Model(Element):
    """
    A base class for creating model elements with built-in pre-processing and validation capabilities.
    This class is designed to be subclassed for creating different types of model elements that require
    initial pre-processing and validation steps upon creation. It maintains a registry dictionary
    of all instances of its subclasses.

    Attributes:
        __all_instances__ (dict[str, 'Model']):
             A class-level dictionary mapping unique identifiers to instances of Model subclasses.
        preprocessor (typing.ClassVar[type['Preprocessor']]):
             A class attribute that should be overridden with a specific Preprocessor subclass if pre-processing is needed.
        validator (typing.ClassVar[type['Validator']]):
             A class attribute that should be overridden with a specific Validator subclass if validation is needed.
        interpreter ('Interpreter'):
             An instance attribute that can be set to an Interpreter object if needed.

    Methods:
        __init_subclass__(cls:
             type['Model'], **kwargs):
            A class method automatically called when a subclass is created. This method applies
            pre-processing and validation to the subclass using its preprocessor and validator class attributes.
        __create__(cls, **kwargs):
            A class method that is used to create instances of the subclass. It registers the instance in
            the __all_instances__ dictionary using its unique identifier and then returns the instance.
            Subclasses should define their own preprocessor and validator if specific actions should be taken during instantiation.

    """

    __all_instances__: dict[str, "Model"] = {}
    preprocessor: typing.ClassVar[type["Preprocessor"]] = None
    validator: typing.ClassVar[type["Validator"]] = None
    interpreter: "Interpreter" = None

    def __init_subclass__(
        cls: type["Model"],
        **kwargs,
    ):
        """
        Initializes the subclass of a `Model` class.
        This method is automatically invoked during the creation of a subclass of `Model`. It starts by invoking the same method in the superclass (if there is one) to ensure that any higher-level initialization occurs as usual. Following this, it checks if the subclass has defined either a `preprocessor` or a `validator`. If a `preprocessor` is defined, it creates an instance of this preprocessor and calls its `preprocess` method, passing in the subclass itself as an argument. Similarly, if a `validator` is defined, this method creates an instance of the validator and calls its `validate` method with the subclass.

        Args:
            cls (type[Model]):
                 The subclass of `Model` that is currently being initialized.
            Keyword Args:
            **kwargs:
                 Variable length keyword arguments that are passed to the superclass's `__init_subclass__` method.

        Raises:
            TypeError:
                 If any mandatory base class initializations are omitted or incorrect arguments are provided.

        """
        preprocessor = cls.preprocessor
        validator = cls.validator
        super().__init_subclass__(**kwargs)
        if not is_redefined(cls):
            if preprocessor is not None:
                preprocessor().preprocess(cls)
            if validator is not None:
                validator().validate(cls)

    @classmethod
    def __create__(cls, **kwargs):
        """
        Creates a new instance of a model and registers it in the model's instance dictionary.
        This method is a class method that creates a new instance of the class using
        the provided keyword arguments. It utilizes the built-in __create__ method
        to initialize the instance and then stores it in a class-level dictionary
        identified by the instance's unique identifier. This allows for easy access to
        all instances of the model.

        Args:
            **kwargs:
                 Arbitrary keyword arguments passed to the model's constructor
                during instance creation.

        Returns:

        Raises:

        """
        self = super().__create__(**kwargs)
        Model.__all_instances__[self.__id__] = self
        return self


def of(element: ElementType) -> typing.Optional[typing.Union[type[Model], Model]]:
    """
    Retrieves a corresponding model instance or class associated with a given element.

    Args:
        element (ElementType):
             An instance or subclass of ElementType for which to retrieve the associated model.

    Returns:
        Optional[Union[type[Model], Model]]:
             The model class or model instance associated with the provided element if it
            exists, otherwise None.

    """
    return element.__all_elements__.get(element.__model__, None)


def all_instances() -> dict[str, Model]:
    """

    Returns a dictionary containing all instances of the Model class.

    Returns:
        dict[str, Model]:
             A dictionary where keys are strings and values are instances
            of the Model class.

    """
    return Model.__all_instances__


def dump(
    element,
    level=0,
    associated_name=None,
):
    """
    Generates a hierarchical representation of an element and its associated elements, printing out the hierarchy to the console.
    The function traverses the element's owned elements and any associated elements that are not owned, recursively printing
    out their details, including the element's qualified name, type, base type information, and memory address. The hierarchy
    is presented in an indented format to illustrate the relationships between elements.
    If 'associated_name' is provided, the printed information will reflect the associated relationship rather than the element's
    actual qualified name.

    Args:
        element:
             The ElementType instance to be dumped.
        level (int):
             The current level in the hierarchy, used for indentation. Defaults to 0.
        associated_name (Optional[str]):
             An optional name to describe the association relationship of 'element'. Defaults to None.
            The function does not return any value; it outputs directly to the console.

    """
    type_or_object = "type" if isinstance(element, type) else "object"
    if associated_name is None:
        base = (
            element.__base__.__name__
            if type_or_object == "type"
            else element.__class__.__base__.__name__
        )
        type_name = f"{type_or_object}[{base}]"
    else:
        type_name = f"{type_or_object}[Association<{qualified_name_of(type_of(element))} @ {id_of(type_of(element))}>]"
    address = id_of(element)
    print(
        f"{level * ' '}{level} -> {associated_name if associated_name is not None else qualified_name_of(element)} {type_name} @ {address}"
    )
    if associated_name is None:
        for owned_element in owned_elements_of(element):
            dump(owned_element, level + 1)
        for name, associated in associations_of(element).items():
            if id_of(associated) not in element.__owned_elements__:
                dump(
                    associated,
                    level + 1,
                    f"{qualified_name_of(element)}.{name}",
                )
