from typing import Any, TypeVar, Generator, Sequence, Type, Union
from stateforward.model.decorators import instance_or_classmethod
from stateforward.model.element import (
    Element,
    new_element,
    set_attribute,
    is_subtype,
    add_owned_element,
    ElementType,
)
from stateforward.model.association import association, is_association

T = TypeVar("T")


def is_collection(value: Any) -> bool:
    """
    Check if a given value is a subtype of Collection.

    Args:
        value (Any): The value to be checked against the Collection type.

    Returns:
        bool: `True` if the value is a subtype of Collection, `False` otherwise.
    """
    return is_subtype(value, (Collection,))


class Collection(Element[T]):
    """
    A representation of a collection of Elements.

    This class inherits from `Element`, allowing collections to be first-class citizens in the
    model, just like any other element. It adds sequential collection functionality.

    Attributes:
        length (int): The number of elements in the collection.

    Methods:
        elements: Returns a generator yielding each Element in the collection.
    """

    length: int = 0

    @instance_or_classmethod
    def elements(self: "CollectionType") -> Generator["ElementType", None, None]:
        for index in range(self.length):
            yield self.attributes[index]

    def __len__(self):
        return self.length

    def __iter__(self):
        return self.elements()

    def __getitem__(self, index):
        return self.attributes[index if index >= 0 else self.length + index]


def collection(
    *elements: Sequence[ElementType],
    name: str = None,
) -> ElementType:
    """
    Create a new collection element that contains a sequence of elements.

    Args:
        *elements (Sequence[ElementType]): One or more ElementType instances to be added to the collection.
        name (str, optional): The name assigned to this collection. Defaults to None.

    Returns:
        ElementType: A new Collection instance containing the provided elements.
    """
    new_collection = new_element(
        bases=(Collection,),
        length=len(elements),
        name=name,
    )
    for index, element in enumerate(elements):
        # if not is_association(element) and element.owner is None:
        #     add_owned_element(new_collection, element)
        set_attribute(new_collection, index, element)
    return new_collection


def sort_collection(element: Type[Collection], key=None, reverse=False):
    """
    Sort the elements of the collection in place.

    Args:
        element (Type[Collection]): The Collection type to be sorted.
        key (callable, optional): A function that serves as a key for the sort comparison.
        reverse (bool, optional): If `True`, the sorted list is reversed (or sorted in descending order).
            Defaults to False.
    """
    sorted_elements = sorted(
        (element.attributes[x] for x in range(element.length)), key=key, reverse=reverse
    )
    for index, _element in enumerate(sorted_elements):
        element.attributes[index] = _element


def extend_collection(
    collection_element: Type[Collection], *elements: Sequence[ElementType]
):
    """
    Extend a collection by adding one or more new elements.

    Args:
        collection_element (Type[Collection]): The Collection to be extended.
        *elements (Sequence[ElementType]): The sequence of new elements to be added to the collection.
    """
    for element in elements:
        set_attribute(collection_element, collection_element.length, element)
        collection_element.length += 1


CollectionType = Union[Type[Collection], Collection]
