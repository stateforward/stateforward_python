"""
# Mock

This was hacked together to provide a simple mocking interface for testing stateforward models. It's not very good, but it works for now.
"""

from unittest.mock import AsyncMock as _AsyncMock, Mock
import stateforward as sf
from typing import Callable, Union, Generic, TypeVar, Sequence, Type
import asyncio

T = TypeVar("T")


class MockedElement(sf.Element):
    pass


def mocked_behavior(name: str):
    return sf.new(name, bases=(sf.Behavior,), activity=Mock(name=name))


def mocked_constraint(name: str):
    return sf.new(name, bases=(sf.Constraint,), condition=Mock(name=name))


def mock(model: sf.Model):
    mocked_model = MockedModel(model)
    for element in sf.descendants_of(model):
        if isinstance(element, sf.CallEvent):
            element.operation = Mock(
                side_effect=element.operation, name=sf.qualified_name_of(element)
            )
            mocked_model.__mocked__.add(element.operation)
        elif isinstance(element, sf.Behavior):
            element.activity = _AsyncMock(
                side_effect=element.activity, name=sf.qualified_name_of(element)
            )
            mocked_model.__mocked__.add(element.activity)
        elif isinstance(element, sf.Constraint):
            element.condition = _AsyncMock(
                side_effect=element.condition, name=sf.qualified_name_of(element)
            )
            mocked_model.__mocked__.add(element.condition)
        elif isinstance(element, sf.Transition):
            if element.effect is None:
                effect = mocked_behavior("effect")
                sf.set_attribute(element, "effect", effect)
                mocked_model.__mocked__.add(effect.activity)
    return mocked_model


class Mocked(Generic[T]):
    __element_type__: type[T] = sf.Element
    __slots__ = ("__element__", "__mocked__")

    def __init_subclass__(cls, element: Type[T] = None):
        cls.__element_type__ = element

    def __init__(self, element: T, all_mocked_elements: Sequence[Mock] = ()):
        self.__element__ = element
        self.__mocked__ = set(all_mocked_elements)

    def future(self):
        future = self.__element__.model.interpreter.stack.get(self.__element__)
        if future is None:
            future = asyncio.Future()
            future.set_result(None)
        return future

    def is_active(self, *elements) -> bool:
        return self.__element__.model.interpreter.is_active(self.__element__)

    def is_inactive(self) -> bool:
        return not self.is_active()

    def __getattr__(self, item):
        if item in super().__getattribute__("__slots__"):
            return super().__getattribute__(item)
        value = super().__getattribute__("__element__").__getattribute__(item)
        return (
            mocked(value, self.__mocked__)
            if isinstance(value, sf.Element) and not isinstance(value, sf.Interpreter)
            else value
        )

    def __getitem__(self, item):
        return mocked(self.__element__[item], self.__mocked__)

    def reset_mocked(self):
        for _mocked in self.__mocked__:
            _mocked.reset_mock()


class MockedCallEvent(Mocked[sf.CallEvent], element=sf.CallEvent):
    def __call__(self, *args, **kwargs):
        self.reset_mocked()
        return self.__element__(*args, **kwargs)


class MockedModel(Mocked[sf.Model], element=sf.Model):
    async def dispatch(self, event: sf.Event):
        self.reset_mocked()
        await sf.send(event, self.__element__)


class MockedBehavior(Mocked, element=sf.Behavior):
    def is_done(self) -> bool:
        return self.is_started() and self.future().done()

    def is_started(self) -> bool:
        return self.activity.call_count == 1

    def was_terminated(self) -> bool:
        if self.activity.call_count < 1:
            return False
        elif self.is_active():
            return self.future().cancelled() or self.future().done()
        return True


class MockedState(Mocked, element=sf.State):
    def was_entered(self) -> bool:
        return (
            self.is_active() and self.entry.is_done() and self.do_activity.is_started()
        )

    def is_entered(self) -> bool:
        return self.was_entered() and not self.was_exited()

    def was_not_entered(self) -> bool:
        if not self.entry.is_inactive():
            return False
        elif not self.do_activity.is_inactive():
            return False
        return self.is_inactive()

    def was_not_exited(self) -> bool:
        return (
            self.do_activity.is_started()
            and self.exit.is_inactive()
            and self.is_active()
        ) and self

    def was_exited(self) -> bool:
        return self.exit.is_done() and self.is_inactive()


class MockedConstraint(Mocked, element=sf.Constraint):
    def was_evaluated(self) -> bool:
        return self.is_active and self.future().done()

    def was_not_evaluated(self) -> bool:
        return self.is_active() and not self.future().done()

    def evaluated_to(self, value: bool) -> bool:
        return self.was_evaluated() and self.future().result() == value


class MockedTransition(Mocked, element=sf.Transition):
    def was_executed(self):
        return (
            self.effect.is_started()
            and self.effect.is_done()
            and (self.guard is None or self.guard.was_evaluated())
        )


def mocked(
    element: sf.ElementType,
    all_mocked_elements: Sequence[Mock] = (),
) -> Union[Mocked, MockedState, MockedTransition, MockedConstraint, MockedBehavior]:
    if isinstance(element, sf.State):
        return MockedState(element, all_mocked_elements)
    elif isinstance(element, sf.Transition):
        return MockedTransition(element, all_mocked_elements)
    elif isinstance(element, sf.Constraint):
        return MockedConstraint(element, all_mocked_elements)
    elif isinstance(element, sf.Behavior):
        return MockedBehavior(element, all_mocked_elements)
    elif isinstance(element, sf.CallEvent):
        return MockedCallEvent(element, all_mocked_elements)

    return Mocked(element)


class Expect:
    def __init__(
        self,
        include: Sequence[Mocked] = (),
        exclude: Sequence[Mocked] = (),
        apply: Callable = all,
    ):
        self.include = include
        self.exclude = exclude
        self.apply = apply

    def __getattr__(self, item):
        def apply(_self=self, _item=item):
            # includes = [getattr(element, _item)() for element in _self.include]
            for element in _self.include:
                assert getattr(
                    element, _item
                )(), f"{sf.qualified_name_of(element.__element__)}.{_item}() assertion failed"
            for element in _self.exclude:
                assert not getattr(
                    element, _item
                )(), f"not {sf.qualified_name_of(element.__element__)}.{_item}() assertion failed"

        return Expect(self.include, self.exclude, apply=apply)

    def __call__(self, *args, **kwargs):
        return self.apply(*args, **kwargs)

    def all(self, element: Mocked, *elements: Sequence[Mocked]):
        return Expect(include=(element, *elements), apply=all)

    def only(self, element: Mocked, *elements: Sequence[Mocked]):
        include = tuple(_element.__element__ for _element in (element, *elements))

        return Expect(
            include=(element, *elements),
            exclude=tuple(
                mocked(_element)
                for _element in sf.descendants_of(element.__element__.model)
                if sf.element.is_subtype(_element, element.__element_type__)
                and _element not in include
            ),
        )


expect = Expect()
