"""

This module provides the `Future` class which implements a Pythonic way of handling asynchronous operations by encapsulating the result of a computation that may not be immediately available. Futures are a core component of asynchronous programming in Python, representing an abstract concept of an operation that provides a result at some point in the future.

The `Future` class provided in this module comes with various methods that allow for managing the lifecycle of a future. Here's a brief description of these methods:

- `cancel`: Attempts to cancel the future. If the future is already done or cancelled, it returns `False`; otherwise, it cancels the future and returns `True`.
- `cancelled`: Returns `True` if the future has been cancelled.
- `running`: Returns `True` if the future is currently being executed and has not been cancelled or finished yet.
- `done`: Returns `True` if the future is done executing (either the result is set, an exception has been set, or it has been cancelled).
- `add_done_callback`: Adds a callback to be run when the future is done.
- `result`: Retrieves the result of the future. If the future is not yet done, it will raise an exception or wait until the result is available or a timeout occurs.
- `exception`: Retrieves the exception set into the future, if any.
- `set_result`: Sets the result of the future. This method is typically used by the party that created the future.
- `set_exception`: Sets an exception as the result of the future. This indicates that the future has finished with an error.

The `Future` class also provides a `__await__` method, making it compatible with the `await` expression in async functions.

Furthermore, the module includes the `results` static method, which wraps a given value in a `Future` object. If the provided value is already a `Future`, it is simply cast to the module's `Future` type and returned. If it is not, a new `Future` object is created with the result already set, mimicking a completed future.

The `Future` class is a `Protocol` that describes the necessary methods and behaviors futures must implement, making it a useful tool for type hinting and ensuring that user-defined future-like classes adhere to a standard interface.
"""
import typing
import asyncio
from concurrent import futures

T = typing.TypeVar("T")
asyncio.Future


