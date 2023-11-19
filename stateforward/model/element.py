from typing import (
    Union,
    Any,
    Callable,
    TypeVar,
    Generator,
    Generic,
    Sequence,
    ClassVar,
    Optional,
    ParamSpec,
    Type,
    TYPE_CHECKING,
    cast,
)
from inspect import isclass
from types import new_class
from dataclasses import MISSING
from stateforward.model.association import Association, is_association, association

if TYPE_CHECKING:
    from stateforward.model import Model

T = TypeVar("T")
P = ParamSpec("P")
R = TypeVar("R")

__all__ = (
    "ElementInterface",
    "Element",
    "ElementType",
    "is_subtype",
    "is_element",
    "is_owned_element",
    "redefine",
    "is_redefined",
    "is_type",
    "new_element",
    "first_owned_element",
    "set_attribute",
    "remove_owned_element",
    "last_owned_element",
    "left_element",
    "right_element",
    "find_owned_elements",
    "find_owned_element",
    "ancestors",
    "find_ancestors",
    "find_ancestor",
    "find_descendants",
    "add_owned_element",
    "has_descendant",
    "all_owned_elements",
    "traverse_pre_order",
    "bind",
    "remove_owned_elements",
)


class ElementInterface(Generic[T]):
    """
    ElementInterface provides a common interface for elements in the model.

    This interface defines a generic contract with attributes commonly shared among elements
    such as associations, owned elements, and model references.

    Attributes:
        name (ClassVar[str]): The name of the element.
        qualified_name (ClassVar[str]): A fully qualified name that uniquely identifies the element.
        type (ClassVar[Type["Element"]]): The concrete type of the element.
        redefined_element (ClassVar[Type["Element"]]): The element that is redefined by this element.
        associations (dict[str, Association]): A dictionary of association proxies where keys are attribute names.
        owned_elements (Union[list["ElementType"], list[T]]): A list of elements that are owned by this element.
        owner (Optional[Association["ElementType"]]): A proxy to the owner element, if any.
        model (Association["Model"]): A proxy to the model that owns this element.
        attributes (dict[Any, Any]): A dictionary of this element's attributes.

    Type Parameters:
        T: The type variable associated with the element.
    """

    # class variables
    name: ClassVar[str] = None
    qualified_name: ClassVar[str] = None
    type: ClassVar[Type["Element"]] = None
    redefined_element: ClassVar[Type["Element"]] = None

    # class & instance variables
    associations: dict[str, Association] = None
    owned_elements: Union[list["ElementType"], list[T]] = None
    owner: Optional[Association["ElementType"]] = None
    model: Association["Model"] = None
    attributes: dict[Any, Any] = None


def is_subtype(
    value: Any, types: Union["ElementType", Sequence["ElementType"]]
) -> bool:
    """Checks if a given value or its class is a subtype of another type or types.

    This function determines whether `value` is a subclass of the given `types`, or
    if the class of `value` itself is a subclass of `types` if `value` is an instance.

    Args:
        value (Any): The value, or a class object, to be checked for subtype
            relationship.
        types (Union["ElementType", Sequence["ElementType"]]): A single class (`ElementType`)
            or a sequence of classes to check against. `ElementType` is a placeholder
            and should be replaced with actual class types in implementation.

    Returns:
        bool: True if `value` is a subtype of `types`, False otherwise.

    Note:
        The function uses `issubclass()` which is a built-in function in Python to
        check for a subclass relationship. If `value` is not a class but an
        instance, it retrieves the class of `value` using `value.__class__` before
        performing the check.

    Examples:
        >>> class Parent: pass
        >>> class Child(Parent): pass
        >>> is_subtype(Child, Parent)
        True
        >>> is_subtype(Child(), Parent)
        True
        >>> is_subtype(Parent, Child)
        False
        >>> is_subtype(Parent(), (Child, Parent))
        True
    """
    return issubclass(value if isclass(value) else value.__class__, types)


