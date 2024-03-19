"""

The `element` module presented here provides a comprehensive framework for representing and manipulating a hierarchy of elements, designed to facilitate the creation and management of complex data models within a software application. It includes a rich set of functions to handle relationships and properties among elements, such as ownership and association management, type checking, element searching, and more. The module also defines an `Element` class, which serves as the base class for all elements within the hierarchy, and it is used to instantiate and define new elements with unique identities, owned elements, and various other attributes.

Key Functionalities:

- **Identities and Types**: Utilize `id_of` and `type_of` to acquire the unique identifier and type of an element, respectively.
- **Ownership Management**: Employ functions like `owned_elements_of`, `add_owned_element_to`, `remove_owned_element_from` to manage which elements are owned by others.
- **Hierarchy Navigation**: Use `ancestors_of`, `descendants_of`, `is_ancestor_of`, `is_descendant_of` to traverse and verify relationships in the hierarchy.
- **Associations Management**: Leverage `add_association_to`, `remove_association_from`, `associations_of` to manage named associations between elements.
- **Search and Filter**: Functions like `find_owned_elements_of`, `find_ancestors_of`, `find_descendants_of` to find elements based on specified conditions.
- **Redefinition and Specialization**: The `redefine` and `specialize` functions are provided to create specialized or redefined versions of existing elements.
- **Attribute Handling**: `set_attribute`, `attributes_of` allow for setting and accessing custom attributes on elements.
- **Utility Functions**: Various helper functions such as `is_type`, `is_subtype`, `is_element`, `name_of`, `qualified_name_of` support common operations needed for working with elements.

The `Element` class encapsulates common functionality needed for all elements in the model, including the initialization and management of class variables that track owned elements, associations, and other class-specific information. It also defines special class methods for defining, redefining, and creating instances of element classes.

This module offers a robust infrastructure for modeling relationships and hierarchies within complex systems and serves as a foundational tool for developers handling structured data within object-oriented paradigms.
"""
import typing
import types

ElementType = typing.TypeVar(
    "ElementType", bound=typing.Union[type["Element"], "Element"]
)
T = typing.TypeVar("T", bound="Element")


def id_of(element: ElementType) -> int:
    """
    Gets the unique identifier of a given element.
    This function retrieves a unique identifier associated with the 'element' parameter.
    If the 'element' has an '__id__' attribute, that value is returned. Otherwise, this function
    falls back to Python's built-in `id()` function to return a unique identifier.

    Args:
        element (ElementType):
             The element for which the unique identifier is to be retrieved.

    Returns:
        int:
             The unique identifier for the 'element'. If '__id__' attribute exists it is returned; otherwise, the result of `id(element)` is returned.

    """
    return getattr(element, "__id__", id(element))


def type_of(element: ElementType) -> type["Element"]:
    """
    Determines the type of a given element.
    This function takes an element of any type and returns its type.

    Args:
        element (ElementType):
             The element for which to determine the type.

    Returns:
        type[Element]:
             The type of the given element.

    """
    return element.__type__


def owned_elements_of(
    element: ElementType,
) -> typing.Generator[ElementType, None, None]:
    """
    Generates elements owned by a given element.
    The function iterates over element IDs stored in the `__owned_elements__` attribute of the provided element and yields the corresponding elements from the `__all_elements__` mapping.

    Args:
        element (ElementType):
             The element whose owned elements are to be generated.

    Returns:
        Generator[ElementType, None, None]:
             A generator that yields elements owned by the input element.

    """
    for owned_element_id in element.__owned_elements__:
        yield element.__all_elements__[owned_element_id]


def descendants_of(element: ElementType) -> typing.Generator[ElementType, None, None]:
    """
    Generates all descendants of a given element in a hierarchy.
    This generator function recursively yields all the descendants of the specified element. A descendant is defined as any element that is a direct or indirect child of the given element, at any depth level in the hierarchy. Each descendant element is yielded exactly once.

    Args:
        element (ElementType):
             The element whose descendants are to be generated.

    Yields:
        ElementType:
             The next descendant element in the hierarchy.

    """
    for owned_element in owned_elements_of(element):
        yield owned_element
        yield from descendants_of(owned_element)


