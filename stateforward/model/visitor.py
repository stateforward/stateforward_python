"""

The `visitor` module provides a flexible framework for navigating and processing various elements within a structured model. It uses the Visitor design pattern to separate the algorithm from the elements on which it operates, allowing different kinds of operations to be performed on the elements of a model seamlessly without changing the classes of the elements themselves. Here's a detailed overview of the components within the `visitor` module:

### Classes

#### `Visitor`

The central class in the `visitor` module is `Visitor`, which serves as a base class for creating specific visitor classes that can walk through a model's structure and perform custom operations.

- `visit_method_prefix`: A class attribute that stores the prefix for visit methods. It defaults to `'visit'`, but subclasses can override it.
- `visited`: A set that keeps track of the ids of visited elements to avoid processing them multiple times.

##### Methods

- `__init_subclass__(cls, visit_method_prefix: Optional[str]=None)`: A class method that ensures the subclass adopts a custom prefix for visiting methods. It also dynamically creates visit methods if they are not already defined in the subclass.
- `__init__(self)`: Initializes the visitor instance and the set to track visited elements.
- `visit_element(self, element: Type[model.Element], *args, **kwargs)`: Visits an element and prevents revisiting already processed elements. It also dynamically dispatches to more specific visit methods based on the class of the element.
- `visit_owned_elements(self, element: Type[model.Element], *args, **kwargs)`: Iterates over and visits all elements owned by the given element.
- `visit(self, element: Type[model.Model])`: Starts the visitation process from the top-level model element.

### Constants

- `TITLE_CASE_PATTERN`: A regular expression pattern used to identify title-cased names within a string.
- `UNDERSCORE_REPLACE_PATTERN`: A pattern used for replacing characters in a string to facilitate method name generation.

- `__all__`: A list containing the names of objects intended for export from the module.

### Helper Functions

- `__get__`: An internal function facilitating the retrieval of the visitor instance in a descriptor context.

Overall, this module provides a generic mechanism for traversing and acting upon different elements within a model by using visitor classes that can be tailored to perform specific operations while maintaining loose coupling between the visitor logic and the model's structure.
"""
import re
from typing import Type, Optional
from stateforward import model

TITLE_CASE_PATTERN = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")
UNDERSCORE_REPLACE_PATTERN = r"_\1"

__all__ = ("Visitor",)


