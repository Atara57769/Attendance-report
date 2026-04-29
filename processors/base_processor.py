from abc import ABC, abstractmethod
from typing import List

from core.exceptions import ParsingError, TransformationError
from core.models.attendance_report_models import AttendanceReport, AttendanceRow


class BaseProcessor(ABC):

    def __init__(self, parsing_service, time_variation_service, pdf_generator):
        self.svc = parsing_service
        self.time_variation = time_variation_service
        self.pdf_gen = pdf_generator

    def parse(self, raw_text: str) -> AttendanceReport:
        """Parse raw text into AttendanceReport with error handling."""
        try:
            lines = raw_text.strip().split("\n")
            rows = [r for r in (self._parse_row(l) for l in lines) if r]
            return self._build_report(rows, raw_text, lines)
        except ParsingError:
            raise
        except Exception as e:
            raise ParsingError(f"Failed to parse report: {e}") from e

    def apply_variation(self, model: AttendanceReport) -> AttendanceReport:
        """Apply time variation to all rows with error handling."""
        try:
            new_rows = [self._process_row_variation(r) for r in model.rows]
            return self._finalize_variation(model, new_rows)
        except TransformationError:
            raise
        except Exception as e:
            raise TransformationError(f"Failed to apply variation: {e}") from e

    def _process_row_variation(self, row: AttendanceRow) -> AttendanceRow:
        """Process a single row's time variation with error handling."""
        try:
            if not row.entry_time or not row.end_time:
                return row

            e, x, h = self.time_variation.apply_variation(row.entry_time, row.end_time)

            if not e or not x:
                return row

            return self._build_variated_row(row, e, x, h)
        except TransformationError:
            raise
        except Exception as e:
            # Log and return original row on transformation failure
            return row

    @abstractmethod
    def _parse_row(self, line: str) -> AttendanceRow | None:
        pass

    @abstractmethod
    def _build_report(self, rows, raw_text, lines) -> AttendanceReport:
        pass

    @abstractmethod
    def _build_variated_row(self, row, e, x, h) -> AttendanceRow:
        pass

    @abstractmethod
    def _finalize_variation(self, model, new_rows) -> AttendanceReport:
        pass

    @abstractmethod
    def generate_pdf(self, model: AttendanceReport) -> str:
        pass