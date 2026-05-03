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

logger = logging.getLogger(__name__)

class AttendanceReportService:

    def __init__(
        self,
        factory: ProcessorFactory,
        ocr_service: Callable[[str], str],
    ) -> None:
        self._factory = factory
        self._ocr_service = ocr_service

    def process(self, input_pdf_path: str) -> AttendanceReport:
        """Process an attendance report PDF with proper error handling."""
        
        # ---------- OCR ----------
        try:
            raw_text = self._ocr_service(input_pdf_path)
        except FileNotFoundError as e:
            raise OCRProcessingError(f"PDF file not found: {input_pdf_path}") from e
        except Exception as e:
            raise OCRProcessingError(f"Failed to process PDF: {e}") from e

        # ---------- DETECT TYPE ----------
        try:
            report_type = detect_report_type(raw_text)
        except Exception as e:
            raise UnknownReportTypeError(f"Failed to detect report type: {e}") from e

        # ---------- FACTORY ----------
        try:
            processor = self._factory.get(report_type)
        except Exception as e:
            raise UnknownReportTypeError(
                f"Failed to get processor for type {report_type}: {e}"
            ) from e

        # ---------- PARSE ----------
        try:
            model = processor.parse(raw_text)
        except ParsingError:
            raise
        except Exception as e:
            raise ParsingError(f"Failed to parse report: {e}") from e

        # ---------- VARIATION ----------
        try:
            model = processor.apply_variation(model)
        except TransformationError as e:
            logger.warning(f"Variation validation failed, falling back to original: {e}")
        except Exception as e:
            raise TransformationError(f"Failed to apply variation: {e}") from e

        # ---------- PDF ----------
        try:
            pdf_path = processor.generate_pdf(model)
        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {e}") from e

        logger.info(f"Report processed successfully -> {pdf_path}")

        return model