"""

Module `attribute` provides a customizable `Attribute` class that can be utilized to define characteristic properties, or attributes, of a model element within various systems. Derived from the `Element` class, the `Attribute` class in this module is designed to store a default value and to be easily integrated with user-defined model elements to enhance their capabilities with additional features.

The `Attribute` class within this module primarily consists of special methods that ensure its attributes can be managed through standard attribute access and manipulation techniques. For instance, `__set__` and `__delete__` are used to handle setting and deleting of an attribute's value within an instance's attribute dictionary. The `__get__` method fetches the attribute's value from an instance's attribute dictionary.

In addition, a classmethod `__define__` is provided to handle the initial setup and configuration of a new `Attribute` class, allowing customization via keyword arguments such as `default_value`. The customization process merges any newly provided attributes with existing ones in the class definition, providing flexibility in defining the attributes and their default values.

Furthermore, the module provides a `attribute` factory function that streamlines the creation of a new `Attribute` class instance. With the capability to pass a default value through the `default_value` parameter, this function makes it efficient and straightforward to instantiate a customized `Attribute` with the desired properties.

Together, these features make the `attribute` module an integral part of developing systems where attribute management is vital, allowing seamless integration and manipulation of model element attributes within various domains.
"""
from stateforward.model.element import Element, new
from typing import Any


class Attribute(Element):
    """
    A class representing an 'Attribute' of an Element in a structured way.
    This class inherits from 'Element' and is designed to handle the attributes associated with an Element.
    It allows for storing a default value and provides class methods for defining the Attribute
    as well as instance methods to get, set, and delete the attribute for an Element instance.
    
    Attributes:
        default_value (Any):
             A class-level attribute that sets the default value of this Attribute.
            Defaults to None. This can be overridden during Attribute definition.
        Class Methods:
        __define__(cls, **kwargs):
             Accepts keyword arguments to define an 'Attribute'.
            This method allows setting the default value and initializes the attribute in the 'attributes'
            dictionary at the class level.
        Instance Methods:
        __get__(self, instance, owner):
             Descriptor method to get the value of the Attribute.
            When the Attribute is accessed as a property on an Element instance, this method retrieves
            the current value from the instance's 'attributes' dictionary, using the name of the
            Attribute as a key.
        __set__(self, instance, value):
             Descriptor method to set the value of the Attribute.
            This method sets the value of the Attribute in the instance's 'attributes' dictionary,
            allowing for the Attribute to be used as a descriptor that sets a specific value.
        __delete__(self, instance):
             Descriptor method to delete the Attribute from the Element instance.
            It removes the Attribute entry from the instance's 'attributes' dictionary.
    
    Note:

    """
    default_value: Any = None

    @classmethod
    def __define__(cls, **kwargs):
        """
        Defines class-level attributes with specified keyword arguments.
        This method allows for dynamic definition or modification of class-level attributes based on
        keyword arguments provided. The 'default_value' keyword argument is specifically extracted and
        used to set a 'default_value' attribute. Any remaining keyword arguments are merged with the
        current class attributes.
        
        Args:
            cls (type):
                 The class on which the method is called.
            **kwargs:
                 Arbitrary keyword arguments. Specifically looks for 'default_value' to set as
                class attribute and merges any additional arguments with existing class attributes.

        """
        cls.default_value = kwargs.pop("default_value", None)
        cls.attributes = {**cls.attributes, "default_value": cls.default_value}

    def __get__(self, instance, owner):
        """
        Gets the value of the attribute with the name of this descriptor from the instance's attributes dictionary.
        
        Args:
            instance (object):
                 The instance from which the attribute value is to be fetched.
            owner (type):
                 The class owning the attribute (unused in this implementation).
        
        Returns:
        
        Raises:
            KeyError:
                 If the attribute with the descriptor's name is not found within the instance's attributes dictionary.

        """
        return instance.attributes[self.name]

    def __set__(self, instance, value):
        """
        __set__ is a special method that is called to assign a value 'value' to the attribute 'self.name' of an 'instance'. This method is typically used within a descriptor class to manage how the attribute of an instance is set. It alters the 'instance' dictionary of attributes by adding or updating the key-value pair, where the key is the descriptor's name and the value is the new value assigned to that key.
        
        Args:
            self:
                 A reference to the descriptor instance.
            instance:
                 The object instance in which the attribute should be set.
            value:
                 The value to be set to the instance's attribute.
        
        Raises:
            TypeError:
                 If 'instance' is not an instance of the expected type (not enforced in this snippet but could be a consideration for implementation).
            ValueError:
                 If 'value' is not an acceptable value for the instance's attribute (also not enforced here but could be relevant depending on context).

        """
        instance.attributes[self.name] = value

    def __delete__(self, instance):
        """
        __delete__(self, instance)
        Deletes an attribute from the given instance based on the descriptor's name.
        This magic method is called when `del obj.attribute` is executed for an object. It uses the descriptor's name to find and delete the attribute from the `attributes` dictionary of the instance.
        
        Args:
            instance (object):
                 The object instance from which the attribute should be deleted.
        
        Raises:
            AttributeError:
                 If the attribute does not exist in the instance's attributes.

        """
        del instance.attributes[self.name]


def attribute(default_value: Any = None):
    """
    Creates a new attribute with a specified default value.
    
    Args:
        default_value (Any, optional):
             The default value for the attribute.
    
    Returns:

    """
    return new(bases=(Attribute,), default_value=default_value)
