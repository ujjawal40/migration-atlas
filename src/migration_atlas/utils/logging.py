"""Logging configuration. Uses Rich for nice console output."""
from __future__ import annotations

import logging
import sys
from typing import Any

from rich.logging import RichHandler

_CONFIGURED = False


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger once. Idempotent."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    logging.basicConfig(
        level=level.upper(),
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True, markup=True, show_path=False)],
    )
    # Quiet noisy libraries
    for noisy in ("urllib3", "httpx", "httpcore", "filelock", "transformers"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a logger; configure root logging if not done yet."""
    if not _CONFIGURED:
        setup_logging()
    return logging.getLogger(name)
