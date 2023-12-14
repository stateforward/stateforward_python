import typing
from weakref import WeakValueDictionary
import types

ElementType = typing.TypeVar(
    "ElementType", bound=typing.Union[type["Element"], "Element"]
)
T = typing.TypeVar("T", bound="Element")


def id_of(element: ElementType) -> int:
    """
    :param element: The element to get the ID of.
    :return: The ID of the element. If the element has a `__id__` attribute, that value is returned. Otherwise, the ID of the element itself is returned.

    """
    return getattr(element, "__id__", id(element))


def type_of(element: ElementType) -> type["Element"]:
    """
    :param element: The element whose type needs to be determined.
    :return: The type of the element.
    """
    return element.__type__


def owned_elements_of(
    element: ElementType,
) -> typing.Generator[ElementType, None, None]:
    """
    :param element: The element for which to retrieve the owned elements.
    :return: A generator that yields the owned elements of the given element.
    """
    for owned_element_id in element.__owned_elements__:
        yield element.__all_elements__[owned_element_id]


def descendants_of(element: ElementType) -> typing.Generator[ElementType, None, None]:
    """
    Return a generator that yields all descendants of a given element.

    :param element: The element of which to find descendants.
    :type element: ElementType
    :return: A generator that yields all descendants of the given element.
    :rtype: typing.Generator[ElementType, None, None]
    """
    for owned_element in owned_elements_of(element):
        yield owned_element
        yield from descendants_of(owned_element)


def is_descendant_of(ancestor: ElementType, descendant: ElementType) -> bool:
    """Check if a given element is a descendant of another element.

    :param ancestor: The ancestor element to check against.
    :param descendant: The descendant element to check.
    :return: True if the descendant is a descendant of the ancestor, False otherwise.
    """
    return (
        next(
            (element for element in descendants_of(ancestor) if element == descendant),
            None,
        )
        is not None
    )


def ancestors_of(element: ElementType) -> typing.Generator[ElementType, None, None]:
    """
    Retrieves the ancestors of the given element.

    :param element: The element to retrieve the ancestors for.
    :type element: ElementType
    :return: A generator that produces the ancestors of the element.
    :rtype: typing.Generator[ElementType, None, None]
    """
    owner = owner_of(element)
    if owner is not None:
        yield owner
        yield from ancestors_of(owner)


def is_ancestor_of(descendant: ElementType, ancestor: ElementType) -> bool:
    """
    Determines if the given `descendant` is an ancestor of the `ancestor` element.

    :param descendant: The descendant element to check.

    :param ancestor: The ancestor element to check against.

    :return: True if the `descendant` is an ancestor of the `ancestor` element, False otherwise.
    """
    return is_descendant_of(ancestor, descendant)


def set_model(element: ElementType, model: ElementType):
    """
    Set the model for the given element and its owned elements recursively.

    :param element: The element to set the model for.
    :type element: ElementType
    :param model: The model to set for the element and its owned elements.
    :type model: ElementType
    """
    element.__model__ = id_of(model)
    for owned_element in owned_elements_of(element):
        set_model(owned_element, model)


def set_owner(element: ElementType, owner: ElementType):
    """
    Set the owner of an element.

    :param element: The element whose owner is to be set.
    :type element: ElementType
    :param owner: The owner element.
    :type owner: ElementType
    :return: None
    """
    element.__owner__ = id_of(owner)
    for owned_element in owned_elements_of(element):
        set_owner(owned_element, element)
    set_model(element, element.__all_elements__[owner.__model__])


def add_owned_element_to(
    owner: ElementType,
    element: ElementType,
    name: str = None,
    *,
    change_ownership: bool = False,
):
    """
    :param owner: The owner of the element to be added.
    :param element: The element to be added to the owner.
    :param name: Optional. The name to assign to the element.
    :param change_ownership: Optional. Whether to change the ownership of the element if it already has an owner.
    :return: None

    This method adds the specified element to the given owner. If the element already has an owner and the change_ownership parameter is set to False, a ValueError will be raised. If the
    * element already has an owner and the change_ownership parameter is set to True, the element will be removed from the current owner before being added to the new owner.

    The owner's __owned_elements__ list will be updated with the ID of the added element. If a name is provided, it will be assigned to the element and its qualified name will be updated
    * to include the owner's qualified name and the provided name.
    """
    element_owner = owner_of(element)
    if element_owner is not None:
        if not change_ownership:
            raise ValueError(f"element {element.__name__} already has an owner")
        remove_owned_element_from(element_owner, element)
    set_owner(element, owner)
    owner.__owned_elements__.append(id_of(element))
    # if name is not None and not is_collection(owner):
    #     element.__name__ = name
    #     element.__qualname__ = f"{owner.__qualname__}.{name}"


