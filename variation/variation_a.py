from datetime import time
import random
from typing import List

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from variation.base_variation import BaseVariationService


class VariationA(BaseVariationService):

    def _build_row(self, row: AttendanceRow, e: time, x: time, rng: random.Random) -> AttendanceRow:
        new_sum = self._calculate_hours(e, x)

        return AttendanceRow(
            **{**row.__dict__,
               "entry_time": e,
               "end_time": x,
               "sum": new_sum}
        )

    def _recalculate_totals(self, original: AttendanceReport, rows: List[AttendanceRow]) -> dict:
        total_hours = round(sum(r.sum for r in rows if r.sum), 2)

        return {
            "total_hours": total_hours,
            "total_days": len(rows),
            "hour_payment": original.hour_payment,
            "total_payment": original.total_payment,
        }