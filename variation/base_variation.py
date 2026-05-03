from abc import ABC, abstractmethod
from datetime import datetime, timedelta, time
from typing import Optional
import random
import logging

from core.models.attendance_report_models import AttendanceReport, AttendanceRow
from core.exceptions import TransformationError

logger = logging.getLogger(__name__)


class BaseVariationService(ABC):

    # ---------- PUBLIC ----------
    def apply(self, report: AttendanceReport, seed: Optional[int] = None, max_variation_minutes: int = 20) -> AttendanceReport:
        # Determine seed: use provided seed, or extract from report date, or default to 42
        if seed is None:
            seed = self._get_seed_from_report(report)
        
        # Create deterministic random instance
        rng = random.Random(seed)
        
        try:
            new_rows = [self._process_row(r, rng, max_variation_minutes) for r in report.rows]

            return AttendanceReport(
                rows=new_rows,
                **self._recalculate_totals(report, new_rows)
            )
        except TransformationError:
            raise
        except Exception as e:
            logger.error(f"Failed to apply variation: {e}")
            raise TransformationError(f"Failed to apply variation: {e}") from e

    def _get_seed_from_report(self, report: AttendanceReport) -> int:
        """Extract seed from report date, or return default 42."""
        if report.rows and report.rows[0].date:
            # Use the date's year, month, and day as the seed
            d = report.rows[0].date
            return d.year * 10000 + d.month * 100 + d.day
        return 42

    # ---------- ROW PROCESS ----------
    def _process_row(self, row: AttendanceRow, rng: random.Random, max_variation_minutes: int = 20) -> AttendanceRow:
        try:
            if not row.entry_time or not row.end_time:
                return row

            e, x = self._shift_times(row.entry_time, row.end_time, rng, max_variation_minutes)

            return self._build_row(row, e, x, rng, max_variation_minutes)
        except Exception as e:
            logger.warning(f"Failed to process row, returning original: {e}")
            return row

    def _shift_times(self, entry: time, exit: time, rng: random.Random, max_variation_minutes: int = 20) -> tuple[time, time]:
        try:
            e = datetime.combine(datetime.today(), entry)
            x = datetime.combine(datetime.today(), exit)

            e += timedelta(minutes=rng.randint(-max_variation_minutes, max_variation_minutes))
            x += timedelta(minutes=rng.randint(-max_variation_minutes, max_variation_minutes))

            return e.time(), x.time()
        except Exception as e:
            logger.error(f"Failed to shift times: {e}")
            raise TransformationError(f"Failed to shift times: {e}") from e

    def _calculate_hours(self, entry: time, exit: time, break_time: Optional[time] = None) -> float:
        try:
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
        except Exception as e:
            logger.error(f"Failed to calculate hours: {e}")
            return 0.0

    def _calculate_total_hours(self, rows: list[AttendanceRow]) -> float:
        return round(sum(r.sum for r in rows if r.sum), 2)

    # ---------- ABSTRACT ----------
    @abstractmethod
    def _build_row(self, row: AttendanceRow, e: time, x: time, rng: random.Random, max_variation_minutes: int = 20) -> AttendanceRow:
        pass

    @abstractmethod
    def _recalculate_totals(
        self,
        original: AttendanceReport,
        rows: list[AttendanceRow],
    ) -> dict[str, float | int | None]:
        raise NotImplementedError
