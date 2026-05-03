import logging
from collections.abc import Callable

from core.models.attendance_report_models import AttendanceReport
from core.exceptions import (
    OCRProcessingError,
    ParsingError,
    TransformationError,
    UnknownReportTypeError,
    PDFGenerationError,
)
from detectors.report_detector import detect_report_type
from factory.processor_factory import ProcessorFactory
from core.observer import Subject

logger = logging.getLogger(__name__)

class AttendanceReportService(Subject):

    def __init__(
        self,
        factory: ProcessorFactory,
        ocr_service: Callable[[str], str],
    ) -> None:
        super().__init__()
        self._factory = factory
        self._ocr_service = ocr_service

    def process(self, input_pdf_path: str) -> AttendanceReport:
        """Process an attendance report PDF with proper error handling."""
        self.notify("process_started", input_pdf=input_pdf_path)
        
        # ---------- OCR ----------
        try:
            self.notify("ocr_started")
            raw_text = self._ocr_service(input_pdf_path)
            self.notify("ocr_finished")
        except FileNotFoundError as e:
            self.notify("ocr_failed", error=str(e))
            raise OCRProcessingError(f"PDF file not found: {input_pdf_path}") from e
        except Exception as e:
            self.notify("ocr_failed", error=str(e))
            raise OCRProcessingError(f"Failed to process PDF: {e}") from e

        # ---------- DETECT TYPE ----------
        try:
            self.notify("detect_type_started")
            report_type = detect_report_type(raw_text)
            self.notify("detect_type_finished", report_type=report_type)
        except Exception as e:
            self.notify("detect_type_failed", error=str(e))
            raise UnknownReportTypeError(f"Failed to detect report type: {e}") from e

        # ---------- FACTORY ----------
        try:
            self.notify("factory_started")
            processor = self._factory.get(report_type)
            self.notify("factory_finished")
        except Exception as e:
            self.notify("factory_failed", error=str(e))
            raise UnknownReportTypeError(
                f"Failed to get processor for type {report_type}: {e}"
            ) from e

        # ---------- PARSE ----------
        try:
            self.notify("parse_started")
            model = processor.parse(raw_text)
            self.notify("parse_finished")
        except ParsingError:
            self.notify("parse_failed")
            raise
        except Exception as e:
            self.notify("parse_failed", error=str(e))
            raise ParsingError(f"Failed to parse report: {e}") from e

        # ---------- VARIATION ----------
        try:
            self.notify("variation_started")
            model = processor.apply_variation(model)
            self.notify("variation_finished")
        except TransformationError as e:
            self.notify("variation_warning", error=str(e))
            logger.warning(f"Variation validation failed, falling back to original: {e}")
        except Exception as e:
            self.notify("variation_failed", error=str(e))
            raise TransformationError(f"Failed to apply variation: {e}") from e

        # ---------- PDF ----------
        try:
            self.notify("pdf_generation_started")
            pdf_path = processor.generate_pdf(model)
            self.notify("pdf_generation_finished", pdf_path=pdf_path)
        except PDFGenerationError:
            self.notify("pdf_generation_failed")
            raise
        except Exception as e:
            self.notify("pdf_generation_failed", error=str(e))
            raise PDFGenerationError(f"Failed to generate PDF: {e}") from e

        logger.info(f"Report processed successfully -> {pdf_path}")
        self.notify("process_finished", pdf_path=pdf_path)

        return model