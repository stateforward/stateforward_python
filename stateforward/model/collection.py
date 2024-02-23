"""

The collection module is designed to manage collections of `Element` objects, providing a suite of functions and a base class to allow for the manipulation and iteration of these collections within an object-oriented framework. The module offers functionality to check if a given value is a collection, create collections, iterate over them, sort them, and extend them with new elements. It also defines the custom metaclass `CollectionMetaclass` and the `Collection` base class which are the core components that empower the structured management of collection elements.

Key Components:

1. `is_collection(value: typing.Any) -> bool`: A function that checks if the passed value is an instance of a collection.

2. `collection(*elements: ElementType) -> type['Collection']`: A factory function that creates a new collection type from the given elements and returns it.

3. `iter_collection(element: typing.Union[type['Collection[T]'], 'Collection[T]']) -> typing.Generator[T, None, None]`: Creates a generator to iterate over the elements of the collection.

4. `sort_collection(element: type['Collection'], key=None, reverse=False)`: Sorts the elements of a collection in-place according to the specified key function and order.

5. `extend_collection(collection_element: 'CollectionType', *elements: typing.Collection[ElementType])`: Extends the given collection with additional elements.

6. `CollectionType`: A type alias that can represent either a 'Collection' class or instance.

7. `CollectionMetaclass(type)`: A metaclass for creating 'Collection' classes with additional class-level functionality like yielding its length and providing an iterator.

8. `Collection(Element[T], metaclass=CollectionMetaclass)`: A base class representing a collection of elements, which can be iterated over, indexed, and extended while retaining the ordering of elements.

Functionality like retrieving items from a collection, checking the number of items, or iterating through every element is encapsulated within the 'Collection' class and its associated metaclass, making it a versatile tool for managing groups of objects that inherit from Element. Overall, this module aims to provide a robust framework for handling collections with ease and efficiency.
"""
import typing
from stateforward.model.element import (
    Element,
    add_association_to,
    is_subtype,
    ElementType,
)

T = typing.TypeVar("T", bound=Element)


def is_collection(value: typing.Any) -> bool:
    """
    Checks whether the given value is an instance of a Collection subtype.
    This function will return True if `value` is a subtype other than the base Collection type
    itself. It utilizes the `is_subtype` function to perform its check.
    
    Args:
        value (typing.Any):
             The value to be checked.
    
    Returns:
        bool:
             True if `value` is a subtype of Collection, False otherwise.

    """
    return is_subtype(value, (Collection,))


