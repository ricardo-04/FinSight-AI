"""
Structured JSON logging.

In production (LOG_FORMAT=json or detected CI/container env) every log record is
emitted as a single-line JSON object, making it trivially parseable by log
aggregators (Datadog, CloudWatch, Loki, Splunk, etc.) without regex gymnastics.

In development (the default), the standard colorised uvicorn text format is kept
so the terminal is readable.

The formatter also injects the current OpenTelemetry trace_id and span_id into
every record when a span is active, so log lines can be correlated with Jaeger
traces automatically.

Usage: call :func:`configure_logging` once at application start, before any
loggers are used.
"""
import json
import logging
import os
import time
from typing import Any


def _otel_context() -> dict[str, str]:
    """Return trace/span IDs from the current OTel context, or empty dict."""
    try:
        from opentelemetry import trace

        span = trace.get_current_span()
        ctx = span.get_span_context()
        if ctx and ctx.is_valid:
            return {
                "trace_id": format(ctx.trace_id, "032x"),
                "span_id": format(ctx.span_id, "016x"),
            }
    except Exception:  # noqa: BLE001 - never break logging
        pass
    return {}


class _JsonFormatter(logging.Formatter):
    """Emit each log record as a single-line JSON object."""

    LEVEL_MAP = {
        logging.DEBUG: "DEBUG",
        logging.INFO: "INFO",
        logging.WARNING: "WARNING",
        logging.ERROR: "ERROR",
        logging.CRITICAL: "CRITICAL",
    }

    def format(self, record: logging.LogRecord) -> str:
        record.msg = record.getMessage()
        record.args = None

        payload: dict[str, Any] = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": self.LEVEL_MAP.get(record.levelno, record.levelname),
            "logger": record.name,
            "msg": record.getMessage(),
        }

        otel = _otel_context()
        if otel:
            payload.update(otel)

        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure root logger to JSON or text based on the LOG_FORMAT env var.

    Set ``LOG_FORMAT=json`` (or ``LOG_FORMAT=json`` is implied when running in a
    container by detecting ``CI`` or ``KUBERNETES_SERVICE_HOST`` env vars).
    """
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format = os.getenv("LOG_FORMAT", "").lower()

    # Auto-detect container/CI environments and default to JSON there.
    if not log_format:
        if os.getenv("CI") or os.getenv("KUBERNETES_SERVICE_HOST") or os.getenv("DOCKER_CONTAINER"):
            log_format = "json"
        else:
            log_format = "text"

    root = logging.getLogger()
    root.setLevel(log_level)

    # Remove handlers added by uvicorn/previous calls so we own the config.
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler()
    if log_format == "json":
        handler.setFormatter(_JsonFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)-8s %(name)s  %(message)s",
                datefmt="%H:%M:%S",
            )
        )

    root.addHandler(handler)

    # Quiet noisy third-party loggers that don't carry useful info.
    for noisy in ("httpx", "httpcore", "openai._base_client", "sqlalchemy.engine"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
