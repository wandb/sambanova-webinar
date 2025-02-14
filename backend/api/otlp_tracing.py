import logging

from opentelemetry import metrics, trace

# Logging (Experimental)
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


def configure_logger():
    logger = logging.getLogger("Co_Pilot")
    logger.setLevel(logging.INFO)

    # Remove all existing handlers to avoid duplicate logging
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler with formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger


logger = configure_logger()

# Helper function to format log messages consistently
def format_log_message(session_id: str | None, message: str) -> str:
    """Format log message with consistent session ID prefix if provided."""
    if session_id:
        return f"[{session_id[:8]}]{message}"
    return message


def configure_oltp_tracing(
    service_name: str = "Co_Pilot",
    endpoint: str = "http://localhost:4317",
    insecure: bool = True,
) -> trace.TracerProvider:
    resource = Resource(attributes={SERVICE_NAME: service_name})
    # Configure Tracing
    tracer_provider = TracerProvider(resource=Resource({"service.name": service_name}))
    processor = BatchSpanProcessor(OTLPSpanExporter())
    tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(tracer_provider)

    # Configure Metrics
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=endpoint, insecure=insecure)
    )
    meterProvider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meterProvider)

    # Configure Logging
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    exporter = OTLPLogExporter(insecure=insecure)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

    # Attach OTLP handler to root logger
    logging.getLogger().addHandler(handler)

    return tracer_provider
