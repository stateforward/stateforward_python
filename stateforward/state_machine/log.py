import logging
import typing
from weakref import WeakValueDictionary


class ColorLevelFormatter(logging.Formatter):
    formatters: typing.ClassVar[dict[int, logging.Formatter]] = {}

    def __init__(
        self,
        level_color_code: int = 97,
    ):
        super().__init__(
            f"\033[35m [%(name)s]\033[34m [%(asctime)s]\033[{level_color_code}m [%(levelname)s]\033[34m line %(lineno)s, in %(funcName)s\033[97m %(message)s\033[00m",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record, formatter=logging.Formatter):
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
    if name in LOGGERS:
        return LOGGERS[name]
    logger = LOGGERS[name] = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(stream_handler)
    return logger
