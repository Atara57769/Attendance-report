from abc import ABC, abstractmethod
from datetime import datetime, timedelta, time
from typing import Optional, List
import random

from core.models.attendance_report_models import AttendanceReport, AttendanceRow


class BaseVariationService(ABC):

    # ---------- PUBLIC ----------
    def apply(self, report: AttendanceReport) -> AttendanceReport:
        new_rows = [self._process_row(r) for r in report.rows]

        return AttendanceReport(
            rows=new_rows,
            **self._recalculate_totals(report, new_rows)
        )

    # ---------- ROW PROCESS ----------
    def _process_row(self, row: AttendanceRow) -> AttendanceRow:
        if not row.entry_time or not row.end_time:
            return row

        e, x = self._shift_times(row.entry_time, row.end_time)

        if x <= e:
            x = (datetime.combine(datetime.today(), e) + timedelta(minutes=1)).time()

        return self._build_row(row, e, x)

    def _shift_times(self, entry: time, exit: time):
        e = datetime.combine(datetime.today(), entry)
        x = datetime.combine(datetime.today(), exit)

        e += timedelta(minutes=random.randint(0, 20))
        x += timedelta(minutes=random.randint(0, 20))

        return e.time(), x.time()

    def _calculate_hours(self, entry: time, exit: time) -> float:
        e = datetime.combine(datetime.today(), entry)
        x = datetime.combine(datetime.today(), exit)
        return round((x - e).total_seconds() / 3600, 2)

    # ---------- ABSTRACT ----------
    @abstractmethod
    def _build_row(self, row: AttendanceRow, e: time, x: time) -> AttendanceRow:
        pass

    @abstractmethod
    def _recalculate_totals(self, original: AttendanceReport, rows: List[AttendanceRow]) -> dict:
        pass