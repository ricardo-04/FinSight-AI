import logging
import os

from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)

_OTEL_ENDPOINT = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "")


def setup_telemetry(app):
    provider = TracerProvider()

    if _OTEL_ENDPOINT:
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
                OTLPSpanExporter,
            )
            provider.add_span_processor(
                BatchSpanProcessor(OTLPSpanExporter(endpoint=_OTEL_ENDPOINT))
            )
            logger.info("OTEL tracing enabled: endpoint=%s", _OTEL_ENDPOINT)
        except Exception as e:
            logger.warning("Failed to configure OTEL exporter: %s", e)
    else:
        logger.info("OTEL tracing disabled (no OTEL_EXPORTER_OTLP_ENDPOINT set)")

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app)