def is_descendant_of(ancestor: ElementType, descendant: ElementType) -> bool:
    """
    Determines whether a specified element is a descendant of a given ancestor element.

    Args:
        ancestor (ElementType):
             The element to be considered as the ancestor.
        descendant (ElementType):
             The element to check for being a descendant.

    Returns:
        bool:
             True if the descendant is indeed a descendant of the ancestor, otherwise False.

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
    Retrieves a generator of the ancestors of a given element.
    The function yields the owner of the provided element, followed recursively by the owner of that owner, and so on. It continues to traverse the ownership hierarchy until it reaches an element that does not have an owner.

    Args:
        element (ElementType):
             The element for which to determine the ancestry.

    Returns:
        typing.Generator[ElementType, None, None]:
             A generator yielding the ancestors of the given element, in the order from the direct owner to the most distant ancestor found.

    """
    owner = owner_of(element)
    if owner is not None:
        yield owner
        yield from ancestors_of(owner)


def is_ancestor_of(descendant: ElementType, ancestor: ElementType) -> bool:
    """
    Determines if the provided ancestor element is an ancestor of the specified descendant element.

    Args:
        descendant (ElementType):
             The element that is potentially a descendant.
        ancestor (ElementType):
             The element that is potentially an ancestor.

    Returns:
        bool:
             True if the ancestor is an ancestor of the descendant, otherwise False.

    """
    return is_descendant_of(ancestor, descendant)


def set_model(element: ElementType, model: ElementType):
    """
    Sets the model attribute for a given element and propagates this setting to all elements owned by it.
    Recursively sets the '__model__' attribute of the given 'element' to the integer ID of the 'model'. It also
    applies the same setting to all elements that are considered owned by the 'element'. The 'owned_elements_of' generator is used to iterate over these owned elements.

    Args:
        element (ElementType):
             The element for which the model is being set.
        model (ElementType):
             The model element whose ID will be used to set the '__model__' attribute.

    """
    element.__model__ = id_of(model)
    for owned_element in owned_elements_of(element):
        set_model(owned_element, model)


def set_owner(element: ElementType, owner: ElementType):
    """
    Sets the owner of an element and all its owned elements to a specified owner element, then updates their model references to the model of the new owner.
    This function recursively assigns the owner's ID to the element and all of its owned
    sub-elements. It also updates the model reference for each element to match the model
    reference of the new owner. This procedure ensures a consistent ownership hierarchy and
    proper linkage to the corresponding model for each element within a given context.

    Args:
        element (ElementType):
             The element whose owner and model are to be updated.
        owner (ElementType):
             The element that will be set as the new owner.

    Returns:

    """
    element.__owner__ = id_of(owner)
    for owned_element in owned_elements_of(element):
        set_owner(owned_element, element)
    set_model(element, element.__all_elements__[owner.__model__])


def add_owned_element_to(
    owner: ElementType,
    element: ElementType,
    *,
    change_ownership: bool = False,
):
    """
    Adds an owned element to the specified owner, optionally changing the current ownership.
    This function is responsible for taking an element and adding it to the ownership structure of the given owner.
    If the element already has an owner and `change_ownership` is `False`, a `ValueError` is raised. If `True`, the current owner is disassociated before proceeding.
    The function sets the element's ownership to the given owner and appends its identifier to the owner's list of owned elements.

    Args:
        owner (ElementType):
             The entity that will own the element after the operation.
        element (ElementType):
             The element to be added to the ownership structure of the owner.
        change_ownership (bool, optional):
             A flag to indicate if the ownership should be changed if the element already has an owner. Defaults to `False`.

    Raises:
        ValueError:
             If the element already has an owner and `change_ownership` is `False`.

    Returns:

    """
    element_owner = owner_of(element)
    if element_owner is not None:
        if not change_ownership:
            raise ValueError(f"element {element.__name__} already has an owner")
        remove_owned_element_from(element_owner, element)
    set_owner(element, owner)
    owner.__owned_elements__.append(id_of(element))


def remove_owned_element_from(
    owner: ElementType, element: ElementType, *, disassociate: bool = False
) -> ElementType:
    """
    Removes an owned element from its owner and optionally disassociates related elements.

    Args:
        owner (ElementType):
             The owner object from which to remove the element.
        element (ElementType):
             The element to be removed from the owner.
        disassociate (bool, optional):
             Flag that indicates whether to disassociate the
            element from related elements. Defaults to False.

    Returns:
        ElementType:
             The element that was removed.

    Raises:
        ValueError:
             If the element is not owned by the given owner.

    """
    element_id = id_of(element)
    if owner_of(element) != owner:
        raise ValueError(f"element {element.__name__} is not owned by {owner.__name__}")
    if disassociate:
        for name, element in associations_of(element).items():
            remove_association_from(owner, element)
    owner.__owned_elements__.remove(element_id)
    element.__owner__ = None
    return element


