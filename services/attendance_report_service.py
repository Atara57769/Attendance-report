import logging

from core.exceptions import (
    OCRProcessingError,
    ParsingError,
    TransformationError,
    UnknownReportTypeError,
    PDFGenerationError,
)
from detectors.report_detector import detect_report_type
from factory.processor_factory import ProcessorFactory
from services.ocr_service import pdf_to_text


logger = logging.getLogger(__name__)


class AttendanceReportService:

    def __init__(self, factory: ProcessorFactory = None, ocr_service=None):
        self._factory = factory or ProcessorFactory()
        self._ocr_service = ocr_service or pdf_to_text

    def process(self, input_pdf_path: str):
        """Process an attendance report PDF with proper error handling."""
        try:
            # Step 1: OCR - convert PDF to text
            raw_text = self._ocr_service(input_pdf_path)
        except FileNotFoundError as e:
            raise OCRProcessingError(f"PDF file not found: {input_pdf_path}") from e
        except Exception as e:
            raise OCRProcessingError(f"Failed to process PDF: {e}") from e

        try:
            # Step 2: Detect report type
            report_type = detect_report_type(raw_text)
        except Exception as e:
            raise UnknownReportTypeError(f"Failed to detect report type: {e}") from e

        try:
            # Step 3: Get appropriate processor
            processor = self._factory.get(report_type)
        except Exception as e:
            raise UnknownReportTypeError(f"Failed to get processor for type {report_type}: {e}") from e

        try:
            # Step 4: Parse raw text into model
            model = processor.parse(raw_text)
        except ParsingError:
            raise
        except Exception as e:
            raise ParsingError(f"Failed to parse report: {e}") from e

        try:
            # Step 5: Apply time variation/transformation
            model = processor.apply_variation(model)
        except TransformationError:
            raise
        except Exception as e:
            raise TransformationError(f"Failed to apply variation: {e}") from e

        try:
            # Step 6: Generate PDF output
            processor.generate_pdf(model)
        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {e}") from e

        return model