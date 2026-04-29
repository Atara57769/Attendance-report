from core.exceptions import UnknownReportTypeError, ConfigurationError
from enums.report_type import ReportType

from parse.parser_a import ParserA
from parse.parser_b import ParserB
from pdf_rander.rander_a import PDFServiceA
from pdf_rander.rander_b import PDFServiceB
from processors.report_processor import ReportProcessor
from variation.variation_a import VariationA
from variation.variation_b import VariationB


class ProcessorFactory:

    def __init__(self):
        self._map = {
            ReportType.A: self._create_a,
            ReportType.B: self._create_b,
        }

    def _create_a(self):
        return ReportProcessor(
            parser=ParserA(),
            variation_service=VariationA(),
            pdf_service=PDFServiceA()
        )

    def _create_b(self):
        return ReportProcessor(
            parser=ParserB(),
            variation_service=VariationB(),
            pdf_service=PDFServiceB()
        )

    def get(self, report_type: ReportType) -> ReportProcessor:
        if report_type is None:
            raise UnknownReportTypeError("Report type cannot be None")

        factory = self._map.get(report_type)

        if not factory:
            raise UnknownReportTypeError(f"No processor for type {report_type}")

        try:
            return factory()
        except Exception as e:
            raise ConfigurationError(f"Failed to build processor: {e}") from e