class Future(typing.Protocol[T]):
    """
    A Future represents an eventual result of an asynchronous operation. It is a placeholder for a value that will be available in the future.
    Instance methods:
    cancel(self) -> bool:
    Attempt to cancel the future. If the future is already done or cannot be cancelled, returns False; otherwise, the future is cancelled and returns True.
    cancelled(self) -> bool:
    Return True if the future has been cancelled.
    running(self) -> bool:
    Return True if the future is currently executing.
    done(self) -> bool:
    Return True if the future has finished executing.
    add_done_callback(self, callback: typing.Callable[['Future'], None]):
    Attach a callable that will be called when the future is done.
    result(self, timeout: typing.Optional[float]=None) -> T:
    Return the result of the future, if available. If the future is not done yet, wait up to a timeout and block until it is done or the timeout expires.
    exception(self, timeout: typing.Optional[float]=None):
    Return the exception raised by the call that the future represents, if any.
    set_result(self, result: T):
    Mark the future as done and set its result.
    set_exception(self, exception: Exception):
    Mark the future as done and set an exception.
    __await__(self, *args, **kwargs):
    Enable the future to be used with the await expression.
    Class methods:
    @staticmethod
    results(value: T) -> 'Future':
    Create a Future object from a given value. If the value is a future, it is cast to a Future object and returned. Otherwise, a new Future object is created, marked as done, and set to the given result.

    Attributes:
        remove_done_callback:
             typing.Optional[typing.Callable[[typing.Callable[['Future'], None]], None]]
            Attribute or function that, when present, defines how to detach a callback previously added using add_done_callback.

    """

    remove_done_callback: typing.Optional[
        typing.Callable[[typing.Callable[["Future"], None]], None]
    ]

    def cancel(self) -> bool:
        """
        Cancels an ongoing operation or process.

        Returns:
            bool:
                 True if the operation was successfully cancelled, False otherwise.

        """
        ...

    def cancelled(self) -> bool:
        """
        Checks if a given operation has been cancelled.

        Returns:
            bool:
                 True if the operation has been cancelled, otherwise False.

        """
        ...

    def running(self) -> bool:
        """
        Checks if the current object is in a running state.

        Returns:
            bool:
                 True if the object is running, False otherwise.

        """
        ...

    def done(self) -> bool:
        """
        Checks if the task is complete.

        Returns:
            bool:
                 True if the task is complete, False otherwise.

        """
        ...

    def add_done_callback(self, callback: typing.Callable[["Future"], None]):
        """
        Adds a callback function that will be called when the future is done.
        The callback provided should have a signature accepting a single argument, which will
        be the future instance itself. The callback will be invoked by the event loop or
        executor when the future is complete, and will be passed the future as its single
        argument. Note that the callbacks are not called in any specific order and should
        not make assumptions about the execution order of multiple callbacks added to the
        same future.

        Args:
            callback (Callable[['Future'], None]):
                 A callable that takes a future as its
                only parameter and returns None.

        Raises:
            Exception:
                 If adding the callback fails due to reasons such as
                future already being done or other internal errors.

        """
        ...

    def result(self, timeout: typing.Optional[float] = None) -> T:
        """

        Returns the result of an asynchronous operation after ensuring it has completed within an optional timeout period.

        Args:
            timeout (typing.Optional[float], optional):
                 Maximum time in seconds to wait for the operation to complete. If not provided, the wait is indefinite.

        Returns:
            T:
                 The result of the operation once it has completed.

        Raises:
            TimeoutError:
                 If the operation does not complete within the specified 'timeout' period.

        """
        ...

    def exception(self, timeout: typing.Optional[float] = None):
        """

        Raises an exception after a specified timeout period has elapsed.

        Args:
            timeout (typing.Optional[float], optional):
                 The number of seconds to wait before
                raising the exception. If None, the function will raise an exception
                immediately. Defaults to None.

        Raises:
            Exception:
                 An error indicating that the timeout period has elapsed.

        """
        ...

    def set_result(self, result: T):
        """
        Sets the result property of the current instance to the provided value.

        Args:
            result (T):
                 The result value to set for the current instance. The type 'T' is a
                generic placeholder indicating that the function is type-agnostic.

        Returns:

        """
        ...

    def set_exception(self, exception: Exception):
        """
        Sets an exception to be the current object's state.
        This method is typically used to indicate that an error has occurred during the execution of a task represented by the object. Once the exception is set, it can be raised or handled accordingly by the object's consumers.

        Args:
            exception (Exception):
                 The exception instance to set as the current state.

        Raises:
            TypeError:
                 If the provided argument is not an instance of the Exception class.

        """
        ...

    def __await__(self, *args, **kwargs):
        """
        __await__(self, *args, **kwargs)
        This special method is used to make an object awaitable. It should return an iterator which is then used by the
        'await' syntax in async functions. This method is typically implemented by classes that represent asynchronous operations,
        and it must return an iterator that has a '__next__' method which should stop the iteration via 'StopIteration' once the
        asynchronous operation is complete.

        Args:
            *args:
                 Variable length argument list that may be used by implementations that require additional parameters.
            **kwargs:
                 Arbitrary keyword arguments that may be used by implementations that require additional parameters.

        Raises:
            TypeError:
                 If the returned value is not an iterator.


        """
        ...

    @staticmethod
    def results(value: T) -> "Future":
        """
        Creates a completed Future object from a given value or Future.
        This static method takes any value, and if the value is already an asyncio.Future or a concurrent.futures.Future, it simply casts and returns it. If the value is not a Future instance, the method creates a new `futures.Future`, sets the provided value as the result of this Future, and returns it.

        Args:
            value (T):
                 The value to be used to create a Future object. This can be any type that can be set as the result of the Future.

        Returns:
            Future:
                 A Future object which is either cast from the input value if it was already a Future, or a new Future with the supplied value set as its result.

        """
        if asyncio.isfuture(value) or isinstance(value, futures.Future):
            return typing.cast(Future, value)
        future = futures.Future()
        future.set_result(value)
        return typing.cast(Future, future)


if __name__ == "__main__":
    foo = Future.results(1)
    print(foo.result())
