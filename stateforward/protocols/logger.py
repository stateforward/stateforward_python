import typing

# TODO add typing for logger


class Logger(typing.Protocol):
    def setLevel(self, level):
        ...

    def debug(self, msg, *args, **kwargs):
        ...

    def info(self, msg, *args, **kwargs):
        ...

    def warning(self, msg, *args, **kwargs):
        ...

    def error(self, msg, *args, **kwargs):
        ...

    def exception(self, msg, *args, exc_info=True, **kwargs):
        ...

    def critical(self, msg, *args, **kwargs):
        ...

    def fatal(self, msg, *args, **kwargs):
        ...

    def log(self, level, msg, *args, **kwargs):
        ...
