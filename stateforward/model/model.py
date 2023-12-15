import typing
from stateforward.model.element import (
    Element,
    ElementType,
    id_of,
    type_of,
    qualified_name_of,
    owned_elements_of,
    associations_of,
)

if typing.TYPE_CHECKING:
    from stateforward.model.preprocessor import Preprocessor
    from stateforward.model.interpreter import Interpreter
    from stateforward.model.validator import Validator

__all__ = (
    "Model",
    "of",
    "dump",
    "all_instances",
)


class Model(Element):
    __all_instances__: dict[str, "Model"] = {}
    preprocessor: typing.ClassVar[type["Preprocessor"]] = None
    validator: typing.ClassVar[type["Validator"]] = None
    interpreter: "Interpreter" = None

    def __init_subclass__(
        cls: type["Model"],
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
        preprocessor = cls.preprocessor
        validator = cls.validator
        super().__init_subclass__(**kwargs)
        if preprocessor is not None:
            preprocessor().preprocess(cls)
        if validator is not None:
            validator().validate(cls)

    @classmethod
    def __create__(cls, **kwargs):
        self = super().__create__(**kwargs)
        Model.__all_instances__[self.__id__] = self
        return self


def of(element: ElementType) -> typing.Optional[typing.Union[type[Model], Model]]:
    """Returns the model associated with the provided element.

    Args:
        element: The element whose model is to be returned.

    Returns:
        Optional[Type[Model]]: The model associated with the provided element.
    """
    return element.__all_elements__.get(element.__model__, None)


def all_instances() -> dict[str, Model]:
    """Returns a dictionary of all model instances.

    Returns:
        dict[str, Model]: A dictionary of all model instances.
    """
    return Model.__all_instances__


def dump(
    element,
    level=0,
    associated_name=None,
):
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