def remove_owned_element_from(
    owner: ElementType, element: ElementType, *, disassociate: bool = False
) -> ElementType:
    """
    :param owner: The owner of the element to be removed.
    :param element: The element to be removed.
    :param disassociate: Specifies whether to also disassociate the element from its associations. Default is False.
    :return: The removed element.

    Removes the specified element from the owner. If the element is not owned by the owner, a ValueError is raised. If disassociate is True, it also removes any associations that the element
    * has.
    """
    element_id = id_of(element)
    if owner_of(element) != owner:
        raise ValueError(f"element {element.__name__} is not owned by {owner.__name__}")
    if disassociate:
        for name, element in associations_of(element).items():
            remove_association_from(element, name)
    owner.__owned_elements__.remove(element_id)
    element.__owner__ = None
    return element


def remove_owned_elements_from(
    owner: ElementType, *owned_elements: typing.Collection[ElementType]
) -> typing.Collection[ElementType]:
    """
    Remove owned elements from an owner.

    :param owner: The owner from which to remove the owned elements.
    :param owned_elements: The owned elements to be removed. If not provided, all owned elements of the owner will be removed.
    :return: A collection of the removed elements.
    """
    if not owned_elements:
        owned_elements = tuple(owned_elements_of(owner))
    removed_elements = tuple(
        remove_owned_element_from(owner, owned_element)
        for owned_element in owned_elements
    )
    return removed_elements


def add_association_to(owner: ElementType, element: ElementType, name: str = None):
    """
    Add an association to the provided 'owner' object.

    :param owner: The object to which the association will be added.
    :type owner: ElementType
    :param element: The object that will be associated with the 'owner'.
    :type element: ElementType
    :param name: The name of the association. Optional.
    :type name: str
    :return: None
    """
    owner.__associations__[name] = id_of(element)


def remove_association_from(owner: ElementType, element: ElementType):
    """
    Remove association between owner and element.

    :param owner: The owner object.
    :type owner: ElementType
    :param element: The element object.
    :type element: ElementType
    :return: None
    """
    for name, element in associations_of(owner).items():
        if element == element:
            del owner.__associations__[name]


def associations_of(element: ElementType) -> dict[str, ElementType]:
    """
    :param element: The element for which associations are to be retrieved.
    :return: A dictionary containing associations of the element, where the keys are the names of the associations and the values are the associated elements.

    """
    return dict(
        (name, element.__all_elements__[element_id])
        for name, element_id in element.__associations__.items()
    )


def associations_for(
    element: ElementType, associated: ElementType
) -> dict[str, ElementType]:
    """
    :param element: The element for which to retrieve associations.
    :param associated: The associated element to find associations for.
    :return: A dictionary of associations for the given element and associated element.

    This method returns a dictionary containing associations for the given element and associated element. The dictionary is created by iterating through the associations of the element
    * and checking if the associated element matches the provided associated parameter. Only associations that match the associated element are included in the dictionary.

    The dictionary has the association names as keys and the associated elements as values.

    Example usage:
    ```python
    element = ...  # The element for which to retrieve associations
    associated = ...  # The associated element to find associations for

    result = associations_for(element, associated)
    print(result)  # Output: {'association_name': associated_element}
    ```
    """
    return dict(
        (name, element.__all_elements__[element_id])
        for name, element_id in element.__associations__.items()
        if element_id == id_of(associated)
    )


def name_of(element: ElementType) -> str:
    """
    Get the name of the element.

    :param element: The element for which the name is to be retrieved.
    :type element: ElementType
    :return: The name of the element.
    :rtype: str
    """
    return element.__name__ if isinstance(element, type) else element.__class__.__name__


def attributes_of(element: ElementType) -> dict[str, typing.Any]:
    """
    Retrieve the attributes of the given element.

    :param element: The element whose attributes are to be retrieved.
    :type element: ElementType
    :return: A dictionary containing the attributes of the element.
    :rtype: dict[str, typing.Any]
    """
    return element.__annotations__


def qualified_name_of(element: ElementType) -> str:
    """
    Returns the qualified name of the given element.

    :param element: The element for which the qualified name is desired.
    :type element: ElementType
    :return: The qualified name of the element.
    :rtype: str
    """
    owner = owner_of(element)
    if owner is None:
        return name_of(element)
    return f"{qualified_name_of(owner)}.{name_of(element)}"


