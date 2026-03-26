"""Structured logging configuration.

Uses ``structlog`` when installed for structured JSON output.  Falls back
transparently to :mod:`logging` so that import-time never fails.
"""

from __future__ import annotations

import logging
from typing import Any

_CONFIGURED = False


def configure_logging(
    level: str = "INFO",
    json_output: bool = False,
) -> None:
    """Set up structured logging for the process.

    Safe to call multiple times; only the first call takes effect.

    Parameters
    ----------
    level:
        Root log level name (``DEBUG``, ``INFO``, ``WARNING``, …).
    json_output:
        When *True* and structlog is available, render events as JSON
        using ``orjson`` if present, else :mod:`json`.
    """

    global _CONFIGURED
    if _CONFIGURED:
        return
    _CONFIGURED = True

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    try:
        import structlog

        processors: list[Any] = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
        ]

        if json_output:
            try:
                import orjson

                def _orjson_dumps(data: Any, **_kw: Any) -> str:
                    return orjson.dumps(data).decode("utf-8")

                processors.append(
                    structlog.processors.JSONRenderer(serializer=_orjson_dumps)
                )
            except ImportError:
                processors.append(structlog.processors.JSONRenderer())
        else:
            processors.append(structlog.dev.ConsoleRenderer())

        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    except ImportError:
        pass

    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("transitions").setLevel(logging.WARNING)


def get_logger(name: str) -> Any:
    """Return a bound logger for *name*.

    Uses structlog if available, otherwise stdlib :func:`logging.getLogger`.
    """

    try:
        import structlog

        return structlog.get_logger(name)
    except ImportError:
        return logging.getLogger(name)