def remove_owned_elements_from(
    owner: ElementType, *owned_elements: typing.Collection[ElementType]
) -> typing.Collection[ElementType]:
    """
    Removes a collection of owned elements from their owner object.
    This function takes an owner object, optionally followed by a collection of owned elements,
    and endeavours to remove those elements from the owner. If the collection of owned elements
    is not explicitly provided, the function first retrieves them all using an external function
    `owned_elements_of(owner)`. It iterates over these elements and removes each one individually
    by invoking `remove_owned_element_from(owner, owned_element)`. After removal, it collects and
    returns the removed elements as a tuple.

    Args:
        owner (ElementType):
             The object from which owned elements will be removed.
        *owned_elements (typing.Collection[ElementType]):
             An optional collection of owned elements to
            be removed. If not provided, all owned elements of the owner will be processed.

    Returns:
        typing.Collection[ElementType]:
             A collection (specifically a tuple) of owned elements
            that have been removed from the owner.

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
    Adds an association to an owner element with a reference to another element by its unique identifier.
    The association is recorded in the owner's `__associations__` dictionary, with the
    name as the key and the unique identifier of the element as the value.

    Args:
        owner (ElementType):
             The element that will hold the association.
        element (ElementType):
             The element to which the owner element will be associated.
        name (str, optional):
             The key under which the association is stored. If not provided,
            a default or an implicit name should be determined in other parts of the codebase.

    Raises:
        AttributeError:
             If the owner does not have an `__associations__` attribute.

    """
    owner.__associations__[name] = id_of(element)


def remove_association_from(owner: ElementType, element: ElementType):
    """
    Removes the association between two ElementType objects.
    This function iterates over the associations of the 'owner' ElementType,
    comparing each associated element to the 'element' argument. If a match is found,
    the association is removed from the 'owner' by deleting the association entry.

    Args:
        owner (ElementType):
             The ElementType object from which the association is to be removed.
        element (ElementType):
             The ElementType object which is to be disassociated from the owner.

    Returns:
        None:
             The function doesn't return anything.

    """
    for name, element in associations_of(owner).items():
        if element == element:
            del owner.__associations__[name]


def associations_of(element: ElementType) -> dict[str, ElementType]:
    """
    Retrieves the associations of a given ElementType object.
    This function takes an ElementType object and returns a dictionary where the keys are the names of the associated elements, and the values are the associated ElementType instances. It works by iterating over the element's `__associations__` attribute which contains a mapping of names to element IDs, and uses the `__all_elements__` mapping attribute of the element to obtain the actual ElementType instances.

    Args:
        element (ElementType):
             The ElementType object whose associations are to be retrieved.

    Returns:
        dict[str, ElementType]:
             A dictionary mapping names to ElementType instances representing the associations of the provided element.

    """
    return dict(
        (name, element.__all_elements__[element_id])
        for name, element_id in element.__associations__.items()
    )


def associations_for(
    element: ElementType, associated: ElementType
) -> dict[str, ElementType]:
    """
    Retrieves a dictionary of associations between two elements of specified types.
    This function searches within the given 'element's associations, identifying and
    returning associations where the associated element has the same id as
    the 'associated' element. Each matching association is stored in the dictionary
    with the association name as the key and the corresponding element as the value.

    Args:
        element (ElementType):
             The element from which associations will be searched.
        associated (ElementType):
             The element whose id is used to find matching associations.

    Returns:
        dict[str, ElementType]:
             A dictionary where each key is the name of the
            association, and each value is the `ElementType` instance associated with
            the 'associated' element's id.

    """
    return dict(
        (name, element.__all_elements__[element_id])
        for name, element_id in element.__associations__.items()
        if element_id == id_of(associated)
    )


def name_of(element: ElementType) -> str:
    """
    Gets the name of a given element.

    Args:
        element (ElementType):
             The element whose name is to be retrieved. This can be an instance or a class.

    Returns:
        str:
             The name of the element. If 'element' is a class, it returns the name of the class. If 'element' is an instance of a class, it returns the name of the instance's class.

    """
    return element.__name__ if isinstance(element, type) else element.__class__.__name__


def attributes_of(element: ElementType) -> dict[str, typing.Any]:
    """
    Retrieves the annotations of the attributes from a given ElementType object.

    Args:
        element (ElementType):
             The object whose attribute annotations we want to obtain.

    Returns:
        dict[str, typing.Any]:
             A dictionary where the keys are the names of the attributes and the values are the corresponding annotations.

    """
    return element.__annotations__