def is_element(value: Any) -> bool:
    """Determines if the provided value or its class is a subtype of Element.

    This function is a specialized version of the `is_subtype` function that
    specifically checks for subclass relationship with the `Element` class.

    Args:
        value (Any): The value, or a class object, to be checked for the subclass
            relationship. It can be an instance of a class or the class itself.

    Returns:
        bool: True if `value` is a subclass or instance of a subclass of `Element`,
              False otherwise.

    Note:
        For this function to work, the `Element` class must be defined elsewhere in
        the codebase. This function makes use of the `is_subtype` utility function
        to carry out the subclass check.

    Examples:
        Assuming there is a class named `Element` defined in the codebase:

        >>> class MyElement(Element): pass
        >>> is_element(MyElement)
        True
        >>> is_element(MyElement())
        True
        >>> is_element(object)
        False
        >>> is_element(object())
        False
    """
    return is_subtype(value, (Element,))


def first_owned_element(element: "ElementType") -> Optional["ElementType"]:
    """
    Get the first owned element from the given ElementType instance.

    This function returns the first element in the 'owned_elements' list of
    'element', if it exists. It returns None if 'element' has no owned elements.

    Args:
        element ("ElementType"): The ElementType instance to retrieve the first owned element from.

    Returns:
        Optional["ElementType"]: The first owned ElementType if available, None otherwise.
    """
    return element.owned_elements[0] if element.owned_elements else None


def last_owned_element(
    element: ElementInterface,
) -> Union[Union[type["Element"], "Element"], None]:
    """Retrieves the last element in the list of owned elements of a given element.

    This function returns the last owned element if it exists; otherwise, it returns
    None. Note that this function expects that the given element has a property
    or attribute `owned_elements` which is a list of elements.

    Args:
        element (Union[type["Element"], "Element"]): The element or class of element
            whose owned elements are to be inspected.

    Returns:
        Optional[Union[type["Element"], "Element"]]: The last owned element or None
            if there are no owned elements.

    """
    owned_elements = element.owned_elements[1:]
    return owned_elements[-1] if owned_elements else None


def left_element(element: "ElementType") -> Union["ElementType", None]:
    elements = element.owner.owned_elements if is_element(element.owner) else ()
    if elements:
        i = elements.index(element)
        if i:
            return elements[i - 1]
    return None


def right_element(element: "ElementType") -> Union["ElementType", None]:
    elements = element.owner.owned_elements if is_element(element.owner) else ()
    if elements:
        i = elements.index(element)
        if i + 1 < len(elements):
            return elements[i + 1]
    return None


def find_owned_elements(
    element: "ElementType", expr: Callable[["ElementType"], bool]
) -> Generator["ElementType", None, None]:
    for owned_element in element.owned_elements:
        if expr(owned_element):
            yield owned_element


def find_owned_element(
    element: "ElementType", expr: Callable[["ElementType"], bool]
) -> Optional["ElementType"]:
    return next(find_owned_elements(element, expr), None)


def ancestors(element: "ElementType") -> Generator["ElementType", None, None]:
    if is_element(element.owner):
        yield element.owner
        yield from ancestors(element.owner)


def find_ancestors(
    element: "ElementType", expr: Callable[["ElementType"], bool]
) -> Generator["ElementType", None, None]:
    for element in ancestors(element):
        if expr(element):
            yield element


def find_ancestor(
    element: "ElementType", expr: Callable[["ElementType"], bool]
) -> Optional["ElementType"]:
    return next(find_ancestors(element, expr), None)


def find_descendants(
    element: "ElementType",
    expr: Callable[["ElementType"], bool],
) -> Generator["ElementType", None, None]:
    for element in traverse_pre_order(element):
        if expr(element):
            yield element


def has_descendant(element: "ElementType", owned_element: "ElementType") -> bool:
    return owned_element is not None and any(
        owned_element == element for element in all_owned_elements(element)
    )


def traverse_pre_order(element: "ElementType"):
    yield element
    first_element = first_owned_element(element)
    if is_element(first_element):
        yield from traverse_pre_order(first_element)
    right = right_element(element)
    if is_element(right):
        yield from traverse_pre_order(right)


