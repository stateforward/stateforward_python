"""

Module `logger` defines an interface for logging functionality, modeled as a Protocol class in Python typing system, which can be implemented by logging providers for consistent logging behavior across different applications.

## Class `Logger`

This abstract base class defines several methods for logging messages at different severity levels. It does not contain any implementations but serves as a contract that other logging classes can follow to ensure compatibility with the expected logging interface.

### Methods

- `setLevel(self, level)`: Set the threshold for this logger to `level`. Logging messages which are less severe than `level` will be ignored.

- `debug(self, msg, *args, **kwargs)`: Log a message with severity 'DEBUG' on this logger.

- `info(self, msg, *args, **kwargs)`: Log a message with severity 'INFO' on this logger.

- `warning(self, msg, *args, **kwargs)`: Log a message with severity 'WARNING' on this logger.

- `error(self, msg, *args, **kwargs)`: Log a message with severity 'ERROR' on this logger.

- `exception(self, msg, *args, exc_info=True, **kwargs)`: Log a message with severity 'ERROR' as well as exception information on this logger. By default, `exc_info` is `True`.

- `critical(self, msg, *args, **kwargs)`: Log a message with severity 'CRITICAL' on this logger.

- `fatal(self, msg, *args, **kwargs)`: An alias for `critical` to log a message with 'FATAL' severity level indicating a potentially program-halting issue.

- `log(self, level, msg, *args, **kwargs)`: Log a message with the specified logging `level` on this logger. This is more generic and can be used for any logging level.

The `*args` and `**kwargs` in the method signatures represent variadic positional and keyword arguments respectively, which can be used to pass additional context or formatting information to the logging methods.

Note: This module serves as a protocol and will need concrete implementations provided by classes that fulfill the interface defined by the `Logger` class.
"""
import typing

# TODO add typing for logger


