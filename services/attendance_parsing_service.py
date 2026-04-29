import logging
import re
from typing import Optional, List

from core.exceptions import ParsingError


logger = logging.getLogger(__name__)


class AttendanceParsingService:

    @staticmethod
    def normalize_line(line: str) -> str:
        """Normalize a line by replacing separators and normalizing whitespace."""
        try:
            line = line.replace("|", " ")
            return re.sub(r"\s+", " ", line).strip()
        except Exception as e:
            logger.warning(f"Failed to normalize line: {e}")
            return line

    @staticmethod
    def extract_times(line: str) -> List[str]:
        """Extract time values from a line with error handling."""
        try:
            raw_times = re.findall(r'\d{1,4}[:.]?\d{0,2}', line)
            times = []

            for t in raw_times:
                if ":" in t or "." in t:
                    t = t.replace(".", ":")
                    parts = t.split(":")
                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        h, m = int(parts[0]), int(parts[1])
                        if h < 24 and m < 60:
                            times.append(f"{h:02d}:{m:02d}")

                elif t.isdigit():
                    val = int(t)
                    if 100 <= val <= 2359:
                        h, m = val // 100, val % 100
                        if h < 24 and m < 60:
                            times.append(f"{h:02d}:{m:02d}")

            return times
        except Exception as e:
            logger.warning(f"Failed to extract times from line: {e}")
            return []

    @staticmethod
    def extract_numbers(line: str) -> List[float]:
        """Extract numeric values from a line with error handling."""
        try:
            nums = re.findall(r'\d+(?:\.\d+)?', line)

            def fix(val_str):
                val = float(val_str)
                if val >= 100 and "." not in val_str:
                    return val / 100.0
                return val

            return [fix(n) for n in nums]
        except Exception as e:
            logger.warning(f"Failed to extract numbers from line: {e}")
            return []

    @staticmethod
    def extract_day(line: str) -> Optional[str]:
        """Extract day of week from a line."""
        try:
            match = re.search(r'(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)', line)
            return match.group(1) if match else None
        except Exception as e:
            logger.warning(f"Failed to extract day from line: {e}")
            return None

    @staticmethod
    def extract_date(line: str) -> str:
        """Extract date from a line."""
        try:
            match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]?\d{0,4}', line)
            return match.group(0) if match else ""
        except Exception as e:
            logger.warning(f"Failed to extract date from line: {e}")
            return ""

    @staticmethod
    def clean_text(line: str) -> str:
        """Clean text by removing numbers and non-word characters."""
        try:
            line = re.sub(r'\d+(?:[/:.]\d+)?', '', line)
            return re.sub(r'[^\w\sא-ת]', '', line).strip()
        except Exception as e:
            logger.warning(f"Failed to clean text: {e}")
            return line

    @staticmethod
    def extract_total_hours(text: str) -> Optional[float]:
        """Extract total hours from text."""
        try:
            match = re.search(r'([\d,]+\.\d+).*?שעות|שעות.*?([\d,]+\.\d+)', text, re.DOTALL)
            if match:
                val = match.group(1) or match.group(2)
                return float(val.replace(',', ''))
            return None
        except Exception as e:
            logger.warning(f"Failed to extract total hours: {e}")
            return None

    @staticmethod
    def extract_total_days(text: str) -> Optional[int]:
        """Extract total days from text."""
        try:
            match = re.search(r'(\d+).*?ימים|ימים.*?(\d+)', text)
            return int(match.group(1) or match.group(2)) if match else None
        except Exception as e:
            logger.warning(f"Failed to extract total days: {e}")
            return None

    @staticmethod
    def extract_hour_payment(text: str) -> Optional[float]:
        """Extract hourly payment from text."""
        try:
            match = re.search(r'([\d,]+\.\d+).*?שעה|שעה.*?([\d,]+\.\d+)', text, re.DOTALL)
            if match:
                val = match.group(1) or match.group(2)
                return float(val.replace(',', ''))
            return None
        except Exception as e:
            logger.warning(f"Failed to extract hour payment: {e}")
            return None

    @staticmethod
    def extract_total_payment(text: str) -> Optional[float]:
        """Extract total payment from text."""
        try:
            match = re.search(r'([\d,]+\.\d+).*?תשלום|תשלום.*?([\d,]+\.\d+)', text, re.DOTALL)
            if match:
                val = match.group(1) or match.group(2)
                return float(val.replace(',', ''))
            return None
        except Exception as e:
            logger.warning(f"Failed to extract total payment: {e}")
            return None