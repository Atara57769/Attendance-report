import logging

from core.exceptions import ParsingError, PDFGenerationError
from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from processors.base_processor import BaseProcessor


logger = logging.getLogger(__name__)


class ProcessorA(BaseProcessor):

    def _parse_row(self, line: str):
        """Parse a single line with error handling."""
        try:
            if not line or len(line.strip()) < 5 or "Page" in line:
                return None

            line = self.svc.normalize_line(line)

            day = self.svc.extract_day(line)
            if not day:
                return None

            date = self.svc.extract_date(line)
            times = self.svc.extract_times(line)
            nums = self.svc.extract_numbers(line)

            if not times or not nums:
                return None

            entry = times[0]
            end = times[1] if len(times) > 1 else entry

            hours = [n for n in nums if 0 < n <= 12]
            if not hours:
                return None

            return AttendanceRow(
                date=date,
                day=day,
                entry_time=entry,
                end_time=end,
                sum=min(hours),
                note=self.svc.clean_text(line) or None
            )
        except Exception as e:
            logger.warning(f"Failed to parse row: {e}")
            return None

    def _build_report(self, rows, raw_text, lines):
        """Build the attendance report with error handling."""
        try:
            return AttendanceReport(
                rows=rows,
                total_hours=self.svc.extract_total_hours(raw_text),
                total_days=self.svc.extract_total_days(raw_text),
                hour_payment=self.svc.extract_hour_payment(raw_text),
                total_payment=self.svc.extract_total_payment(raw_text),
            )
        except Exception as e:
            raise ParsingError(f"Failed to build report: {e}") from e

    def _build_variated_row(self, row, e, x, h):
        """Build a variated row with error handling."""
        try:
            return AttendanceRow(**{**row.__dict__, "entry_time": e, "end_time": x, "sum": h})
        except Exception as e:
            logger.warning(f"Failed to build variated row: {e}")
            return row

    def _finalize_variation(self, model, new_rows):
        """Finalize the variation with error handling."""
        try:
            return AttendanceReport(
                rows=new_rows,
                total_hours=self.time_variation.calculate_total_hours(new_rows),
                total_days=self.time_variation.calculate_total_days(new_rows),
                hour_payment=model.hour_payment,
                total_payment=model.total_payment,
            )
        except Exception as e:
            raise ParsingError(f"Failed to finalize variation: {e}") from e

    def generate_pdf(self, model):
        """Generate PDF with error handling."""
        try:
            return self.pdf_gen.create_report_a_pdf(model)
        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {e}") from e