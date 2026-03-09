"""Utility helpers."""

import logging


def setup_logging(debug: bool = False) -> None:
    """Configure application logging."""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def truncate_text(text: str, max_length: int = 10000) -> str:
    """Truncate text to a maximum length to prevent processing extremely large inputs."""
    if len(text) > max_length:
        return text[:max_length]
    return text