def specialize(
    base_class: Type["Element"],
    derived_class: Type["Element"],
):
    # specializing an element requires recursively creating copies of the owned elements
    for inherited_element in base_class.owned_elements:
        # create a copy of the inherited element
        add_owned_element(
            derived_class,
            new_element(
                inherited_element.name,
                (inherited_element,),
                redefined_element=inherited_element
                if derived_class.redefined_element is not None
                else None,
            ),
        )

    # we only want to map attributes after all the sub elements have been specialized
    if base_class.owner is None:
        # create a map of all the elements
        element_map = dict(
            (element.qualified_name, element)
            for element in traverse_pre_order(derived_class)
        )
        for element in element_map.values():
            for name, value in element.attributes.items():
                # we know attributes are proxies so update them to proxy the specialized element
                if is_element(value):
                    value = element_map[
                        value.qualified_name.replace(
                            base_class.qualified_name, derived_class.qualified_name, 1
                        )
                    ]
                set_attribute(element, name, value)
        for name, value in derived_class.__dict__.items():
            if (
                name not in ElementInterface.__annotations__
                and is_element(value)
                and has_descendant(base_class, value)
            ):
                set_attribute(
                    derived_class,
                    name,
                    element_map[
                        value.qualified_name.replace(
                            base_class.qualified_name, derived_class.qualified_name, 1
                        )
                    ],
                )


class Alias(str):
    pass


