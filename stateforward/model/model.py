from typing import ClassVar, TYPE_CHECKING, Type, Optional
from stateforward.model.element import Element, set_attribute
from inspect import isclass

if TYPE_CHECKING:
    from stateforward.model.preprocessor import Preprocessor
    from stateforward.model.interpreter import Interpreter
    from stateforward.model.validator import Validator

__all__ = (
    "Model",
    "dump",
)


class Model(Element):
    """A base Model class for handling processing elements.

    `Model` serves as a template for creating models which include preprocessing,
    validation, and interpretation logic. Subclasses of Model should define their
    specific processing behavior.

    Attributes:
        preprocessor (ClassVar[Preprocessor], optional): A class-level attribute
            that holds a `Preprocessor` instance or None by default. The `Preprocessor`
            instance is responsible for preparing input data for the model.
        validator (ClassVar[Validator], optional): A class-level attribute that
            holds a `Validator` instance or None by default. The `Validator` instance is
            responsible for ensuring that the model's input data is valid.
        interpreter (ClassVar[type[Interpreter]], optional): A class-level attribute
            that holds a 'Interpreter' class or None by default. The 'Interpreter'
            class is responsible for interpreting the model's output.

    To create a subclass of Model with specific processing components:

    ```python
    class MyModel(Model, preprocessor=MyPreprocessor, validator=MyValidator,
                  interpreter=MyInterpreter):
        pass
    ```

    When creating a subclass, if specific processors are not provided, the
    class-level attributes from the `Model` base class will be used.

    Note:
        - If a preprocessor is provided and a preprocessor already exists, the
          existing one's `preprocess` method will be called before it is replaced.
        - Similarly, if a validator is provided and a validator already exists, the
          existing one's `validate` method will be called before it is replaced.
    """

    preprocessor: ClassVar[Type["Preprocessor"]] = None
    validator: ClassVar[Type["Validator"]] = None
    interpreter: ClassVar[Type["Interpreter"]] = None

    def __init_subclass__(
        cls: type["Model"],
        # preprocessor: Optional[type["Preprocessor"]] = None,
        # validator: Optional[type["Validator"]] = None,
        # processor: Optional[type["Interpreter"]] = None,
        **kwargs,
    ):
        """Initializes the subclass with the provided processors.

        This magic method is automatically called during the creation of a subclass
        and updates the subclass's preprocessor, validator, and interpreter with the
        provided arguments if they are not None; otherwise, it retains the existing
        processors from the base class.

        Args:
            cls: The subclass of `Model` being initialized.
            preprocessor: An instance or class of
                a `Preprocessor`.
            validator: An instance or class of a `Validator`.
            processor: A class of `Interpreter`.
            **kwargs: Arbitrary keyword arguments that are passed to the base
                class's `__init_subclass__` method.
        """
        preprocessor = kwargs.pop("preprocessor", None)
        validator = kwargs.pop("validator", None)
        interpreter = kwargs.pop("interpreter", None)
        super().__init_subclass__(**kwargs)
        if cls.preprocessor is not None:
            cls.preprocessor().preprocess(cls)
        set_attribute(cls, "preprocessor", preprocessor or cls.preprocessor)
        if cls.validator is not None:
            cls.validator().validate(cls)
        set_attribute(cls, "validator", validator or cls.validator)
        set_attribute(cls, "interpreter", interpreter or cls.interpreter)


def dump(element, level=0, associated_name=None, max_level=None):
    if max_level is not None and level > max_level:
        return
    type_or_object = "type" if isclass(element) else "object"
    if associated_name is None:
        base = (
            element.__base__.__name__
            if isclass(element)
            else element.__class__.__base__.__name__
        )
        type_name = f"{type_or_object}[{base}]"
    else:
        type_name = f"{type_or_object}[Association<{element.type.qualified_name}>]"
    address = hex(
        id(element if associated_name is None else element.type)
        if isclass(element)
        else element.__hash__()
    )
    print(
        f"{level * ' '}{level} -> {associated_name if associated_name is not None else element.qualified_name} {type_name} @ {address}"
    )
    if not associated_name:
        for owned_element in element.owned_elements:
            dump(owned_element, level + 1, max_level=max_level)
        for name, associated in element.associations.items():
            dump(
                getattr(element, str(name), associated),
                level + 1,
                f"{element.qualified_name}.{name}",
                max_level=max_level,
            )