def is_type(
    element: ElementType, types: typing.Union[type, typing.Collection[type]]
) -> bool:
    """
    Check if an element is of a specific type or types.

    :param element: The element to check the type of.
    :param types: The type or types to check against.
    :return: True if the element is of the specified type or types, False otherwise.
    """
    return (
        issubclass(element, types)
        if isinstance(element, type)
        else isinstance(element, types)
    )


def is_subtype(
    element: ElementType, types: typing.Union[type, typing.Collection[type]]
) -> bool:
    """
    Check if the given element is a subtype of the specified types.

    :param element: The element to check.
    :param types: The types to check against. Can be a single type or a collection of types.
    :type element: ElementType
    :type types: Union[type, Collection[type]]
    :return: True if the element is a subtype of any of the specified types, False otherwise.
    :rtype: bool
    """
    if is_element(types):
        types = (types,)
    return element not in types and is_type(element, types)


def is_element(value: typing.Any) -> bool:
    """
    Check if the given value is an instance of the Element class.

    :param value: The value to be checked.
    :return: True if the value is an instance of the Element class, False otherwise.
    """
    return is_type(value, Element)


def owner_of(element: ElementType) -> ElementType:
    """
    :param element: The element for which to determine the owner.
    :return: The owner of the element, or None if the element has no owner.
    """
    return (
        element.__owner__
        if isinstance(element, Element)
        else element.__all_elements__.get(element.__owner__, None)
    )


def redefined_element_of(element: ElementType) -> ElementType:
    """
    Retrieve the redefined element of a given element.

    :param element: The element for which to retrieve the redefined element.
    :return: The redefined element of the given element.
    """
    return element.__redefined_element__


def is_owner_of(owner: ElementType, element: ElementType) -> bool:
    """

    :param owner: The owner of the element.
    :type owner: ElementType

    :param element: The element to check ownership for.
    :type element: ElementType

    :return: True if the owner is the current owner of the element, false otherwise.
    :rtype: bool

    """
    return owner_of(element) == owner


def specialize(base: ElementType, derived: ElementType, **kwargs):
    """
    :param base: The base ElementType to specialize from.
    :param derived: The derived ElementType to create as a specialization of the base.
    :param kwargs: Additional keyword arguments.
    :return: None

    Specializes the base ElementType to create a derived ElementType by creating copies of the base elements during inheritance. The method loops through the base owned element mapping and
    * creates new owned elements for the derived ElementType. The specialized ElementType is then returned.

    """
    # we have to create copies of the base elements during inheritance
    # loop through base owned element mapping
    for owned_element_id in base.__owned_elements__:
        # get the owned element
        owned_element = base.__all_elements__[owned_element_id]
        # create a new owned element
        new_owned_element = typing.cast(
            ElementType,
            types.new_class(
                owned_element.__name__,
                (owned_element,),
                {
                    "redefined_element": base,
                },
            ),
        )
        add_owned_element_to(derived, new_owned_element)
        # for name, value in associations_of(base).items():
        #     if value == owned_element:
        #         add_association_to(derived, new_owned_element, name)

    if owner_of(base) is None:
        base_elements = (base, *descendants_of(base))
        new_elements = (derived, *descendants_of(derived))
        element_map = dict(
            (id_of(base), id_of(derived))
            for base, derived in zip(base_elements, new_elements)
        )

        for index, element in enumerate(base_elements):
            for name, element_id in element.__associations__.items():
                new_element = new_elements[index]
                associated_element = new_element.__associations__[name] = element_map[
                    element_id
                ]
                setattr(new_element, name, associated_element)
    return None


def is_redefined(element: ElementType) -> bool:
    """
    :param element: The element to check for redefinition.
    :return: True if the element is redefined, False otherwise.
    """
    return redefined_element_of(element) is not None


def redefine(element: ElementType, **kwargs):
    """
    :param element: The element that needs to be redefined.
    :param kwargs: Additional keyword arguments to be added to the redefined element.
    :return: The redefined element.

    This method takes an element and any additional keyword arguments and creates a new class that is a subclass of the original element. The new class has all the properties and methods
    * of the original element, but with the additional keyword arguments added.

    Example usage:
        >>> redefine(MyElement, additional_property='value')
        <class '__main__.MyElement'>  # The redefined element
    """
    return typing.cast(
        ElementType,
        types.new_class(
            name_of(element),
            (element,),
            {
                "redefined_element": element,
                **kwargs,
            },
        ),
    )