class Logger(typing.Protocol):
    """
    A protocol defining the interface for a logging system.
    This Logger protocol specifies the methods that a logger must implement to be considered a conforming implementation. It provides a way to log messages with different severity levels. Implementations of this protocol can be used to log debug, information, warning, error, exception, and critical level messages.
    
    Methods:
        setLevel(level):
             Set the threshold for this logger to level. Logging messages which are less severe than level will be ignored.
        debug(msg, *args, **kwargs):
             Log 'msg % args' with the severity 'DEBUG'.
        info(msg, *args, **kwargs):
             Log 'msg % args' with the severity 'INFO'.
        warning(msg, *args, **kwargs):
             Log 'msg % args' with the severity 'WARNING'.
        error(msg, *args, **kwargs):
             Log 'msg % args' with the severity 'ERROR'.
        exception(msg, *args, exc_info=True, **kwargs):
             Log 'msg % args' with the severity 'ERROR', including an exception traceback (exceptions only).
        critical(msg, *args, **kwargs):
             Log 'msg % args' with the severity 'CRITICAL'.
        fatal(msg, *args, **kwargs):
             Log 'msg % args' with the severity 'CRITICAL' (synonym for critical).
        log(level, msg, *args, **kwargs):
             Log 'msg % args' with the severity 'level'.
            The '*args' and '**kwargs' are to be used for string formatting of the message and passing extra parameters specific to the logging system implementation, respectively.

    """
    def setLevel(self, level):
        """
        Sets the logging level of the object.
        
        Args:
            level (int):
                 An integer representing the logging level to set.

        """
        ...

    def debug(self, msg, *args, **kwargs):
        """
        Logs a debug message to the console or a file, if configured.
        
        Args:
            msg (str):
                 The message to be logged.
            *args:
                 Variable length argument list that may be used to pass in objects for
                formatting the message.
            **kwargs:
                 Arbitrary keyword arguments that may be used for providing
                additional information to fine-tune the logging behavior.

        """
        ...

    def info(self, msg, *args, **kwargs):
        """
        Logs an informational message to the console or designated log handler.
        This method logs a message with an 'INFO' level. The args provided are
        used to format the msg string using the standard string formatting
        operator. Additional kwargs are passed to the underlying logging
        handler and can control various aspects of the logging process such as
        the stack info and the exception information.
        
        Args:
            msg (str):
                 The message format string to log.
            *args:
                 Variable length argument list used for string formatting.
            **kwargs:
                 Arbitrary keyword arguments.
        
        Returns:

        """
        ...

    def warning(self, msg, *args, **kwargs):
        """
        Logs a warning message with optional arguments supporting variable data insertion.
        
        Args:
            msg (str):
                 The warning message to log. This message can contain format strings which will be replaced by data from `args`.
            *args:
                 Variable length argument list used to insert data into the `msg` format string.
            **kwargs:
                 Arbitrary keyword arguments. These arguments can be used to pass additional data relevant to the logging system, such as context or error codes.

        """
        ...

    def error(self, msg, *args, **kwargs):
        """
        Logs an error message with additional context provided by arguments.
        This method is used to log error level messages. The message can be
        formatted with additional arguments and keyword arguments to provide
        context for the error. It is especially useful in a logging system where
        the error message, along with its context, is recorded or reported.
        
        Args:
            msg (str):
                 The error message to log. This should be a clear and concise
                description of the error.
            *args:
                 Variable length argument list used to format the msg.
            **kwargs:
                 Arbitrary keyword arguments which can be used to provide
                additional information for formatting the error message.
        
        Returns:

        """
        ...

    def exception(self, msg, *args, exc_info=True, **kwargs):
        """
        Logs an exception message along with the traceback information, if exc_info is True.
        
        Args:
            msg (str):
                 A human-readable message describing the exception.
            *args:
                 Variable length argument list that may be used by the logging formatter.
            exc_info (bool, optional):
                 Determines whether to log exception traceback information. Defaults to True.
            **kwargs:
                 Arbitrary keyword arguments which may be passed to the logger.

        """
        ...

    def critical(self, msg, *args, **kwargs):
        """
        Logs a message with level 'CRITICAL' on this logger.
        The message 'msg' is logged on the logger with the integer level CRITICAL. The arguments are interpreted as for fmt.format(). Exception information is added to the logging message if the 'exc_info' keyword argument is set to a true value. If an exception tuple (in the format returned by sys.exc_info()) or an exception instance is provided as 'exc_info', it is used; otherwise, sys.exc_info() is called to get the exception information.
        
        Args:
            msg (str):
                 The message format string to log.
            *args:
                 Variable length argument list to pass to the message format string.
            **kwargs:
                 Arbitrary keyword arguments. Commonly used keyword arguments are 'exc_info' to add exception information to the message, and 'extra' which is used to pass additional information for the logger to emit with the message.
        
        Returns:

        """
        ...

    def fatal(self, msg, *args, **kwargs):
        """
        Logs a message with severity 'FATAL' on the logger instance, then exits the program with a non-zero exit code. The message can be a string message or a string with placeholders for variable content, with args providing the variable content to fill in the placeholders. The kwargs can be used to customize the logging behavior (e.g., exception information, stack information, etc.).
        
        Args:
            msg (str):
                 The message to log or a format string containing placeholders for variable content.
            *args:
                 Variable length argument list to fill in the placeholders within the msg, if any.
            **kwargs:
                 Arbitrary keyword arguments passed to the underlying logging function.
        
        Returns:
            None:
                 This function does not return as it exits the process after logging.
        
        Raises:
            SystemExit:
                 The process will exit with a non-zero exit code after logging the fatal message.

        """
        ...

    def log(self, level, msg, *args, **kwargs):
        """
        Logs a message with the given level on this logger.
        The message is formatted using the provided positional and keyword arguments. The level corresponds to the
        severity of the message and should be an integer representing a standard logging level (e.g., logging.DEBUG,
        logging.INFO, etc.).
        
        Args:
            level (int):
                 An integer representing the logging level indicating the severity of the
                message. For example, logging.DEBUG, logging.INFO, etc.
            msg (str):
                 The message format string to log. This will be merged with args and kwargs to
                produce the final message string.
            *args:
                 Variable length argument list that is merged with msg using str.format() to create
                the final message string.
            **kwargs:
                 Arbitrary keyword arguments that are used for advanced formatting when merging with msg.
        
        Returns:
        
        Raises:
            ValueError:
                 If the message formatting fails due to improper args or kwargs.

        """
        ...
