import logging

from detectors.report_detector import detect_report_type
from factory.processor_factory import ProcessorFactory
from services.ocr_service import pdf_to_text


logger = logging.getLogger(__name__)


class AttendanceReportService:

    def __init__(self, factory: ProcessorFactory = None, ocr_service=None):
        self._factory = factory or ProcessorFactory()
        self._ocr_service = ocr_service or pdf_to_text

    def process(self, input_pdf_path: str):
        raw_text = self._ocr_service(input_pdf_path)

        report_type = detect_report_type(raw_text)
        processor = self._factory.get(report_type)

        model = processor.parse(raw_text)
        model = processor.apply_variation(model)
        processor.generate_pdf(model)

        return model