def find_owned_elements_of(
    element: "ElementType", condition: typing.Callable[["ElementType"], bool]
) -> typing.Generator["ElementType", None, None]:
    """

    This method finds owned elements of a given element that satisfy a given condition.

    :param element: The element for which to find owned elements.
    :param condition: A callable that takes an ElementType object and returns True if the object satisfies the condition.
    :return: A generator that yields ElementType objects that are owned by the given element and satisfy the condition.

    """
    for owned_element in owned_elements_of(element):
        if condition(owned_element):
            yield owned_element


def find_owned_element_of(
    element: "ElementType", condition: typing.Callable[["ElementType"], bool]
) -> typing.Optional["ElementType"]:
    """
    Find and return an owned element that satisfies the given condition.

    :param element: The element to search for owned elements.
    :param condition: A callable that takes an element and returns a boolean value indicating whether the element satisfies the condition.
    :return: The owned element that satisfies the condition, or None if no such element is found.

    """
    return next(find_owned_elements_of(element, condition), None)


def find_ancestors_of(
    element: "ElementType", condition: typing.Callable[["ElementType"], bool]
) -> typing.Generator["ElementType", None, None]:
    """
    Find the ancestors of the given element that satisfy the given condition.

    :param element: The element for which to find ancestors.
    :param condition: A callable that determines if an ancestor satisfies the condition. It takes an ancestor element as
    input and returns a boolean value.
    :return: A generator that yields ancestors of the element that satisfy the condition.
    """
    for element in ancestors_of(element):
        if condition(element):
            yield element


def find_ancestor_of(
    element: "ElementType", expr: typing.Callable[["ElementType"], bool]
) -> typing.Optional["ElementType"]:
    """
    Find the ancestor of the given element that satisfies the given expression.

    :param element: The element for which to find the ancestor.
    :param expr: The expression that must be satisfied by the ancestor.
    :return: The ancestor of the element that satisfies the expression, or None if no such ancestor is found.
    """
    return next(find_ancestors_of(element, expr), None)


def find_descendants_of(
    element: "ElementType",
    condition: typing.Callable[["ElementType"], bool],
) -> typing.Generator["ElementType", None, None]:
    """
    :param element: The element from which the descendants are to be found.
    :type element: ElementType

    :param condition: The condition that each descendant must satisfy.
    :type condition: Callable[ElementType, bool]

    :return: A generator that yields the descendants of the specified element that satisfy the condition.
    :rtype: Generator[ElementType, None, None]
    """
    for element in descendants_of(element):
        if condition(element):
            yield element


def set_attribute(
    element: ElementType,
    name: str,
    value: typing.Any,
):
    """
    :param element: The element for which the attribute will be set.
    :param name: The name of the attribute.
    :param value: The value to be set for the attribute.
    :return: None

    Sets the attribute with the given name to the provided value for the given element. If the value is an element, it checks the ownership and association before setting the value.
    """
    if is_element(value):
        value_id = id_of(value)
        if value_id not in element.__owned_elements__:
            owner = owner_of(value)
            change_ownership = (
                owner is None or is_descendant_of(element, owner)
            ) and element.__model__ != id_of(value)
            if change_ownership:
                add_owned_element_to(
                    element, value, name, change_ownership=change_ownership
                )
        add_association_to(element, value, name)
    setattr(element, name, value)


def new(name: str, bases: typing.Collection[type] = None, **kwargs) -> type[T]:
    """
    :param name: the name of the class to be created
    :param bases: the base classes for the new class (optional)
    :param kwargs: additional keyword arguments used to define attributes and methods of the new class (optional)
    :return: the newly created class

    """
    return typing.cast(
        type[T],
        types.new_class(
            name,
            bases or (Element,),
            {
                **kwargs,
            },
        ),
    )


