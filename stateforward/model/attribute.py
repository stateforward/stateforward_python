from stateforward.model.element import Element, new
from typing import Any


class Attribute(Element):
    default_value: Any = None

    @classmethod
    def __define__(cls, **kwargs):
        cls.default_value = kwargs.pop("default_value", None)
        cls.attributes = {**cls.attributes, "default_value": cls.default_value}

    def __get__(self, instance, owner):
        return instance.attributes[self.name]

    def __set__(self, instance, value):
        instance.attributes[self.name] = value

    def __delete__(self, instance):
        del instance.attributes[self.name]


def attribute(default_value: Any = None):
    return new(bases=(Attribute,), default_value=default_value)
