import re
import logging

from core.exceptions import UnknownReportTypeError
from enums.report_type import ReportType


logger = logging.getLogger(__name__)

REPORT_B_PATTERNS = [
    r'הנשר',
    r'הפסקה',
    r'\b125\b',
    r'\b150\b',
    r'125%',
    r'150%',
    r'%\s*150',
    r'%\s*125',
]

REPORT_A_PATTERNS = [
    r'מחיר\s*לשעה',
    r'לתשלום',
]


def _match_any(patterns, text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def detect_report_type(raw_text: str) -> ReportType:
    """Detect report type from raw text with error handling."""
    if not raw_text or not isinstance(raw_text, str):
        logger.warning("Empty or invalid raw_text provided, defaulting to ReportType.A")
        return ReportType.A
    
    try:
        is_b = _match_any(REPORT_B_PATTERNS, raw_text)
        is_a = _match_any(REPORT_A_PATTERNS, raw_text)

        if is_b and not is_a:
            return ReportType.B
        elif is_a:
            return ReportType.A

        if '150' in raw_text or '125' in raw_text:
            return ReportType.B

        return ReportType.A
    except Exception as e:
        logger.error(f"Error detecting report type: {e}")
        raise UnknownReportTypeError(f"Failed to detect report type: {e}") from e