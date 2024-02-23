"""

The `cursor` module defines the `Cursor` class, which is a subclass of the built-in list type with additional functionality for managing text content with indentation levels. The class facilitates structured text generation with auto-indentation, particularly useful for code generation or formatting output where hierarchical representation is needed.

The `Cursor` class can contain both strings and other `Cursor` instances, allowing for nested structures. This design pattern is beneficial when dealing with text blocks at various indentation levels, such as in code files with nested scopes or structured documents.

### Class `Cursor`

#### Initialization

- `__init__(self, *data, indent: int=0)`
  Constructor for creating a `Cursor` instance. Accepts variable data items and an optional `indent` parameter which sets the initial indentation level.

#### Methods

- `__str__(self)`
  Overrides the string representation to output the contents with proper indentation applied to each line, considering the `indent` level of the `Cursor`.

- `auto_indent(self, indent: int=2)`
  Returns a context manager that yields a new `Cursor` with increased indentation. When the context manager exits, the original indentation level is restored.

- `extend(self, *items: Union[str, 'Cursor'])`
  Extends the current `Cursor` instance by appending multiple items, which can be strings or other `Cursor` instances, allowing for incremental building of content.

The `Cursor` class is designed with simplicity and flexibility in mind, aiming to ease the manipulation of hierarchically structured text through intuitive methods and context management.
"""
from typing import Union
from contextlib import contextmanager


class Cursor(list[Union[str, "Cursor"]]):
    """
    A custom list-like class for maintaining text with an indentation level.
    This class extends `list` to manage strings and other `Cursor` instances with
    the capability to present them as a single string with proper indentation. The
    class can be used to build text content hierarchically with different
    indentation levels, allowing for easier generation of structured text documents,
    such as code or configuration files.
    
    Attributes:
        indent (int):
             The number of spaces used for the indentation level of this
            `Cursor` instance.
    
    Methods:
        __init__(*data, indent=0):
            Initializes a new `Cursor` instance with optional content and an
            indentation level.
    
    Args:
        *data:
             A variable number of string or `Cursor` instances to initialize
            the `Cursor` list with.
        indent (int, optional):
             The initial indentation level. Defaults to 0.
        __str__():
            Returns a string representation of the `Cursor` content, with each element
            rendered on a new line and properly indented.
    
    Returns:
        str:
             The string representation of the `Cursor` with applied indentation.
        auto_indent(indent=2):
            A context manager that returns a new `Cursor` instance indented relative
            to the current indentation level.
    
    Args:
        indent (int, optional):
             The additional indentation to apply to the new
            `Cursor` instance within the context. Defaults to 2.
    
    Yields:
        Cursor:
             A new `Cursor` instance with increased indentation.
    
    Returns:
        Cursor:
             The same `Cursor` instance that was yielded, for use after the
            context block exits.
        extend(*items):
            Extends the `Cursor` with additional strings or `Cursor` instances.
    
    Args:
        *items:
             A variable number of strings or `Cursor` instances to add to
            the `Cursor`.

    """

    def __init__(self, *data, indent: int = 0):
        """
        Initialize a new instance of the class.
        This constructor initializes a new instance with provided data and an indentation level.
        It also calls the superclass' constructor.
        
        Args:
            *data (variable):
                 Variable length argument list representing data to initialize the instance with.
            indent (int, optional):
                 The indentation level for the instance. Defaults to 0 if not provided.

        """
        super().__init__(data)
        self.indent = indent

    def __str__(self):
        """
        __str__(self)
        Creates a string representation of a list-like object with custom indentation.
        This method generates a string where each item of the object is converted to a string and joined by a space. The composite string is then split by line breaks ('
        '), and each resulting line is prefixed with a number of spaces defined by the object's 'indent' attribute.
        
        Returns:
            str:
                 The formatted string representation of the object.

        """
        content = " ".join(str(item) for item in self)
        return "\n".join(f"{' ' * self.indent}{line}" for line in content.split("\n"))

    @contextmanager
    def auto_indent(self, indent: int = 2):
        """
        Context manager that creates a new Cursor instance with increased indentation.
        The method generates a new Cursor object with an indent level higher than the current object by the specified amount. It appends this new Cursor to the current Cursor instance, and upon exiting the context, it returns the formatted Cursor, preserving the indentation structure. This is useful for creating nested structures with proper indentation in text-based representations.
        
        Args:
            indent (int):
                 The amount of indentation to add to the current indent level. Defaults to 2.
        
        Yields:
            Cursor:
                 A new Cursor instance with increased indentation that can be used within the context.
        
        Returns:
            Cursor:
                 The same Cursor instance yielded, after the context execution finishes.

        """
        formatted = Cursor(indent=self.indent + indent)
        self.append(formatted)
        try:
            yield formatted
        finally:
            return formatted

    def extend(self, *items: Union[str, "Cursor"]):
        """
        Extends the current collection with additional items.
        This method takes a variable number of arguments, each of which can either be a string or an instance of the 'Cursor' class, and adds them to the existing collection by calling the 'extend' method of the superclass.
        
        Args:
            *items (Union[str, 'Cursor']):
                 A variable number of arguments where each one is either a string or a 'Cursor' instance to be added to the collection.

        """
        super().extend(items)
