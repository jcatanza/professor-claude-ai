"""Structured logging configuration.

Uses structlog for JSON-formatted logs in production and human-readable logs
in development. Stdlib logging is wired through structlog so third-party
library logs (langgraph, anthropic, arxiv) get the same treatment.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog


def configure_logging(*, dev: bool = False, level: int = logging.INFO) -> None:
    """Configure structlog + stdlib logging.

    dev=True gives a colored console renderer; dev=False (default) gives JSON.
    """
    timestamper = structlog.processors.TimeStamper(fmt="iso")

    shared_processors: list[Any] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        timestamper,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer = structlog.dev.ConsoleRenderer() if dev else structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[*shared_processors, renderer],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Wire stdlib logging through too
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
