import re
from typing import Type, Optional
from stateforward import model

TITLE_CASE_PATTERN = re.compile("((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))")
UNDERSCORE_REPLACE_PATTERN = r"_\1"

__all__ = ("Visitor",)


class Visitor:
    visit_method_prefix: str = "visit"

    def __init_subclass__(cls, visit_method_prefix: Optional[str] = None):
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
                        return __visit__(*args, **kwargs)

                    setattr(cls, method_name, visitor)

    def __init__(self):
        self.visited = set()

    def visit_element(self, element: Type[model.Element], *args, **kwargs):
        if (
            not model.is_redefined(element)
            and element.qualified_name not in self.visited
        ):
            self.visited.add(element.qualified_name)
            for base in element.__mro__:
                method = getattr(
                    self,
                    f"{self.visit_method_prefix}_{TITLE_CASE_PATTERN.sub(UNDERSCORE_REPLACE_PATTERN, base.__name__).lower()}",
                    None,
                )
                if method not in (None, Visitor.visit_element):
                    if method(element.type, *args, **kwargs):
                        return
                    break
            self.visit_owned_elements(element.type, *args, **kwargs)

    def visit_owned_elements(self, element: Type[model.Element], *args, **kwargs):
        for owned_element in element.owned_elements:
            self.visit_element(owned_element, *args, **kwargs)

    def visit(self, element: Type[model.Model]):
        self.visit_element(element)
