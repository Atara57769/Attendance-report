
import logging
from factory.processor_factory import get_processor
from services.ocr_service import pdf_to_text

logger = logging.getLogger(__name__)

def process_attendance_report(input_pdf_path: str, output_pdf_path: str):
    logger.info(f"Processing attendance report: {input_pdf_path}")
    raw_text = pdf_to_text(input_pdf_path)
    logger.debug(f"Extracted text length: {len(raw_text)}")

    processor = get_processor(raw_text)
    logger.info(f"Selected processor: {processor.__class__.__name__}")
    
    model = processor.parse(raw_text)
    logger.info("Parsed report data")

    model = processor.apply_variation(model)
    logger.info("Applied time variations")

    processor.generate_pdf(model, output_pdf_path)
    logger.info(f"Generated PDF: {output_pdf_path}")

    return model