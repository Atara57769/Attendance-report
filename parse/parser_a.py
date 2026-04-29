import logging

from core.models.attendance_report_models import (
    AttendanceReport,
    AttendanceRow,
)

from parse.base_parser import BaseParsingService

logger = logging.getLogger(__name__)


class ParserA(BaseParsingService):

    def parse_row(self, line: str) -> AttendanceRow | None:

        try:
            if not line or len(line.strip()) < 5 or "Page" in line:
                return None

            line = self.normalize_line(line)

            day = self.extract_day(line)

            if not day:
                return None

            date = self.extract_date(line)
            times = self.extract_times(line)
            nums = self.extract_numbers(line)

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
                note=self.clean_text(line) or None
            )

        except Exception as e:
            logger.warning(f"Failed to parse row: {e}")
            return None

    def build_report(
        self,
        rows: list[AttendanceRow],
        raw_text: str,
        lines: list[str],
    ) -> AttendanceReport:

        return AttendanceReport(
            rows=rows,
            total_hours=self.extract_total_hours(raw_text),
            total_days=self.extract_total_days(raw_text),
            hour_payment=self.extract_hour_payment(raw_text),
            total_payment=self.extract_total_payment(raw_text),
        )
