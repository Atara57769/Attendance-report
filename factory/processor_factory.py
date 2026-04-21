
import re

from processores.processor_a import ProcessorA
from processores.processor_b import ProcessorB


def get_processor(raw_text: str):
    """
    Determine the correct processor based on robust OCR-friendly keywords.
    """
    # Check for Report B indicators: The word "הפסקה" (Break), the company name "הנשר",
    # or the presence of the exact numbers 125 / 150 (with or without %).
    is_report_b = bool(re.search(r'הנשר|הפסקה|\b125\b|\b150\b|125%|150%|\%\s*150|\%\s*125', raw_text))

    # Check for Report A indicators: The words "מחיר לשעה" or "לתשלום"
    is_report_a = bool(re.search(r'מחיר\s*לשעה|לתשלום', raw_text))

    # Prioritize based on the strongest matches
    if is_report_b and not is_report_a:
        return ProcessorB()
    elif is_report_a:
        return ProcessorA()

    # Fallback: if we just see 150 or 125 floating around, it's likely B
    if '150' in raw_text or '125' in raw_text:
        return ProcessorB()

    # Default to A if we can't be sure
    return ProcessorA()