class Element(ElementInterface[T]):
    """
    Element is the base class for all elements in the model.

    The Element class extends ElementInterface and provides a default implementation of several methods.
    It supports customization via the '__init_subclass__' and '__define__' methods, which allows
    properties and behavior specific to a given element to be set up.

    Attributes:
        associations (dict[str, Association]): A dictionary of association proxies where keys are attribute names.
        owned_elements (Union[list["ElementType"], list[T]]): A list of elements that are owned by this element.
        owner (Optional[Association["ElementType"]]): A proxy to the owner element, if any.
        model (Association["Model"]): A proxy to the model that owns this element.
        attributes (dict[Any, Any]): A dictionary of this element's attributes.

    Type Parameters:
        T: The type variable associated with the element.

    Methods:
        __init_subclass__: Allows subclasses to be initialized with custom attributes and behavior.
        __define__: Allows for the definition of owned elements and other properties.
        __new__: Overrides the default object instantiation behavior.
    """

    __init__: Callable[P, None] = object.__init__

    def __init_subclass__(
        cls: type["Element"],
        name: str = None,
        redefined_element: "ElementType" = None,
        **kwargs: dict,
    ) -> None:
        """
        Initialize a new subclass of Element.

        Invoked when a new subclass of Element is defined in order to customize
        element-specific attributes, associations, and owned elements.
        Supports specialization of the base class by copying inherited elements
        and setting up attributes.

        Parameters:
        - cls (type["Element"]): The class object representing the subclass being initialized.
        - name (str, optional): The name of the element. If not provided, defaults to the name of the subclass.
        - redefined_element (ElementType, optional): The element that the subclass redefines.
        - **kwargs (dict): Additional keyword arguments containing attribute initializations which are not directly handled.

        Raises:
        - TypeError: If an unexpected keyword is encountered in element initializations.

        Note:
        - Redefined elements allow subclassing elements to replace or extend the behavior of inherited features.
        - The method also takes care of handling the owned elements through specialization.
        - Attributes like "owning association" and "model" are set here.
        """
        attributes = cls.attributes = (cls.attributes or {}).copy()
        for key in kwargs:
            if key not in attributes and getattr(cls, key, ...) is ...:
                raise TypeError(
                    f"{name or cls.__name__}.__init_subclass__ got an unexpected keyword {key}"
                )
        cls.owned_elements = []
        cls.name = name or cls.__name__
        cls.qualified_name = cls.__qualname__
        cls.owner = None
        # cls.type = cls
        cls.model = association(cls)
        cls.associations = {}
        cls.redefined_element = redefined_element or cls.redefined_element
        if cls.__base__.owned_elements:
            specialize(cls.__base__, cls)
        else:
            cls.type = cls
        if redefined_element is None:
            cls.__define__(name=name, **kwargs)
        else:
            cls.__redefine__(cls.redefined_element, **kwargs)

    @classmethod
    def __redefine__(cls, _: "ElementType", **kwargs):
        for key, value in kwargs.items():
            set_attribute(cls, key, value)

    def __set_name__(self, owner, name):
        print("set name", owner, name)

    @classmethod
    def __define__(
        cls: type["Element"],
        name: str = None,
        owned_elements: Sequence["ElementType"] = (),
        **kwargs: dict,
    ) -> None:
        """
        Define the class-level attributes for the Element class or subclass.

        This method is used to set up the owned elements and any additional
        attributes passed in the kwargs. It ensures that owned elements are
        properly added and that each additional attribute is set on the class
        if it's not already defined in the `ElementInterface`.

        Args:
            cls (type[Element]): The class on which to define the attributes.
            name (str): The name of the element. If not provided, the __name__ attribute of the class will be used.
            owned_elements (Sequence[ElementType]): A sequence of ElementType objects that are owned by this element.
            **kwargs (dict): Additional keyword arguments representing the attributes to be set on the class.

        Raises:
            TypeError: If an unexpected keyword argument is provided that is not part of the class attributes or annotations.
        """
        for owned_element in owned_elements:
            add_owned_element(cls, owned_element)
        for key, value in {
            **dict((name, getattr(cls, name, MISSING)) for name in cls.__annotations__),
            **cls.__dict__,
            **kwargs,
        }.items():
            if (
                f"{key[-2:]}{key[:2]}" != "____"
                and key not in ElementInterface.__annotations__
            ):
                set_attribute(cls, key, value)

    @staticmethod
    def __new__(
        cls: type["Element"], *args: Sequence[Any], **kwargs
    ) -> Union["Element", Callable[[], "Element"]]:
        """
        Create a new instance or a callable to instantiate the Element class.

        This method intercepts the creation of a new Element object to support
        custom initialization logic, such as setting up owned elements and attributes
        before calling __init__. If no owner is specified, this method returns the
        created instance directly. If an owner is given, a lambda function delaying
        the call to __init__ is returned instead.

        Parameters:
        - cls (type[Element]): The class object from which an instance is created.
        - *args (Sequence[Any]): Variable length argument list.
        - **kwargs (dict): Arbitrary keyword arguments.

        Returns:
        - Union[Element, Callable[[], Element]]: An instance of the Element class or
          a callable that, when called, returns an instance of the Element class.
        """

        self = super().__new__(cls)
        self.owner = kwargs.pop("owner", None)
        self.owned_elements = []
        self.attributes = {}
        self.model = self.owner.model if self.owner is not None else self
        element_map = kwargs.pop(
            "element_map", {self.qualified_name: self}
        )  # create a namespace for the elements in the element
        for owned_element in cls.owned_elements:
            instance = owned_element(
                owner=self,
                element_map=element_map,
            )()  # using the extra function call to prevent __init__ from being called
            element_map[owned_element.qualified_name] = instance
            self.owned_elements.append(instance)
        if self.owner is None:
            for element in reversed(element_map.values()):
                for name, value in element.__class__.attributes.items():
                    if is_element(value):
                        value = element.attributes[name] = element_map[
                            value.qualified_name
                        ]
                        setattr(element, str(name), value)
                if element is not self:
                    element.__init__(**kwargs.pop(element.qualified_name, {}))
            # this is the root element of the element, so we can start initializing
            return self
        # a hack to prevent __init__ from being called
        return lambda _self=self: _self


TypeElement = Type[Element]
ElementType = Union[TypeElement, Element, Association[T]]


def all_owned_elements(
    element: ElementType,
) -> Generator[Association[ElementType], None, None]:
    """
    Generator function to iterate over all elements owned by a given element, including nested owned elements.

    Parameters:
        element (ElementType): The element whose owned elements are to be iterated over.

    Yields:
        Association[ElementType]: A proxy association to the next owned element in the sequence.
    """
    for owned_element in element.owned_elements:
        yield owned_element
        yield from all_owned_elements(owned_element)


