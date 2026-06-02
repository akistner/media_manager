"""Logging setup for command-line runs."""

import logging


def configure_logging(level_name: str = "INFO") -> None:
    """Configure application logging.

    Parameters:
        level_name: Logging level name such as ``INFO``, ``WARNING``, or ``ERROR``.
    """

    level = getattr(logging, level_name.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