def qualified_name_of(element: ElementType) -> str:
    """
    Determines the fully qualified name of the provided `element` by traversing its ownership hierarchy.
    This function ascertains the complete dotted path name of the element starting from the top-level owner down to the element itself. This is useful for identifying elements within a nested structure with their full context.

    Args:
        element (ElementType):
             The element for which to determine the qualified name. The ElementType is
            a type that is assumed to have `__name__` and `__owner__` attributes or a way to identify its
            owner and its container.

    Returns:
        str:
             A string representing the fully qualified name of the element.
            The function first identifies the owner of the element, then recursively constructs the qualified name
            by prepending the name of the owner (if any) followed by a dot and then the name of the element itself.
            If the element does not have an owner, the function simply returns the name of the element.

    """
    owner = owner_of(element)
    if owner is None:
        return name_of(element)
    return f"{qualified_name_of(owner)}.{name_of(element)}"


def is_type(
    element: ElementType, types: typing.Union[type, typing.Collection[type]]
) -> bool:
    """
    Determines if an element is of a given type or types.
    This function checks if the provided element is either an instance of, or a subclass of,
    the given type or types. It supports checking against a single type or a collection
    of types. If multiple types are provided, the function will return True if the element
    matches any one of the types.

    Args:
        element (ElementType):
             The element to check.
        types (typing.Union[type, typing.Collection[type]]):
             A single type or a collection of types
            against which to check the element.

    Returns:
        bool:
             True if the element is an instance of one of the types or is a subclass of one
            of the types, otherwise False.

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
    Determines if a given element type is a subtype of specified types.
    This function checks if the provided `element` is not exactly one of the `types` and subsequently verifies if it is a subclass or an instance of the given `types`.

    Args:
        element (ElementType):
             The element or type to check.
        types (Union[type, Collection[type]]):
             A single type or a collection of types to compare with the `element`.

    Returns:
        bool:
             True if `element` is a subtype of any of the given `types`, otherwise False.

    Note:

    """
    if is_element(types):
        types = (types,)
    return element not in types and is_type(element, types)


def is_element(value: typing.Any) -> bool:
    """
    Determines whether a given value is an instance of the Element type or a subtype thereof.
    This function checks if the provided value is an instance of Element or any class derived from Element.

    Args:
        value (typing.Any):
             The value to be checked.

    Returns:
        bool:
             True if 'value' is an instance of Element or a derived class, otherwise False.

    """
    return is_type(value, Element)


def owner_of(element: ElementType) -> ElementType:
    """
    Determines the owner of a given element.
    The function checks if the provided 'element' is an instance of the Element type and retrieves its owner attribute. If the element is not an instance of Element, it attempts to look up the owner in the element's '__all_elements__' dictionary using the element's '__owner__' attribute as the key. The function then returns the owner of the element.

    Args:
        element (ElementType):
             The element for which the owner is to be determined.

    Returns:
        ElementType:
             The owner of the provided element. If the element is an instance of the Element type, returns the value of its __owner__ attribute. If not, returns the corresponding value from the element's '__all_elements__' dictionary for the key '__owner__'.

    Raises:
        AttributeError:
             If '__owner__' or '__all_elements__' attributes do not exist on the provided element.

    """
    return (
        element.__owner__
        if isinstance(element, Element)
        else element.__all_elements__.get(element.__owner__, None)
    )


def redefined_element_of(element: ElementType) -> ElementType:
    """
    Retrieves the redefined element from the given element object.
    This function fetches the '__redefined_element__' attribute from the element passed to it. It expects a
    predefined attribute '__redefined_element__' to be present on the 'element' which is the redefined version of the element.

    Args:
        element (ElementType):
             The element from which the redefined version will be retrieved.

    Returns:
        ElementType:
             The redefined version of the element.

    Raises:
        AttributeError:
             If the element does not have '__redefined_element__' attribute.

    """
    return element.__redefined_element__


def is_owner_of(owner: ElementType, element: ElementType) -> bool:
    """
    Determines if the provided 'owner' is the owner of the 'element'.

    Args:
        owner (ElementType):
             The potential owner whose ownership is being checked.
        element (ElementType):
             The element for which ownership is being verified.

    Returns:
        bool:
             True if 'owner' is the owner of 'element', otherwise False.

    """
    return owner_of(element) == owner


