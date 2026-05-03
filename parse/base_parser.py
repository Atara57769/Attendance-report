from abc import ABC, abstractmethod
from datetime import date, time
from datetime import datetime
from typing import Optional
import logging
import re

from core.models.attendance_report_models import AttendanceReport, AttendanceRow

logger = logging.getLogger(__name__)


class BaseParsingService(ABC):

    def parse(self, raw_text: str) -> AttendanceReport:
        """Parse raw text into AttendanceReport."""
        try:
            lines = raw_text.strip().split("\n")
            rows = [r for r in (self.parse_row(l) for l in lines) if r]

            return self.build_report(rows, raw_text, lines)

        except Exception as e:
            raise ValueError(f"Failed to parse report: {e}") from e

    @staticmethod
    def normalize_line(line: str) -> str:
        try:
            line = line.replace("|", " ")
            return re.sub(r"\s+", " ", line).strip()
        except Exception as e:
            logger.warning(f"Failed to normalize line: {e}")
            return line

    @staticmethod
    def extract_times(line: str) -> list[time]:
        """Extract time objects from line."""
        try:
            raw_times = re.findall(r'\d{1,4}[:.]?\d{0,2}', line)

            parsed_times = []

            for t in raw_times:

                if ":" in t or "." in t:
                    t = t.replace(".", ":")
                    parts = t.split(":")

                    if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                        h, m = int(parts[0]), int(parts[1])

                        if h < 24 and m < 60:
                            if h < 6:
                                h += 12
                            parsed_times.append(time(hour=h, minute=m))

                elif t.isdigit():
                    val = int(t)

                    if 100 <= val <= 2359:
                        h, m = val // 100, val % 100

                        if h < 24 and m < 60:
                            if h < 6:
                                h += 12
                            parsed_times.append(time(hour=h, minute=m))

            return parsed_times

        except Exception as e:
            logger.warning(f"Failed to extract times from line: {e}")
            return []

    @staticmethod
    def extract_numbers(line: str) -> list[float]:
        try:
            nums = re.findall(r'\d+(?:\.\d+)?', line)

            def fix(val_str: str) -> float:
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
        try:
            match = re.search(r'(ראשון|שני|שלישי|רביעי|חמישי|שישי|שבת)', line)
            return match.group(1) if match else None

        except Exception as e:
            logger.warning(f"Failed to extract day from line: {e}")
            return None

    @staticmethod
    def extract_date(line: str) -> Optional[date]:

        try:
            match = re.search(r'\d{1,2}[/-]\d{1,2}[/-]?\d{0,4}', line)

            if not match:
                return None

            raw = match.group(0)

            raw = raw.replace("-", "/")

            parts = raw.split("/")

            if len(parts) == 2:
                day, month = parts
                year = datetime.now().year

            else:
                day, month, year = parts

                if len(year) == 2:
                    year = f"20{year}"

            return date(
                year=int(year),
                month=int(month),
                day=int(day)
            )

        except Exception as e:
            logger.warning(f"Failed to extract date from line: {e}")
            return None

    @staticmethod
    def clean_text(line: str) -> str:
        try:
            line = re.sub(r'\d+(?:[/:.]\d+)?', '', line)
            return re.sub(r'[^\w\sא-ת]', '', line).strip()

        except Exception as e:
            logger.warning(f"Failed to clean text: {e}")
            return line

    @staticmethod
    def extract_total_hours(text: str) -> Optional[float]:
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
        try:
            match = re.search(r'(\d+).*?ימים|ימים.*?(\d+)', text)

            return int(match.group(1) or match.group(2)) if match else None

        except Exception as e:
            logger.warning(f"Failed to extract total days: {e}")
            return None

    @staticmethod
    def extract_hour_payment(text: str) -> Optional[float]:
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
        try:
            match = re.search(r'([\d,]+\.\d+).*?תשלום|תשלום.*?([\d,]+\.\d+)', text, re.DOTALL)

            if match:
                val = match.group(1) or match.group(2)
                return float(val.replace(',', ''))

            return None

        except Exception as e:
            logger.warning(f"Failed to extract total payment: {e}")
            return None

    @abstractmethod
    def parse_row(self, line: str) -> AttendanceRow | None:
        raise NotImplementedError

    @abstractmethod
    def build_report(
        self,
        rows: list[AttendanceRow],
        raw_text: str,
        lines: list[str],
    ) -> AttendanceReport:
        raise NotImplementedError