class Visitor:
    """
    A base class for implementing visitor pattern logic for traversing and processing elements in a model hierarchy.
    This class defines the basic mechanics of a visitor pattern, where subclasses can override specific visit methods to implement custom behaviors while traversing model elements. It uses a dynamic method resolution based on element types and their inheritance hierarchy to determine the appropriate visit methods to invoke.
    Subclasses can define their own visit methods with a customizable prefix by specifying the 'visit_method_prefix' attribute during subclassing. If the subclass does not define a certain prefixed visit method that exists in the base class, it will be automatically populated with a default implementation based on the Visitor's corresponding method.
    The visitor keeps track of visited elements by their unique IDs to avoid redundant processing, especially when traversing complex model structures with potential redefinitions or cyclic references.

    Attributes:
        visit_method_prefix (str):
             The prefix used for visitor methods, defaulting to 'visit' for the base class. Subclasses may override.
        visited (set[int]):
             A set that keeps track of the IDs of elements that have been visited to prevent redundant visits.

    Methods:
        __init_subclass__(cls, visit_method_prefix=None):
             Class method to handle subclass initialization by assigning a method prefix and populating missing prefixed visit methods with default logic from the base class.
        __init__():
             Initializes a new instance of Visitor, primarily responsible for initializing the 'visited' attribute.
        visit_element(element, *args, **kwargs):
             Processes an individual element and its hierarchy, marking it as visited, and calling the specific visit methods based on the element's type.
        visit_owned_elements(element, *args, **kwargs):
             Iterates over and processes all owned elements of a given element using 'visit_element'.
        visit(element):
             The entry point for visiting a model, invoking 'visit_element' on the top-level element.

    """

    visit_method_prefix: str = "visit"
    visited: set[int]

    def __init_subclass__(cls, visit_method_prefix: Optional[str] = None):
        """
        Customizes the subclass initialization process by setting a visit method prefix and providing default implementations for visitor methods if they are not already defined in the subclass.
        This modification allows different subclasses to utilize custom prefixes for their own visitor methods. During the subclass initialization, it checks whether the subclass has defined the necessary visitor methods according to a specified prefix. If such methods are not found, it dynamically creates and assigns default visitor method implementations that delegate the calls to the parent visitor methods.
        The method specifically targets visitor methods with or without '_element' and '_owned_elements' postfixes. This dynamic method creation aims to maintain consistency across various visitor implementations, ensuring that all necessary visitor interface methods are present in the subclass, regardless of the prefix chosen.

        Args:
            cls (type):
                 The class being initialized as a subclass.
            visit_method_prefix (Optional[str]):
                 An optional string to specify the prefix for the visit methods in the subclass. If not provided, it defaults to the prefix used in the base Visitor class.

        Raises:
            TypeError:
                 If the cls argument is provided, but it is not a type.

        """
        cls.visit_method_prefix = visit_method_prefix or cls.visit_method_prefix
        if cls.visit_method_prefix != Visitor.visit_method_prefix:
            for postfix in ("", "_element", "_owned_elements"):
                method_name = f"{cls.visit_method_prefix}{postfix}"
                if not hasattr(cls, method_name):

                    def visitor(
                        *args,
                        __visit__=getattr(
                            Visitor, f"{Visitor.visit_method_prefix}{postfix}"
                        ),
                        **kwargs,
                    ):
                        """
                        Handles the visitation of a node or structure using a dynamically determined visitor method.
                        This function dynamically retrieves a visitor method based on the postfix supplied, which is appended to the visit_method_prefix defined in the Visitor class. The retrieved method is then called with the provided arguments and keyword arguments.

                        Args:
                            *args:
                                 Variable length argument list to pass to the __visit__ method.
                            __visit__:
                                 The visitor method to execute, dynamically determined by appending the postfix to 'visit_method_prefix' of the Visitor class.
                            **kwargs:
                                 Arbitrary keyword arguments to pass to the __visit__ method.

                        Returns:

                        """
                        return __visit__(*args, **kwargs)

                    setattr(cls, method_name, visitor)

    def __init__(self):
        """
        Initializes a new instance of the class.
        This constructor initializes an empty set that is used to store visited elements or items.

        """
        self.visited = set()

    def visit_element(self, element: Type[model.Element], *args, **kwargs):
        """
        Visits a given element and processes it according to the visiting rules defined in the visitor.

        Args:
            element (Type[model.Element]):
                 The element to visit.
            *args:
                 Variable length argument list.
            **kwargs:
                 Arbitrary keyword arguments.
                This method processes an element by first checking if it has been redefined and if it hasn't been visited already, provided that the element has a unique identifier. It then iterates over the Method Resolution Order (MRO) of the element. For each class in the MRO, it attempts to find a corresponding method on the visitor with a name that matches the naming convention 'visit_' followed by the class name in lowercase with spaces replaced by underscores. If such a method is found and it is not the base 'visit_element' method, it invokes the method with the element and any additional arguments passed to 'visit_element'. If the method returns a truthy value, the traversal is short-circuited. Lastly, if no truthy value is returned, 'visit_owned_elements' is called to continue processing any owned elements of the current element.

        """
        qualified_name = model.qualified_name_of(element)
        element_id = model.id_of(element)
        if element_id not in self.visited:
            self.visited.add(element_id)
            for base in element.__mro__:
                method = getattr(
                    self,
                    f"{self.visit_method_prefix}_{TITLE_CASE_PATTERN.sub(UNDERSCORE_REPLACE_PATTERN, base.__name__).lower()}",
                    None,
                )
                if method not in (None, Visitor.visit_element):
                    if method(element, *args, **kwargs):
                        return
                    break
            self.visit_owned_elements(element, *args, **kwargs)

    def visit_owned_elements(self, element: Type[model.Element], *args, **kwargs):
        """
        Visits all owned elements of a given model element.
        This method iterates over all elements owned by the specified element and applies the visit_element method to each.
        It is intended to be used for traversing a hierarchy of model elements and performing operations on each owned element.
        The visit_element method called by this function should be defined elsewhere and is responsible for the actual operation performed on each element.

        Args:
            element (Type[model.Element]):
                 The root element from which owned elements will be visited.
            *args:
                 Variable length argument list for arguments to pass to visit_element method.
            **kwargs:
                 Arbitrary keyword arguments for arguments to pass to visit_element method.

        """
        for owned_element in model.owned_elements_of(element):
            self.visit_element(owned_element, *args, **kwargs)

    def visit(self, element: Type[model.Model]):
        """
        Visits a model element to perform operations on it.
        This method delegates the operation to the 'visit_element' method which needs to be implemented to perform actual actions on the model element passed to this 'visit' method.

        Args:
            element (Type[model.Model]):
                 The model element that needs to be visited. It should be an instance of a class from the 'model' module.

        """
        self.visit_element(element)