def specialize(base: ElementType, derived: ElementType, **kwargs):
    """
    Specializes the given base ElementType by deriving a new ElementType with properties and associations of the base type adjusted for the derived type.
    This function works by iterating through the owned elements of the base ElementType and creating a new owned element for each of them within the derived ElementType with redefinitions as needed. Associations within the base ElementType are also remapped to corresponding elements within the derived ElementType. If the base ElementType has no owner, a mapping is established between the base elements and the new elements, and associations are adapted accordingly.

    Args:
        base (ElementType):
             The base element type from which the new derived type will be created.
        derived (ElementType):
             The new element type that will inherit and specialize from the base type.
        **kwargs:
             Additional keyword arguments (unused).

    Returns:
        None:
             The function performs in-place specialization and does not return any value.

    """
    # we have to create copies of the base core during inheritance
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

    if owner_of(base) is None:
        base_elements = (base, *descendants_of(base))
        new_elements = (derived, *descendants_of(derived))
        element_map = dict(
            (id_of(base), id_of(derived))
            for base, derived in zip(base_elements, new_elements)
        )

        for index, element in enumerate(base_elements):
            new_element = new_elements[index]
            for name, element_id in element.__associations__.items():
                associated_id = new_element.__associations__[name] = element_map[
                    element_id
                ]
                setattr(new_element, name, new_element.__all_elements__[associated_id])
    return None


def is_redefined(element: ElementType) -> bool:
    """
    Determines if the provided element has been redefined.
    This function checks whether the element passed to it has a redefined counterpart by calling the 'redefined_element_of' function and
    inspecting if the returned value is not None.

    Args:
        element (ElementType):
             The element to check for a redefinition.

    Returns:
        bool:
             True if the element has been redefined, False otherwise.

    """
    return redefined_element_of(element) is not None