def collection(*elements: ElementType) -> type["Collection"]:
    """
    Creates a new collection type with the specified elements.
    This function dynamically generates a new collection type by subclassing a 'Collection' base class. The new type includes a 'length' class attribute representing the number of elements provided, and each element is added as a class attribute with the index as the key.
    The generated collection type is cast to 'ElementType' before being returned.
    
    Args:
        *elements (ElementType):
             Variable length argument list representing the elements to include in the new collection type.
    
    Returns:
        type['Collection']:
             A new collection type that includes the provided elements as attributes, along with a 'length' class attribute.

    """
    new_collection = type(
        "collection",
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
    """
    Iterates over a collection and yields its elements one by one.
    This function takes a 'Collection' object or its type and creates an
    iterator that yields each element of the collection in sequence. The
    'Collection' interface is expected to have a 'length' attribute and
    allow accessing its elements by index, with indices being string
    representations of integers starting from 0.
    
    Args:
        element:
             A 'Collection' object or its type, which is expected to
            fulfill the interface requirements mentioned above.
    
    Yields:
    
    Returns:
    
    Raises:
        AttributeError:
             If the 'Collection' object does not have a 'length'
            attribute or does not support accessing elements by index.

    """
    for index in range(element.length):
        yield getattr(element, str(index))


def sort_collection(element: type["Collection"], key=None, reverse=False):
    """
    Sorts a given collection in place based on the specified key and order.
    
    Args:
        element (type['Collection']):
             The collection instance to be sorted. The collection should have attributes accessible by string representations of indices.
        key (callable, optional):
             A function that serves as a key for the sort comparison. Defaults to None, which means that the items are sorted directly without calculating a separate key value.
        reverse (bool, optional):
             If set to True, the collection is sorted in reverse (descending) order; if False (default), the collection is sorted in ascending order.
    
    Raises:
        AttributeError:
             If the collection does not have attributes corresponding to string representations of indices, or if the attributes can't be set.

    """
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
    """
    Extends a collection with additional elements.
    This function takes a collection element and an arbitrary number of elements to be added to the collection.
    Each element is associated with the collection element using an identifier as the name of the association.
    The name of the association is determined by the current length of the collection. After adding each element,
    the length of the collection is incremented.
    
    Args:
        collection_element (CollectionType):
             The collection to be extended.
        *elements (Collection[ElementType]):
             A variable number of elements that will be added to the collection.
    
    Raises:
    
    Note:

    """
    for element in elements:
        add_association_to(collection_element, element, str(collection_element.length))
        collection_element.length += 1


CollectionType = typing.Union[type["Collection"], "Collection"]


class CollectionMetaclass(type):
    """
    A metaclass for creating collection types with a defined length.
    This metaclass allows for the creation of collection classes which support
    the len() function and iteration protocol. It provides a class-level
    attribute 'length' to denote the size of the collection, which is returned
    when __len__() is called. It also makes the collection class itself iterable
    via the __iter__() method, which is expected to be defined by instances of
    collection classes using this metaclass.
    
    Attributes:
        length (int):
             Class-level attribute specifying the number of elements
            in the collection.
    
    Methods:
        __len__(cls) -> int:
            Returns the length of the collection class.
    
    Returns:
        int:
             The number of elements in the collection.
        __iter__(cls) -> typing.Iterator[T]:
            Should return an iterator over the elements of the collection class.
    
    Returns:
        typing.Iterator[T]:
             An iterator over the collection elements.

    """

    length: int = 0

    def __len__(cls):
        """
        Computes the number of elements in the instance of the class.
        This method returns the 'length' attribute of the class instance, which should represent the number of elements it contains.
        
        Returns:
            int:
                 The number of elements in the instance.

        """
        return cls.length

    def __iter__(cls) -> typing.Iterator[T]:
        """
        Iterates over the elements of the collection class.
        This method enables the class to be iterable, allowing it to be used in for-loops
        and other contexts where an iterator is expected. It utilizes the 'iter_collection'
        function to yield elements of the collection.
        
        Returns:
            typing.Iterator[T]:
                 An iterator for the collection class that yields elements
                of type 'T'.

        """
        return iter_collection(cls)


class Collection(Element[T], metaclass=CollectionMetaclass):
    """
    A generic collection class that acts as an iterable container for elements of type T.
    This class inherits from the 'Element' class with a generic type parameter 'T' and uses a 'CollectionMetaclass'. It supports basic
    sequence protocols such as length retrieval, iteration, and item access by index. The generic type 'T' specifies the type
    of elements stored in the collection.
    
    Attributes:
        T:
             A generic type parameter specifying the type of elements in the collection.
    
    Methods:
        __len__(self) -> int:
            Returns the number of elements in the collection as per the class's 'length' attribute.
        __iter__(self) -> typing.Iterator[T]:
            Returns an iterator for the elements in the collection, making the class iterable.
        __getitem__(self, index:
             int) -> T:
            Retrieves an element from the collection by its integer index.
    
    Args:
        index (int):
             The index of the element to retrieve.
    
    Returns:
        T:
             The element at the specified index in the collection.
        __class_getitem__(cls, item):
            A class method that allows access to class attributes using subscript notion if the attribute name is numeric.
            If the attribute name is not numeric, defers to the superclass's '__class_getitem__' method.
    
    Args:
        item:
             The attribute name or a numeric string representing the attribute to access.
    
    Returns:

    """

    def __len__(self):
        """
        
        Returns the length of an object.
        
        Returns:
            int:
                 The length of the object.

        """
        return self.__class__.length

    def __iter__(self) -> typing.Iterator[T]:
        """
        Iterates over a collection instance.
        This method will return an iterator for the items in the collection by utilizing the `iter_collection` function.
        
        Returns:
            typing.Iterator[T]:
                 An iterator over the items in the collection.

        """
        return iter_collection(self)

    def __getitem__(self, index: int) -> T:
        """
        __getitem__ method
        This method overrides the default item-access ([] operator) behavior.
        The method allows accessing elements of the instance using an integer index like an array. It takes an
        integer index and returns the attribute of the instance corresponding to that index, converted to a string.
        
        Args:
            index (int):
                 An integer representing the index of the desired attribute within the instance.
        
        Returns:
            T:
                 The value of the attribute corresponding to the passed index cast to type T.
        
        Raises:
            AttributeError:
                 If the attribute corresponding to the provided index does not exist.

        """
        return getattr(self, str(index))

    def __class_getitem__(cls, item):
        """
        Gets the attribute of the class based on the provided `item`. If `item` can be converted to a number (numeric string), it tries to access the attribute with the numerical name, otherwise, it delegates the lookup to the superclass's `__class_getitem__` method.
        
        Args:
            cls (type):
                 The class on which the method is being called.
            item (Any):
                 The identifier for the class attribute, which could be a label or a numeric string that represents an integer attribute name.
        
        Returns:
            Any:
                 The value of the attribute corresponding to `item` if it's a numeric string, otherwise the result from the superclass's `__class_getitem__`.
        
        Raises:
            AttributeError:
                 If an attribute with the given numeric string as a name does not exist within the class.
            TypeError:
                 If the superclass's `__class_getitem__` does not support handling the provided `item`.

        """
        if str(item).isnumeric():
            return getattr(cls, str(item))
        return super().__class_getitem__(item)
