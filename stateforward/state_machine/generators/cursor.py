from typing import Union
from contextlib import contextmanager


class Cursor(list[Union[str, "Cursor"]]):
    def __init__(self, *data, indent: int = 0):
        super().__init__(data)
        self.indent = indent

    def __str__(self):
        content = " ".join(str(item) for item in self)
        return "\n".join(f"{' ' * self.indent}{line}" for line in content.split("\n"))

    @contextmanager
    def auto_indent(self, indent: int = 2):
        formatted = Cursor(indent=self.indent + indent)
        self.append(formatted)
        try:
            yield formatted
        finally:
            return formatted

    def extend(self, *items: Union[str, "Cursor"]):
        super().extend(items)
