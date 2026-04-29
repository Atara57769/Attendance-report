from datetime import datetime, time, timedelta
import random
from typing import List, Optional

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from variation.base_variation import BaseVariationService


class VariationB(BaseVariationService):

    def _build_row(self, row: AttendanceRow, e: time, x: time, rng: random.Random) -> AttendanceRow:

        new_break = self._shift_break(row.break_time, rng)
        new_sum = self._calculate_with_break(e, x, new_break)

        return AttendanceRow(
            **{**row.__dict__,
               "entry_time": e,
               "end_time": x,
               "break_time": new_break,
               "sum": new_sum}
        )

    def _shift_break(self, break_time: Optional[time], rng: random.Random) -> Optional[time]:
        if not break_time:
            return break_time

        dt = datetime.combine(datetime.today(), break_time)
        dt += timedelta(minutes=rng.randint(0, 15))
        return dt.time()

    def _calculate_with_break(self, entry: time, exit: time, break_time: Optional[time]) -> float:
        e = datetime.combine(datetime.today(), entry)
        x = datetime.combine(datetime.today(), exit)

        if x <= e:
            return 0.0

        total = (x - e).total_seconds() / 3600

        if break_time:
            b = datetime.combine(datetime.today(), break_time)
            break_minutes = b.hour * 60 + b.minute

            max_minutes = (x - e).total_seconds() / 60
            if break_minutes < max_minutes:
                total -= break_minutes / 60

        return round(max(0, total), 2)

    def _recalculate_totals(self, original: AttendanceReport, rows: List[AttendanceRow]) -> dict:
        total_hours = round(sum(r.sum for r in rows if r.sum), 2)

        return {
            "total_hours": total_hours,
            "total_days": len(rows),
            "total_100": original.total_100,
            "total_125": original.total_125,
            "total_150": original.total_150,
            "total_saturday": original.total_saturday,
        }