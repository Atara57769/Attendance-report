
from factory.processor_factory import get_processor
from services.ocr_service import pdf_to_text


def process_attendance_report(input_pdf_path: str, output_pdf_path: str):
    raw_text = pdf_to_text(input_pdf_path)

    processor = get_processor(raw_text)
    
    model = processor.parse(raw_text)

    processor.apply_variation(model)

    processor.generate_pdf(model, output_pdf_path)

    return model