def redefine(element: ElementType, **kwargs):
    """
    Redefines an existing element by creating a new subclass with additional properties.
    The `redefine` function takes an existing class or type (referred to as `element`) and returns a new class that is a subclass of the given `element`. This subclass can incorporate additional properties that are passed to the function as keyword arguments (`**kwargs`). The original class/type is also stored as an attribute `redefined_element` in the newly created subclass.

    Args:
        element (ElementType):
             The original class or type that is to be redefined into a new subclass.
        **kwargs:
             Arbitrary keyword arguments that represent additional properties to be included in the new subclass.

    Returns:
        ElementType:
             A new subclass of the provided `element`, with added keyword arguments as attributes.

    """
    return typing.cast(
        ElementType,
        types.new_class(
            name_of(element),
            kwargs.pop("bases", (element,)),
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
    Generates elements owned by a given element that meet a specified condition.
    This generator function iterates through elements owned by the provided `element` and yields each owned element that satisfies the `condition` function. The `condition` function should take an `ElementType` as its argument and return a boolean indicating whether the element meets the desired criteria.

    Args:
        element (ElementType):
             The element whose owned elements are to be examined.
        condition (Callable[[ElementType], bool]):
             A function that takes an `ElementType` as an argument and returns True if the element satisfies the condition; otherwise, False.

    Returns:
        Generator[ElementType, None, None]:
             A generator yielding owned elements of the provided `element` that satisfy the `condition`.

    """
    for owned_element in owned_elements_of(element):
        if condition(owned_element):
            yield owned_element


def find_owned_element_of(
    element: "ElementType", condition: typing.Callable[["ElementType"], bool]
) -> typing.Optional["ElementType"]:
    """
    Finds the first element within a given element's ownership hierarchy that satisfies a specified condition.
    This function traverses the ownership structure of the provided element to locate the first child or descendant
    that meets the criteria defined by the `condition` callable. If such an element is found, it is returned;
    otherwise, the function returns `None`.

    Args:
        element (ElementType):
             The element from which the search for owned elements should begin.
        condition (Callable[[ElementType], bool]):
             A function that takes an element of type `ElementType` as a single argument
            and returns a boolean value. The function should return `True` for an element that fulfills the
            search criteria and `False` otherwise.

    Returns:
        Optional[ElementType]:
             The first element that satisfies the condition, or `None` if no matching element is found.

    """
    return next(find_owned_elements_of(element, condition), None)


def find_ancestors_of(
    element: "ElementType", condition: typing.Callable[["ElementType"], bool]
) -> typing.Generator["ElementType", None, None]:
    """
    Generates a sequence of ancestor elements of a given element that satisfy a specified condition.
    This generator function traverses the ancestor hierarchy of the provided element, testing each ancestor against a condition function.
    It yields each ancestor element that meets the criteria defined by the condition function. The traversal continues until the root of the hierarchy is reached or the generator is exhausted.

    Args:
        element (ElementType):
             The element whose ancestors are to be found.
        condition (typing.Callable[[ElementType], bool]):
             A callable that takes an element as its single argument
            and returns a boolean indicating whether the element meets the desired condition.

    Yields:
        ElementType:
             Ancestors of the initial element that satisfy the condition.

    """
    for element in ancestors_of(element):
        if condition(element):
            yield element


def find_ancestor_of(
    element: "ElementType", expr: typing.Callable[["ElementType"], bool]
) -> typing.Optional["ElementType"]:
    """
    Finds the first ancestor of a specified element that matches a given condition.

    Args:
        element (ElementType):
             The element from which to begin the search for an ancestor.
        expr (typing.Callable[['ElementType'], bool]):
             A function that takes an element as an argument and returns True if the element matches the condition, False otherwise.

    Returns:
        typing.Optional['ElementType']:
             The first ancestor element that matches the condition specified by expr. If no matching ancestor is found, returns None.

    """
    return next(find_ancestors_of(element, expr), None)


def find_descendants_of(
    element: "ElementType",
    condition: typing.Callable[["ElementType"], bool],
) -> typing.Generator["ElementType", None, None]:
    """
    Finds and yields descendants of a given element that satisfy a specified condition.
    This generator function traverses through the descendants of the provided element, checking each one
    against the given condition function. If a descendant meets the condition, it is yielded.

    Args:
        element (ElementType):
             The element whose descendants will be checked.
        condition (Callable[[ElementType], bool]):
             A function that takes an element as its argument
            and returns True if the element satisfies the condition, otherwise False.

    Yields:
        ElementType:
             The next descendant of 'element' that satisfies the 'condition'.

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
    Sets an attribute for an ElementType object with special handling for Element objects.
    This method sets an attribute on an ElementType object with the given name and value. If the value is an Element,
    additional steps are taken to manage ownership and associations. If the Element is not owned by any ElementType, or if
    it's a descendant of 'element' and it doesn't belong to a different model, it will be added to 'element's owned
    elements. Furthermore, an association between 'element' and the value is established using the name as the key.
    If the provided value is not an Element, the attribute is simply set on 'element' with the provided name and value.

    Args:
        element (ElementType):
             The ElementType object to which the attribute should be set.
        name (str):
             The name of the attribute to be set.
        value (typing.Any):
             The value to be assigned to the attribute. If an Element, ownership and
            association logic applies.

    Raises:
        ValueError:
             If the Element value is owned by a different model and is not a descendant
            of 'element', or if any ownership related issues are encountered.

    """
    if is_element(value):
        value_id = id_of(value)
        if value_id not in element.__owned_elements__:
            owner = owner_of(value)
            change_ownership = (
                owner is None or is_descendant_of(element, owner)
            ) and element.__model__ != id_of(value)
            if change_ownership:
                add_owned_element_to(element, value, change_ownership=change_ownership)
        add_association_to(element, value, name)
    setattr(element, name, value)


def new(name: str, bases: typing.Collection[type] = None, **kwargs) -> type[T]:
    """
    Creates a new class with the given name, optional base classes, and any additional keyword arguments.

    Args:
        name (str):
             The name of the new class.
        bases (typing.Collection[type], optional):
             An optional collection of base classes for the new class. Defaults to a tuple only containing Element.
        **kwargs:
             Arbitrary keyword arguments that will be included as class attributes.

    Returns:
        type[T]:
             A new class of type T that is derived from the specified base classes and includes the provided keyword arguments as class attributes.

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


P = typing.ParamSpec("P")


class Element(typing.Generic[T]):
    """
    A generic base class for modeling elements within a custom framework.
    This class serves as a template for defining various model elements by providing mechanisms to handle
    attributes, ownership, associations, and element specialization through subclassing. It implements a
    registry for all elements, associates unique identifiers, and handles element creation, definition,
    redefinition, and ownership.
    When a subclass is created, it automatically registers itself, allocates a new ID, and sets up its
    model, owner, and type information. Subclasses can further define or redefine their structure by
    providing additional attributes and owned elements via the `__define__` or `__redefine__` methods.
    The `__create__` and `__create_owned_elements__` methods are responsible for instance creation,
    and ensuring that all elements within the namespace of the created element are properly initialized.
    The constructor '__new__' is overridden to integrate this creation process and to manage the
    initialization flow of the newly created elements.

    Attributes:
        __all_elements__ (dict[int, 'Element']):
             A class attribute that acts as a registry of all
            c        reated element instances, mapped by their unique IDs.
        __id__ (int):
             A class-level unique identifier for elements.
        __owned_elements__ (list[int]):
             A list of IDs representing elements owned by this class.
        __redefined_element__ (Optional['Element']):
             An element that this class may redefine.
        __associations__ (dict[str, int]):
             A dictionary mapping association names to their respective IDs.
        __owner__ (Optional[int]):
             The ID of the owner element, if any.
        __type__ (Type['Element']):
             The type of the class, typically set to the subclass itself.
        __model__ (Optional[int]):
             The ID of the model element, if any.
        __init__ (Callable[..., None]):
             The initialization method for the element, with a default noop
            implemmentation.
        model (Optional['Element']):
             The model element associated with an instance of this class.
        Class Methods:
        __init_subclass__(cls, **kwargs):
            Automatically called when a subclass is defined, used to initialize class-level attributes
            nd register the new element.
        __define__(cls, **kwargs):
            Handles the definition of new elements by associating owned_elements and configuring the
            amespace.
        __redefine__(cls, **kwargs):
            Designed to be overridden in subclasses to handle element redefinition.
        __create__(cls, **kwargs) -> 'Element':
            Responsible for creating a new instance of the class, including initializing ownership and
            ll elements within its namespace.
        __new__(cls:
             type['Element'], *args: typing.Any, **kwargs) -> Union['Element', Callable[[], 'Element']]:
            Overrides the default object instantiation process to integrate element creation and
            nitialization management.
        __create_owned_elements__(cls, self, all_elements:
             dict[int, 'Element']):
            Instantiates owned elements and ensures they are added to the current element's namespace.

    """

    __all_elements__: dict[int, "ElementType"] = {}
    __id__: typing.ClassVar[int] = 0
    __owned_elements__: list[int] = None
    __redefined_element__: typing.Optional["Element"] = None
    __associations__: dict[str, int] = None
    __owner__: typing.Optional[int] = None
    __type__: typing.ClassVar[type["Element"]] = None
    __model__: typing.Optional[int] = None
    __init__: typing.Callable[P, None] = lambda *args, **kwargs: None
    model: typing.Optional["Element"] = None

    def __init_subclass__(cls, **kwargs):
        """
        Initializes a subclass.
        This method is called when a new subclass of the `Element` base class is created, and it
        performs essential setup for the new subclass, including assigning unique identifiers,
        establishing element relationships, and initializing annotations.

        Attributes for the subclass, such as owned elements, model associations, and type definitions, are

        Args:
            **kwargs:
                 Arbitrary keyword arguments. These can include:
            name (str):
                 The name to assign to the subclass. If not provided, the default name of the
                subclass will be used.
            redefined_element (Element):
                 An optional argument specifying an element that the subclass
                is redefining. If not provided, it is assumed this is an original definition rather than
                a redefinition.

        Raises:
            TypeError:
                 If the subclass does not properly specify the base type for an `Element`.

        """
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
        """
        Class method to define extra owned elements and attributes for an Element class based on provided keyword arguments.
        This method is used to define additional owned elements and set attributes for an Element class by processing
        keyword arguments passed to the method. Each owned element is added to the class through the
        `add_owned_element_to` function. Subsequently, the namespace is sorted to distinguish owned elements,
        orphans, and attributes. Attributes are set using the `set_attribute` function according to their respective sorted order.

        Args:
            **kwargs:
                 Arbitrary keyword arguments where the key is the attribute name or owned element, and the value is its corresponding value or owned element instance.
                The 'owned_elements' keyword argument is expected to be an iterable of owned elements that are to be added to this class.
                Any other keyword argument corresponds to an attribute or owned element of the class that will be set or added respectively based on the type of the value provided. Attributes are set directly, whereas owned elements are added using pre-defined mechanisms while respecting ownership rules.
                Sorting of the namespace involves determining the owned elements, orphan elements (elements without an owner), and attributes that need to be set on the class. This is performed by 'sort_namespace' nested function.

        """
        for owned_element in kwargs.get("owned_elements", ()):
            add_owned_element_to(cls, owned_element)

        def sort_namespace(namespace: dict[str, typing.Any]) -> dict[str, typing.Any]:
            """
            Sorts the provided namespace dictionary into a consistently ordered mapping.
            The function segregates keys based on whether they are owned, orphaned, or regular attributes.
            Elements in the namespace which are considered 'owned' are those where an owner is identifiable.
            Orphaned elements have no identifiable owner, and attributes include all other elements.
            The sorting is done based on a calculated identity for each item.

            Args:
                namespace (dict[str, typing.Any]):
                     A dictionary representing the namespace to be sorted.

            Returns:
                dict[str, typing.Any]:
                     A dictionary with keys sorted into orphans, owned, and attributes in that order.
                    The resultant dictionary contains all elements from orphans first, followed by owned elements, and then the regular attributes, each sorted by their calculated identities.

            """
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
        """
        A class method to redefine properties of the class based on provided keyword arguments.
        This method allows dynamic modification of class attributes, altering the class' behaviour
        at runtime. The kwargs dictionary should contain attribute names and their new values.

        Args:
            **kwargs:
                 Variable length keyword arguments. Each key corresponds to an attribute
                name of the class, and each value is the new value to set for that
                attribute.

        Returns:
            None:
                 This method does not return anything.

        """
        for key, item in kwargs.items():
            set_attribute(cls, key, item)
        pass

    @classmethod
    def __create__(cls, **kwargs) -> "Element":
        """
        Creates an instance of the Element class with provided keyword arguments.
        This method populates the new object's attributes, creating a namespace for the
        core in the element. The `owner` and `all_elements` attributes are set from keyword
        arguments if provided, otherwise, default values are assumed. Any elements owned by
        the instance are initialized in this method.

        Args:
            **kwargs:
                 Variable length keyword arguments.
            - 'owner' (optional):
                 The owner of the element. Defaults to None.
            - 'id' (optional):
                 The identifier for the element. Defaults to the object id.
            - 'all_elements' (optional):
                 A dictionary of all element instances keyed by their ids.
                Defaults to a dictionary with the current class's id_of as the key and `self` as the value.

        Returns:
            Element:
                 A new instance of the Element class or its subclass with initialized attributes.

        Raises:
            TypeError:
                 If super().__new__(cls) does not return an instance of cls.

        """
        self = super().__new__(cls)
        owner = self.__owner__ = kwargs.pop("owner", None)
        self.__owned_elements__ = []
        self.__id__ = kwargs.pop("id", id(self))
        self.model = typing.cast(Element, owner).model if owner is not None else self
        all_elements = self.__all_elements__ = kwargs.pop(
            "all_elements", {id_of(cls): self}
        )  # create a namespace for the core in the element
        cls.__create_owned_elements__(self, all_elements)
        return self

    @staticmethod
    def __new__(
        cls: type["Element"], *args: typing.Any, **kwargs
    ) -> typing.Union["Element", typing.Callable[[], "Element"]]:
        """
        Creates a new instance of the Element class or returns a callable that creates an instance when invoked.
        This static method is a custom constructor for creating instances of the given `Element` class or its subclasses. It uses the private `__create__` method to construct an instance with the provided keyword arguments. If the created instance does not have an owner, it iterates through all associated elements to set their attributes based on existing associations and initializes them with the corresponding kwargs.
        For the root element of the element tree, this method finalizes its creation and returns the new instance directly. If the instance being created is not the root element, this method returns a lambda function that, when called, returns the created instance without invoking the `__init__` method.

        Args:
            cls (type[Element]):
                 The class of the element to create an instance of.
            *args (typing.Any):
                 Variable length argument list, currently not utilized in the method body.
            **kwargs (typing.Any):
                 Variable keyword arguments used for initializing the instance attributes.

        Returns:
            typing.Union[Element, typing.Callable[[], Element]]:
                 An instance of the `Element` class if it is the root element, or a lambda function that returns the new instance for non-root elements.

        """
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

    @classmethod
    def __create_owned_elements__(cls, self, all_elements: dict[int, "Element"]):
        """
        Class method to instantiate and associate owned elements with a class instance.
        This method loops through the class-level collection of owned element IDs, retrieves the corresponding element from a shared class-level dictionary, instantiates it by preventing the direct call of its constructor, and finally stores the instance in a provided dictionary. This method modifies the provided dictionary in place by adding the new instances and also appends the element IDs to the instance specific owned elements list.

        Args:
            cls (type):
                 The class from which the method is called.
            self (object):
                 The instance of the class owning the new elements.
            all_elements (dict[int, 'Element']):
                 A dictionary mapping element IDs to their corresponding 'Element' instances.

        Notes:

        """
        for owned_element_id in cls.__owned_elements__:
            owned_element = cls.__all_elements__[owned_element_id]
            instance = owned_element(
                owner=self,
                all_elements=all_elements,
            )()  # using the extra function call to prevent __init__ from being called
            all_elements[owned_element_id] = instance
            self.__owned_elements__.append(owned_element_id)
