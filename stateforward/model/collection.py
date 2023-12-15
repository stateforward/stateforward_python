import typing
from stateforward.model.element import (
    Element,
    add_association_to,
    is_subtype,
    ElementType,
)

T = typing.TypeVar("T", bound=Element)


def is_collection(value: typing.Any) -> bool:
    return is_subtype(value, (Collection,))


def collection(*elements: ElementType) -> type["Collection"]:
    new_collection = type(
        "Collection",
        (Collection,),
        {
            "length": len(elements),
            **dict((str(index), element) for index, element in enumerate(elements)),
        },
    )

    return typing.cast(ElementType, new_collection)


def iter_collection(
    element: typing.Union[type["Collection[T]"], "Collection[T]"],
) -> typing.Generator[T, None, None]:
    for index in range(element.length):
        yield getattr(element, str(index))


def sort_collection(element: type["Collection"], key=None, reverse=False):
    sorted_elements = sorted(
        (getattr(element, str(x)) for x in range(element.length)),
        key=key,
        reverse=reverse,
    )
    for index, _element in enumerate(sorted_elements):
        setattr(element, str(index), _element)


def extend_collection(
    collection_element: "CollectionType", *elements: typing.Collection[ElementType]
):
    for element in elements:
        add_association_to(collection_element, element, str(collection_element.length))
        collection_element.length += 1


CollectionType = typing.Union[type["Collection"], "Collection"]


class CollectionMetaclass(type):
    length: int = 0

    def __len__(cls):
        return cls.length

    def __iter__(cls) -> typing.Iterator[T]:
        return iter_collection(cls)


class Collection(Element[T], metaclass=CollectionMetaclass):
    def __len__(self):
        return self.__class__.length

    def __iter__(self) -> typing.Iterator[T]:
        return iter_collection(self)

    def __getitem__(self, index: int) -> T:
        return getattr(self, str(index))

    def __class_getitem__(cls, item):
        if str(item).isnumeric():
            return getattr(cls, str(item))
        return super().__class_getitem__(item)
