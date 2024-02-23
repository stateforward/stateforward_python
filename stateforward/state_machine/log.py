"""

The `log` module is designed with the functionality to provide color-coded logging messages to enhance the readability of logged information. It defines a `ColorLevelFormatter` class, which extends Python's standard `logging.Formatter` class, to enable custom formatting of log messages according to the log level. It also maintains a dictionary of loggers using `WeakValueDictionary` to avoid memory issues by reusing loggers that are already created.

## Class: ColorLevelFormatter
This custom formatter class allows setting different color codes for various log levels, making the logs visually distinguishable and easier to follow. It includes a class variable `formatters` that holds a mapping between log levels and corresponding `logging.Formatter` instances.

### Method: __init__
The constructor accepts an optional `level_color_code` parameter, which defaults to 97 (white color), and it initializes the formatter with a specific color-coded format string and a date format.

### Method: format
Override of the base `format` method from `logging.Formatter`. It checks the log record's level and applies the appropriate color formatter based on the level of the incoming log record.

## Module-level Variables
- `ColorLevelFormatter.formatters` - a dictionary mapping log levels to colored formatters for Warning, Error, and Critical levels.
- `LOGGERS` - a `WeakValueDictionary` used to store and reuse logger instances by their names.
- `stream_handler` - a logging stream handler with the `ColorLevelFormatter` set as its formatter.

## Function: create_logger
This function takes a logger name as an argument and either retrieves an existing logger from the `LOGGERS` dictionary or creates a new one. The new or existing logger is then configured with the `DEBUG` level and the `stream_handler` added to it. This function ensures that each logger with a unique name is instantiated only once and then reused, which helps optimize memory usage and application performance.

The `log` module primarily focuses on enhancing the logging messages and providing efficient handling of logger instances without comprising the application's memory footprint. Its design is particularly useful in applications requiring detailed and readable logs, such as in development, debugging, or monitoring scenarios.
"""
import logging
import typing
from weakref import WeakValueDictionary


class ColorLevelFormatter(logging.Formatter):
    """
    A custom logging formatter to add color-coded levels to log messages.
    This class is a subclass of `logging.Formatter` that provides a mechanism to color code log messages based on the log level.
    It allows the specification of custom color codes for different logging levels.
    By default, it formats the log messages with timestamps, logger names, logging levels, line numbers, and function names in colored output.

    Attributes:
        formatters (ClassVar[dict[int, logging.Formatter]]):
             A class variable that holds formatters for various logging levels.

    Args:
        level_color_code (int, optional):
             The color code to use for the log level. Defaults to 97 (white).

    Methods:
        format(record, formatter=logging.Formatter):
             Overrides the base class format method to provide custom formatting.
            It makes use of the `formatters` class variable to determine the formatter that should be used for the given record's level.
            If no custom formatter is found for the level, it defaults to using the instance's own formatting style.
            The color codes are ANSI escape codes that are used to set the text color in the terminal.
            The color coding helps in distinguishing log messages based on their severity for easy visibility and troubleshooting purposes.

    """

    formatters: typing.ClassVar[dict[int, logging.Formatter]] = {}

    def __init__(
        self,
        level_color_code: int = 97,
    ):
        """
        Initialize a new instance of the logger with a specified log level color code.
        This constructor initializes the logger with a custom format for log messages, incorporating the name,
        timestamp, log level, line number, function name, and log message. The color of the log level
        is customizable through a color code. ANSI escape codes are used to set different colors.

        Args:
            level_color_code (int, optional):
                 An integer representing the ANSI color code for the log level.
                The default color code is 97 (bright white).

        """
        super().__init__(
            f"\033[35m [%(name)s]\033[34m [%(asctime)s]\033[{level_color_code}m [%(levelname)s]\033[34m line %(lineno)s, in %(funcName)s\033[97m %(message)s\033[00m",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record, formatter=logging.Formatter):
        """
        Formats a log record using different formatters based on the log level.
        This method accepts a log record and a formatter instance and applies a
        specific formatter to the log record based on its level. If a formatter for the
        provided level is not found in the class attribute `formatters`, it uses the
        formatter passed as a parameter.

        Args:
            record (logging.LogRecord):
                 The log record to be formatted.
            formatter (logging.Formatter):
                 The default formatter to use if
                no specific formatter is found for the log level of the record.

        Returns:
            str:
                 The formatted log record string.

        """
        return formatter.format(
            ColorLevelFormatter.formatters.get(record.levelno, self), record
        )


ColorLevelFormatter.formatters = {
    logging.WARNING: ColorLevelFormatter(33),
    logging.ERROR: ColorLevelFormatter(31),
    logging.CRITICAL: ColorLevelFormatter(91),
}

LOGGERS = WeakValueDictionary()

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(ColorLevelFormatter())


def create_logger(name: str):
    """
    Creates a logger with the specified name or returns it if it already exists.
    This function checks if a logger with the given name is present in the global `LOGGERS` dictionary. If it exists, the existing logger is returned. Otherwise, a new logger is created, set to DEBUG level, and a predefined stream handler is attached to it before being added to `LOGGERS`. Finally, the new logger is returned.

    Args:
        name (str):
             The name to assign to the logger. This name is used to retrieve or create the logger.

    Returns:
        logging.Logger:
             The logger with the specified name.

    """
    if name in LOGGERS:
        return LOGGERS[name]
    logger = LOGGERS[name] = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    return logger
