"""Logging Functions

Used in other modules as:
   log = logger.get_logger(__name__)

"""

import logging


def get_logger(name: str):
    """Returns a simple logger.

    Args:
        name (str): module name (__name__)

    Returns:
        Logger:  logging instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    logger.addHandler(ch)

    return logger
