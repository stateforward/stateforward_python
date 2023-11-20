try:
    import picologging as log
except ImportError:
    import logging as log
import typing


class ColorLevelFormatter(log.Formatter):
    formatters: typing.ClassVar[dict[int, log.Formatter]] = {}

    def __init__(
        self,
        level_color_code: int = 97,
    ):
        super().__init__(
            f"\033[35m [%(name)s]\033[34m [%(asctime)s]\033[{level_color_code}m [%(levelname)s]\033[34m line %(lineno)s, in %(funcName)s\033[97m %(message)s\033[00m",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def format(self, record, formatter=log.Formatter):
        return formatter.format(
            ColorLevelFormatter.formatters.get(record.levelno, self), record
        )


ColorLevelFormatter.formatters = {
    log.WARNING: ColorLevelFormatter(33),
    log.ERROR: ColorLevelFormatter(31),
    log.CRITICAL: ColorLevelFormatter(91),
}

stream_handler = log.StreamHandler()
stream_handler.setFormatter(ColorLevelFormatter())


log.basicConfig(level=log.DEBUG, handlers=(stream_handler,))