class Element(typing.Generic[T]):
    """
    :class: Element

    Generic class representing an element.

    Attributes:
        - __all_elements__: dict[int, "ElementType"]: Dictionary containing all elements.
        - __id__: typing.ClassVar[int]: Unique identifier for an element.
        - __owned_elements__: list[int]: List of owned elements.
        - __redefined_element__: typing.Optional["Element"]: Redefined element, if any.
        - __associations__: dict[str, int]: Dictionary of associations with other elements.
        - __owner__: typing.Optional[int]: Owner of the element.
        - __type__: typing.ClassVar[type["Element"]]: Type of the element.
        - __model__: typing.Optional[int]: Model identifier for the element.
        - __init__: typing.Callable[..., None]: Initializer function.

    Methods:
        - __init_subclass__(cls, **kwargs): Initializes a subclass of Element.
        - __define__(cls, **kwargs): Defines the element.
        - __redefine__(cls, **kwargs): Redefines the element.
        - __create__(cls, **kwargs): Creates a new instance of the element.
        - __new__(cls, *args: typing.Collection[typing.Any], **kwargs) -> typing.Union["Element", typing.Callable[[], "Element"]]: Creates a new element instance.
    """

    __all_elements__: dict[int, "ElementType"] = {}
    __id__: typing.ClassVar[int] = 0
    __owned_elements__: list[int] = None
    __redefined_element__: typing.Optional["Element"] = None
    __associations__: dict[str, int] = None
    __owner__: typing.Optional[int] = None
    __type__: typing.ClassVar[type["Element"]] = None
    __model__: typing.Optional[int] = None
    __init__: typing.Callable[..., None] = object.__init__

    def __init_subclass__(cls, **kwargs):
        cls.__owned_elements__ = []
        cls.__id__ = Element.__id__ = Element.__id__ + 1
        cls.__model__ = cls.__id__
        cls.__all_elements__[cls.__id__] = cls
        cls.__associations__ = {}
        cls.__type__ = cls
        cls.__owner__ = None
        cls.__name__ = kwargs.pop("name", cls.__name__)
        redefined_element = cls.__redefined_element__ = kwargs.pop(
            "redefined_element", None
        )
        if is_subtype(cls.__base__, Element):
            cls.__annotations__.update(cls.__base__.__annotations__)
            specialize(cls.__base__, cls)
        if redefined_element is None:
            cls.__define__(**kwargs)
        else:
            cls.__redefine__(**kwargs)

    @classmethod
    def __define__(cls, **kwargs):
        for owned_element in kwargs.get("owned_elements", ()):
            add_owned_element_to(cls, owned_element)

        def sort_namespace(namespace: dict[str, typing.Any]) -> dict[str, typing.Any]:
            owned = {}
            orphans = {}
            attributes = {}
            for key, item in namespace.items():
                if key not in Element.__dict__:
                    item_id = id_of(item)
                    if is_element(item):
                        if owner_of(item) is None:
                            orphans[key] = (item_id, item)
                        else:
                            owned[key] = (item_id, item)
                    else:
                        attributes[key] = (item_id, item)

            return {**orphans, **owned, **attributes}

        sorted_namespace = sort_namespace(
            {
                **cls.__dict__,
                **dict(
                    (name, kwargs.get(name, getattr(cls, name, None)))
                    for name in cls.__annotations__
                ),
            },
        )
        for name, (item_id, item) in sorted_namespace.items():
            set_attribute(cls, name, item)

    @classmethod
    def __redefine__(cls, **kwargs):
        pass

    @classmethod
    def __create__(cls, **kwargs):
        self = super().__new__(cls)
        owner = self.__owner__ = kwargs.pop("owner", None)
        self.__owned_elements__ = []
        self.__id__ = kwargs.pop("id", id(self))
        self.model = owner.model if owner is not None else self
        all_elements = self.__all_elements__ = kwargs.pop(
            "all_elements", {id_of(cls): self}
        )  # create a namespace for the elements in the element
        for owned_element_id in cls.__owned_elements__:
            owned_element = cls.__all_elements__[owned_element_id]
            instance = owned_element(
                owner=self,
                all_elements=all_elements,
            )()  # using the extra function call to prevent __init__ from being called
            all_elements[owned_element_id] = instance
            self.__owned_elements__.append(owned_element_id)
        return self

    @staticmethod
    def __new__(
        cls: type["Element"], *args: typing.Collection[typing.Any], **kwargs
    ) -> typing.Union["Element", typing.Callable[[], "Element"]]:
        self = cls.__create__(**kwargs)
        if owner_of(self) is None:
            for element in reversed(self.__all_elements__.values()):
                for name, value in associations_of(element).items():
                    value = self.__all_elements__[id_of(type(value))]
                    setattr(element, str(name), value)
                if element is not self:
                    element.__init__(**kwargs.pop(qualified_name_of(element), {}))
            # this is the root element of the element, so we can start initializing
            return self
        # a hack to prevent __init__ from being called
        return lambda _self=self: _self
