import logging
import re

from core.exceptions import ParsingError, PDFGenerationError
from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from processors.base_processor import BaseProcessor


logger = logging.getLogger(__name__)


class ProcessorB(BaseProcessor):

    def _parse_row(self, line: str):
        """Parse a single line with error handling."""
        try:
            if not line or len(line.strip()) < 10 or "Page" in line:
                return None

            line = self.svc.normalize_line(line)

            day = self.svc.extract_day(line)
            if not day:
                return None

            times = re.findall(r"\d{1,2}[:.]\d{2}", line)
            if len(times) < 2:
                return None

            times = [t.replace(".", ":") for t in times]

            nums = [n for n in self.svc.extract_numbers(line) if 0 <= n <= 24]

            if not nums:
                return None

            return AttendanceRow(
                date=self.svc.extract_date(line),
                day=day,
                entry_time=times[0],
                end_time=times[1],
                break_time=times[2] if len(times) > 2 else "00:00",
                sum=nums[0],
                col_100=nums[1] if len(nums) > 1 else 0.0,
                col_125=nums[2] if len(nums) > 2 else 0.0,
                col_150=nums[3] if len(nums) > 3 else 0.0,
                col_saturday=nums[4] if len(nums) > 4 else 0.0,
                location=self.svc.clean_text(line)
            )
        except Exception as e:
            logger.warning(f"Failed to parse row: {e}")
            return None

    def _build_report(self, rows, raw_text, lines):
        """Build the attendance report with error handling."""
        try:
            totals_pattern = r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)'

            total_saturday = total_150 = total_125 = total_100 = total_hours = None

            for line in reversed(lines):
                match = re.search(totals_pattern, line)
                if match:
                    total_saturday = float(match.group(1))
                    total_150 = float(match.group(2))
                    total_125 = float(match.group(3))
                    total_100 = float(match.group(4))
                    total_hours = float(match.group(5))
                    break

            return AttendanceReport(
                rows=rows,
                total_hours=total_hours,
                total_100=total_100,
                total_125=total_125,
                total_150=total_150,
                total_saturday=total_saturday,
            )
        except Exception as e:
            raise ParsingError(f"Failed to build report: {e}") from e

    def _build_variated_row(self, row, e, x, _):
        """Build a variated row with error handling."""
        try:
            new_break = self.time_variation.apply_break_variation(row.break_time)

            new_sum = self.time_variation.calculate_hours_with_break(e, x, new_break)

            return AttendanceRow(
                **{**row.__dict__,
                   "entry_time": e,
                   "end_time": x,
                   "break_time": new_break,
                   "sum": new_sum}
            )
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
                total_100=model.total_100,
                total_125=model.total_125,
                total_150=model.total_150,
                total_saturday=model.total_saturday,
            )
        except Exception as e:
            raise ParsingError(f"Failed to finalize variation: {e}") from e


    def generate_pdf(self, model):
        """Generate PDF with error handling."""
        try:
            return self.pdf_gen.create_report_b_pdf(model)
        except PDFGenerationError:
            raise
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {e}") from e