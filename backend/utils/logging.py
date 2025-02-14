import logging
from typing import Optional

from opentelemetry import metrics, trace
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

class UnifiedLogger:
    """
    Unified logging class for FastAPI that combines standard Python logging with OpenTelemetry.
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UnifiedLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Initialize standard Python logger
        self.logger = logging.getLogger("co-pilot")
        self.logger.setLevel(logging.INFO)

        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)

        # Add console handler with formatting
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        self.logger.propagate = False

        self._initialized = True

    def configure_otlp(
        self,
        service_name: str = "co-pilot",
        endpoint: str = "http://localhost:4317",
        insecure: bool = True
    ) -> trace.TracerProvider:
        """Configure OpenTelemetry tracing, metrics and logging."""
        resource = Resource(attributes={SERVICE_NAME: service_name})
        
        # Configure Tracing
        tracer_provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter())
        tracer_provider.add_span_processor(processor)
        trace.set_tracer_provider(tracer_provider)

        # Configure Metrics
        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=endpoint, insecure=insecure)
        )
        meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(meter_provider)

        # Configure OTLP Logging
        logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(logger_provider)

        exporter = OTLPLogExporter(insecure=insecure)
        logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        
        # Use the same formatter for OTLP handler
        handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S'
        ))

        # Add OTLP handler to our logger
        self.logger.addHandler(handler)

        return tracer_provider

    def format_message(self, session_id: Optional[str], message: str) -> str:
        """Format log message with session ID if provided."""
        if session_id:
            return f"[{session_id[:5]}...{session_id[-5:]}] {message}"
        return message

    def debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning message."""
        self.logger.warning(message)

    def error(self, message: str, exc_info: bool = False) -> None:
        """Log error message."""
        self.logger.error(message, exc_info=exc_info)

    def critical(self, message: str) -> None:
        """Log critical message."""
        self.logger.critical(message)

# Create singleton instance
logger = UnifiedLogger() 