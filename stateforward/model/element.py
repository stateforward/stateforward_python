import typing
from weakref import WeakValueDictionary
import types

ElementType = typing.TypeVar(
    "ElementType", bound=typing.Union[type["Element"], "Element"]
)
T = typing.TypeVar("T", bound="Element")


def id_of(element: ElementType) -> int:
    return getattr(element, "__id__", id(element))


def type_of(element: ElementType) -> type["Element"]:
    return element.__type__


def owned_elements_of(
    element: ElementType,
) -> typing.Generator[ElementType, None, None]:
    for owned_element_id in element.__owned_elements__:
        yield element.__all_elements__[owned_element_id]


def descendants_of(element: ElementType) -> typing.Generator[ElementType, None, None]:
    for owned_element in owned_elements_of(element):
        yield owned_element
        yield from descendants_of(owned_element)


def is_descendant_of(ancestor: ElementType, descendant: ElementType) -> bool:
    return (
        next(
            (element for element in descendants_of(ancestor) if element == descendant),
            None,
        )
        is not None
    )


def ancestors_of(element: ElementType) -> typing.Generator[ElementType, None, None]:
    owner = owner_of(element)
    if owner is not None:
        yield owner
        yield from ancestors_of(owner)


def is_ancestor_of(descendant: ElementType, ancestor: ElementType) -> bool:
    return is_descendant_of(ancestor, descendant)


def set_model(element: ElementType, model: ElementType):
    element.__model__ = id_of(model)
    for owned_element in owned_elements_of(element):
        set_model(owned_element, model)


def set_owner(element: ElementType, owner: ElementType):
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
    if not owned_elements:
        owned_elements = tuple(owned_elements_of(owner))
    removed_elements = tuple(
        remove_owned_element_from(owner, owned_element)
        for owned_element in owned_elements
    )
    return removed_elements


def add_association_to(owner: ElementType, element: ElementType, name: str = None):
    owner.__associations__[name] = id_of(element)


def remove_association_from(owner: ElementType, element: ElementType):
    for name, element in associations_of(owner).items():
        if element == element:
            del owner.__associations__[name]


def associations_of(element: ElementType) -> dict[str, ElementType]:
    return dict(
        (name, element.__all_elements__[element_id])
        for name, element_id in element.__associations__.items()
    )


def associations_for(
    element: ElementType, associated: ElementType
) -> dict[str, ElementType]:
    return dict(
        (name, element.__all_elements__[element_id])
        for name, element_id in element.__associations__.items()
        if element_id == id_of(associated)
    )


def name_of(element: ElementType) -> str:
    return element.__name__ if isinstance(element, type) else element.__class__.__name__


def attributes_of(element: ElementType) -> dict[str, typing.Any]:
    return element.__annotations__


def qualified_name_of(element: ElementType) -> str:
    owner = owner_of(element)
    if owner is None:
        return name_of(element)
    return f"{qualified_name_of(owner)}.{name_of(element)}"


def is_type(
    element: ElementType, types: typing.Union[type, typing.Collection[type]]
) -> bool:
    return (
        issubclass(element, types)
        if isinstance(element, type)
        else isinstance(element, types)
    )


def is_subtype(
    element: ElementType, types: typing.Union[type, typing.Collection[type]]
) -> bool:
    if is_element(types):
        types = (types,)
    return element not in types and is_type(element, types)


def is_element(value: typing.Any) -> bool:
    return is_type(value, Element)


def owner_of(element: ElementType) -> ElementType:
    return (
        element.__owner__
        if isinstance(element, Element)
        else element.__all_elements__.get(element.__owner__, None)
    )


def redefined_element_of(element: ElementType) -> ElementType:
    return element.__redefined_element__


def is_owner_of(owner: ElementType, element: ElementType) -> bool:
    return owner_of(element) == owner


def specialize(base: ElementType, derived: ElementType, **kwargs):
    # we have to create copies of the base elements during inheritance
    redefined_element = redefined_element_of(derived)
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
                    "redefined_element": owned_element
                    if redefined_element is not None
                    else None,
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
            for name, element_id in element.__associations__.items():
                new_element = new_elements[index]
                associated_element = new_element.__associations__[name] = element_map[
                    element_id
                ]
                setattr(new_element, name, associated_element)
    return None


def is_redefined(element: ElementType) -> bool:
    return redefined_element_of(element) is not None


def redefine(element: ElementType, **kwargs):
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
    for owned_element in owned_elements_of(element):
        if condition(owned_element):
            yield owned_element


def find_owned_element_of(
    element: "ElementType", condition: typing.Callable[["ElementType"], bool]
) -> typing.Optional["ElementType"]:
    return next(find_owned_elements_of(element, condition), None)


def find_ancestors_of(
    element: "ElementType", condition: typing.Callable[["ElementType"], bool]
) -> typing.Generator["ElementType", None, None]:
    for element in ancestors_of(element):
        if condition(element):
            yield element


def find_ancestor_of(
    element: "ElementType", expr: typing.Callable[["ElementType"], bool]
) -> typing.Optional["ElementType"]:
    return next(find_ancestors_of(element, expr), None)


def find_descendants_of(
    element: "ElementType",
    condition: typing.Callable[["ElementType"], bool],
) -> typing.Generator["ElementType", None, None]:
    for element in descendants_of(element):
        if condition(element):
            yield element


def set_attribute(
    element: ElementType,
    name: str,
    value: typing.Any,
):
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
        cls.__model__ = cls.__id__ = Element.__id__ = Element.__id__ + 1
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

    @staticmethod
    def __new__(
        cls: type["Element"], *args: typing.Collection[typing.Any], **kwargs
    ) -> typing.Union["Element", typing.Callable[[], "Element"]]:
        self = super().__new__(cls)
        owner = self.__owner__ = kwargs.pop("owner", None)
        self.__owned_elements__ = []
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
        if owner_of(self) is None:
            for element in reversed(all_elements.values()):
                for name, value in associations_of(element).items():
                    value = all_elements[id_of(value)]
                    setattr(element, str(name), value)
                if element is not self:
                    element.__init__(**kwargs.pop(qualified_name_of(element), {}))
            # this is the root element of the element, so we can start initializing
            return self
        # a hack to prevent __init__ from being called
        return lambda _self=self: _self
