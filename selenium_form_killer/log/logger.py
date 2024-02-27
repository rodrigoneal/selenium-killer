from sys import stderr

from loguru import logger


def get_logger(verbose=True):
        logger.remove()
        logger.add("killer.log",
                   format="{time:DD-MM-YYYY at HH:mm:ss} | {name}:{function} | {level} | {message}",
                   rotation="25 MB",
                   level="DEBUG",
                   backtrace=False,
                   diagnose=True)
        if verbose:
            logger.add(sink=stderr,
                    format="{time:DD-MM-YYYY at HH:mm:ss} | {name}:{function} | {level} | {message}",
                    level="DEBUG",
                    backtrace=True,
                    diagnose=True,
                    colorize=True
                    )
        return logger