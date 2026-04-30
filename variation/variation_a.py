from datetime import time
import random

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from variation.base_variation import BaseVariationService


class VariationA(BaseVariationService):

    def _build_row(self, row: AttendanceRow, e: time, x: time, rng: random.Random, max_variation_minutes: int = 20) -> AttendanceRow:
        new_sum = self._calculate_hours(e, x)

        return AttendanceRow(
            **{**row.__dict__,
               "entry_time": e,
               "end_time": x,
               "sum": new_sum}
        )

    def _recalculate_totals(
        self,
        original: AttendanceReport,
        rows: list[AttendanceRow],
    ) -> dict[str, float | int | None]:
        total_hours = self._calculate_total_hours(rows)

        return {
            "total_hours": total_hours,
            "total_days": len(rows),
            "hour_payment": original.hour_payment,
            "total_payment": original.total_payment,
        }