def new_element(name: str = None, bases: tuple[type] = (Element,), **kwargs) -> T:
    """
    Factory function to create a new element class or instance with the specified bases and attributes.

    Parameters:
        name (str): The name for the new element. If None, the default 'Element' name is used.
        bases (tuple[type], optional): A tuple of base classes for the new element class.
        **kwargs: Additional keyword arguments representing attributes and their values.

    Returns:
        ElementType: The new element class or instance created.
    """
    return cast(
        ElementType,
        new_class(name or bases[0].__name__, bases, {"name": name, **kwargs}),
    )


def is_type(value: Any, element_type: ElementType) -> bool:
    """
    Check if the provided value is of the given element type.

    Parameters:
        value (Any): The value to perform the type check on.
        element_type (ElementType): The element type to be checked against the value.

    Returns:
        bool: True if the value is of the given element type, False otherwise.
    """
    bases = value.__bases__ if isclass(value) else value.__class__.__bases__
    return element_type in bases


def is_owned_element(element: ElementType) -> bool:
    """
    Determine if the element is an owned element.

    Parameters:
        element (ElementType): The element to check for ownership.

    Returns:
        bool: True if the element is an owned element, i.e., it has an owner; False otherwise.
    """
    return is_element(element) and element.owner is not None


def remove_owned_element(
    element: ElementType, owned_element: ElementType
) -> ElementType:
    if owned_element not in element.owned_elements:
        raise ValueError(f"element {owned_element} is not owned by {element}")
    owned_element.owner = owned_element.model = None
    element.owned_elements.remove(owned_element)
    return owned_element


def remove_owned_elements(
    element: ElementType, *owned_elements: Sequence[ElementType]
) -> Sequence[ElementType]:
    if not owned_elements:
        owned_elements = element.owned_elements[:]
    removed_elements = tuple(
        remove_owned_element(element, owned_element) for owned_element in owned_elements
    )
    return removed_elements


def set_qualified_name(
    owner: ElementType, owned_element: ElementType, name: str = None
):
    if name is not None:
        owned_element.name = str(name)
    owned_element.__module__ = owner.__module__
    owned_element.qualified_name = (
        owned_element.__qualname__
    ) = f"{owner.qualified_name}.{owned_element.name}"
    owned_element.model = owner.model
    for _owned_element in owned_element.owned_elements:
        set_qualified_name(owned_element, _owned_element)


def add_owned_element(
    element: type[Element], owned_element: type["Element"], name: str = None
):
    if owned_element.owner is not None:
        raise ValueError(
            f"element {owned_element.qualified_name} is already owned by {owned_element.owner.qualified_name}"
        )
    owned_element.owner = association(element)
    element.owned_elements.append(owned_element)
    set_qualified_name(element, owned_element, name)
    return owned_element


def add_association(
    element: type[Element], associated: type["Association"], name: str = None
):
    element.associations[name] = associated


def set_attribute(element: type[Element], name: Union[str, int], value: Any):
    from stateforward.model.collection import is_collection

    if is_element(value):
        # check if the element is already a proxy
        # flags = (is_association(value), value.owner is not None, value == element.model)
        if is_association(value) or value.owner is not None or value == element.model:
            # if not flags[0] and flags[1] and not is_collection(element):
            #     # this element is the namespace of the element, so we need to update the qualified name
            #     set_qualified_name(value.owner, value, name)
            add_association(element, value := association(value), name)
        else:
            add_owned_element(
                element, value, name if not is_collection(element) else None
            )
        # if not is_association(value) and value.owner is None and value != element.model:
        #     add_owned_element(
        #         element, value, name if not is_collection(element) else None
        #     )
        #
        #     # attributes are always proxies
        #     value = association(value)
        # else:
        #     add_association(element, value, name)

    value = element.attributes[name] = value
    setattr(element, str(name), value)
    return value


def is_redefined(element: ElementType) -> bool:
    return element.redefined_element is not None


def redefine(
    element: ElementType,
    **attributes,
) -> ElementType:
    """
    redefining an element will create a new specialization of the element and overwrite the attributes of the element
    :param element:
    :param attributes:
    :return:
    """
    return new_element(
        bases=(element,),
        redefined_element=element,
        **attributes,
    )


def bind(element: ElementType, **attributes) -> ElementType:
    return (
        new_element(bases=(element,), redefined_element=element, **attributes)
        if element.owner is not None
        else element
    )
