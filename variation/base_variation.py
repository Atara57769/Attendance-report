from abc import ABC, abstractmethod
from datetime import datetime, timedelta, time
from typing import Optional, List
import random
import logging

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from core.exceptions import TransformationError

logger = logging.getLogger(__name__)


class BaseVariationService(ABC):

    # ---------- PUBLIC ----------
    def apply(self, report: AttendanceReport) -> AttendanceReport:
        try:
            new_rows = [self._process_row(r) for r in report.rows]

            return AttendanceReport(
                rows=new_rows,
                **self._recalculate_totals(report, new_rows)
            )
        except TransformationError:
            raise
        except Exception as e:
            logger.error(f"Failed to apply variation: {e}")
            raise TransformationError(f"Failed to apply variation: {e}") from e

    # ---------- ROW PROCESS ----------
    def _process_row(self, row: AttendanceRow) -> AttendanceRow:
        try:
            if not row.entry_time or not row.end_time:
                return row

            e, x = self._shift_times(row.entry_time, row.end_time)

            if x <= e:
                x = (datetime.combine(datetime.today(), e) + timedelta(minutes=1)).time()

            return self._build_row(row, e, x)
        except Exception as e:
            logger.warning(f"Failed to process row, returning original: {e}")
            return row

    def _shift_times(self, entry: time, exit: time):
        try:
            e = datetime.combine(datetime.today(), entry)
            x = datetime.combine(datetime.today(), exit)

            e += timedelta(minutes=random.randint(0, 20))
            x += timedelta(minutes=random.randint(0, 20))

            return e.time(), x.time()
        except Exception as e:
            logger.error(f"Failed to shift times: {e}")
            raise TransformationError(f"Failed to shift times: {e}") from e

    def _calculate_hours(self, entry: time, exit: time) -> float:
        try:
            e = datetime.combine(datetime.today(), entry)
            x = datetime.combine(datetime.today(), exit)
            return round((x - e).total_seconds() / 3600, 2)
        except Exception as e:
            logger.error(f"Failed to calculate hours: {e}")
            return 0.0

    # ---------- ABSTRACT ----------
    @abstractmethod
    def _build_row(self, row: AttendanceRow, e: time, x: time) -> AttendanceRow:
        pass

    @abstractmethod
    def _recalculate_totals(self, original: AttendanceReport, rows: List[AttendanceRow]) -> dict:
        pass