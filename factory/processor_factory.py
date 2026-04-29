from core.exceptions import UnknownReportTypeError, ConfigurationError
from enums.report_type import ReportType
import logging
from collections.abc import Callable

from parse.parser_a import ParserA
from parse.parser_b import ParserB
from pdf_render.render_a import PDFServiceA
from pdf_render.render_b import PDFServiceB
from processors.report_processor import ReportProcessor
from variation.variation_a import VariationA
from variation.variation_b import VariationB
from variation.validating_strategy_decorator import ValidatingStrategyDecorator

logger = logging.getLogger(__name__)


class ProcessorFactory:

    def __init__(self) -> None:
        self._map: dict[ReportType, Callable[[], ReportProcessor]] = {
            ReportType.A: self._create_a,
            ReportType.B: self._create_b,
        }

    def _create_a(self) -> ReportProcessor:
        try:
            return ReportProcessor(
                parser=ParserA(),
                variation_service=ValidatingStrategyDecorator(VariationA()),
                pdf_service=PDFServiceA()
            )
        except Exception as e:
            logger.error(f"Failed to create ProcessorA: {e}")
            raise ConfigurationError(f"Failed to create ProcessorA: {e}") from e

    def _create_b(self) -> ReportProcessor:
        try:
            return ReportProcessor(
                parser=ParserB(),
                variation_service=ValidatingStrategyDecorator(VariationB()),
                pdf_service=PDFServiceB()
            )
        except Exception as e:
            logger.error(f"Failed to create ProcessorB: {e}")
            raise ConfigurationError(f"Failed to create ProcessorB: {e}") from e

    def get(self, report_type: ReportType) -> ReportProcessor:
        try:
            if report_type is None:
                raise UnknownReportTypeError("Report type cannot be None")

            factory = self._map.get(report_type)

            if not factory:
                raise UnknownReportTypeError(f"No processor for type {report_type}")

            return factory()
        except UnknownReportTypeError:
            raise
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Failed to get processor for type {report_type}: {e}")
            raise ConfigurationError(f"Failed to build processor: {e}") from e
