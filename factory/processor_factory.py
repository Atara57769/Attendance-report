from enums.report_type import ReportType
from processors.processor_a import ProcessorA
from processors.processor_b import ProcessorB
from services.attendance_parsing_service import AttendanceParsingService
from services.pdf_generator_service import PDFGenerator
from services.time_variation_service import TimeVariationService


class ProcessorFactory:
    def __init__(self):
        # singletons חיים כאן 👇
        self._parsing_service = AttendanceParsingService()
        self._pdf_generator = PDFGenerator()
        self._time_variation_service = TimeVariationService()

        # mapping
        self._processor_map = {
            ReportType.A: self._create_processor_a,
            ReportType.B: self._create_processor_b,
        }

    def _create_processor_a(self):
        return ProcessorA(
            self._parsing_service,
            self._time_variation_service,
            self._pdf_generator
        )

    def _create_processor_b(self):
        return ProcessorB(
            self._parsing_service,
            self._time_variation_service,
            self._pdf_generator
        )

    def get(self, report_type: ReportType):
        factory = self._processor_map.get(report_type)

        if not factory:
            raise ValueError(f"No processor for {report_type}")

        return factory()