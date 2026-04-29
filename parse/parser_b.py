import logging
import re
from datetime import time

from core.models.attendance_report_models import (
    AttendanceReport,
    AttendanceRow,
)

from parse.base_parser import BaseParsingService

logger = logging.getLogger(__name__)


class ParserB(BaseParsingService):

    def parse_row(self, line: str):

        try:
            if not line or len(line.strip()) < 10 or "Page" in line:
                return None

            line = self.normalize_line(line)

            day = self.extract_day(line)

            if not day:
                return None

            times = re.findall(r"\d{1,2}[:.]\d{2}", line)

            if len(times) < 2:
                return None

            times = [
                time(
                    hour=int(t.replace(".", ":").split(":")[0]),
                    minute=int(t.replace(".", ":").split(":")[1])
                )
                for t in times
            ]

            nums = [n for n in self.extract_numbers(line) if 0 <= n <= 24]

            if not nums:
                return None

            return AttendanceRow(
                date=self.extract_date(line),
                day=day,
                entry_time=times[0],
                end_time=times[1],
                break_time=times[2] if len(times) > 2 else time(0, 0),
                sum=nums[0],
                col_100=nums[1] if len(nums) > 1 else 0.0,
                col_125=nums[2] if len(nums) > 2 else 0.0,
                col_150=nums[3] if len(nums) > 3 else 0.0,
                col_saturday=nums[4] if len(nums) > 4 else 0.0,
                location=self.clean_text(line)
            )

        except Exception as e:
            logger.warning(f"Failed to parse row: {e}")
            return None

    def build_report(self, rows, raw_text, lines):

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