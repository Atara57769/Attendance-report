from datetime import datetime, time, timedelta
import random
from typing import Optional

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from variation.base_variation import BaseVariationService


class VariationB(BaseVariationService):

    def _build_row(self, row: AttendanceRow, e: time, x: time, rng: random.Random, max_variation_minutes: int = 20) -> AttendanceRow:
        new_break = self._shift_break(row.break_time, rng, max_variation_minutes)
        new_sum = self._calculate_hours(e, x, new_break)

        return AttendanceRow(
            **{**row.__dict__,
               "entry_time": e,
               "end_time": x,
               "break_time": new_break,
               "sum": new_sum}
        )

    def _shift_break(self, break_time: Optional[time], rng: random.Random, max_variation_minutes: int = 20) -> Optional[time]:
        if not break_time:
            return break_time

        dt = datetime.combine(datetime.today(), break_time)
        dt += timedelta(minutes=rng.randint(-max_variation_minutes, max_variation_minutes))
        return dt.time()

    def _recalculate_totals(
        self,
        original: AttendanceReport,
        rows: list[AttendanceRow],
    ) -> dict[str, float | int | None]:
        total_hours = self._calculate_total_hours(rows)

        return {
            "total_hours": total_hours,
            "total_days": len(rows),
            "total_100": original.total_100,
            "total_125": original.total_125,
            "total_150": original.total_150,
            "total_saturday": original.total_saturday,
        }
